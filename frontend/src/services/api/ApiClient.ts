import type { 
  ApiResponse, 
  NarrativeArc, 
  Character, 
  VectorStoreEntry, 
  ArcProgression, 
  ArcCluster,
  CreateArcData 
} from '@/architecture/types';

// Add interface for arc creation data
interface ArcCreateData extends Omit<Partial<NarrativeArc>, 'progressions' | 'main_characters'> {
  initial_progression?: {
    content: string;
    season: string;
    episode: string;
    interfering_characters: string;
  };
  main_characters: string;
}

interface GenerateProgressionResponse {
  content: string;
  interfering_characters: string[];
}

interface ApiProgressionResponse {
  data: GenerateProgressionResponse | null;
  error?: string;
}

// Update the createProgression interface to match API expectations
interface CreateProgressionData {
  arc_id: string;
  content: string;
  series: string;
  season: string;
  episode: string;
  interfering_characters: string | string[];  // Accept either format
}

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000/api') {
    this.baseUrl = baseUrl;
  }

  public async request<T>(endpoint: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        data: null as any,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }

  // Arc endpoints
  async getArcs(series: string): Promise<ApiResponse<NarrativeArc[]>> {
    return this.request<NarrativeArc[]>(`/arcs/series/${series}`);
  }

  async getArcById(arcId: string): Promise<ApiResponse<NarrativeArc>> {
    return this.request<NarrativeArc>(`/arcs/${arcId}`);
  }

  async createArc(arcData: CreateArcData): Promise<ApiResponse<NarrativeArc>> {
    console.log('Received arcData with progressions:', arcData.progressions?.length);

    // Validate required fields
    if (!arcData.title || !arcData.description || !arcData.arc_type || !arcData.series) {
      console.error('Missing required fields:', {
        hasTitle: !!arcData.title,
        hasDescription: !!arcData.description,
        hasArcType: !!arcData.arc_type,
        hasSeries: !!arcData.series
      });
      throw new Error('Missing required fields');
    }

    // Validate and format main_characters
    const mainCharacters = Array.isArray(arcData.main_characters)
      ? arcData.main_characters.join(';')
      : typeof arcData.main_characters === 'string'
        ? arcData.main_characters
        : '';

    console.log('Formatted main_characters:', mainCharacters);

    // If we have multiple progressions, use the first one as initial_progression
    let initialProgression: ArcCreateData['initial_progression'] | undefined;
    
    if (arcData.progressions?.[0]) {
      const firstProgression = arcData.progressions[0];
      console.log('Using first progression as initial progression:', firstProgression);

      if (firstProgression.content && firstProgression.season && firstProgression.episode) {
        initialProgression = {
          content: firstProgression.content,
          season: firstProgression.season,
          episode: firstProgression.episode,
          interfering_characters: Array.isArray(firstProgression.interfering_characters)
            ? firstProgression.interfering_characters.join(';')
            : firstProgression.interfering_characters || ''
        };
      }
    }

    const formattedData: ArcCreateData = {
      title: arcData.title,
      description: arcData.description,
      arc_type: arcData.arc_type,
      main_characters: mainCharacters,
      series: arcData.series,
      initial_progression: initialProgression
    };

    console.log('Sending formatted data to API:', formattedData);

    // Create the arc with initial progression
    const response = await this.request<NarrativeArc>('/arcs', {
      method: 'POST',
      body: JSON.stringify(formattedData),
    });

    // Check for error response
    if ('error' in response) {
      return response;
    }

    // If we have more progressions, add them to the created arc
    if (arcData.progressions && arcData.progressions.length > 1) {
      console.log(`Adding ${arcData.progressions.length - 1} additional progressions`);
      
      // Add remaining progressions
      for (let i = 1; i < arcData.progressions.length; i++) {
        const prog = arcData.progressions[i];
        
        // Skip if missing required fields
        if (!prog.content || !prog.season || !prog.episode) {
          console.warn('Skipping progression with missing required fields:', prog);
          continue;
        }

        await this.createProgression({
          arc_id: response.data.id,
          content: prog.content,
          series: prog.series || arcData.series,
          season: prog.season,
          episode: prog.episode,
          interfering_characters: Array.isArray(prog.interfering_characters)
            ? prog.interfering_characters.join(';')
            : ''
        });
      }
    }

    return response;
  }

  async updateArc(
    arcId: string,
    updateData: {
      title?: string;
      description?: string;
      arc_type?: string;
      main_characters?: string[] | string;
    }
  ): Promise<ApiResponse<NarrativeArc>> {
    const formattedData = {
      ...updateData,
      main_characters: typeof updateData.main_characters === 'string'
        ? (updateData.main_characters as string).split(';')
        : updateData.main_characters
    };

    return this.request<NarrativeArc>(
      `/arcs/${arcId}`,
      {
        method: 'PATCH',
        body: JSON.stringify(formattedData)
      }
    );
  }

  async deleteArc(arcId: string): Promise<ApiResponse<void>> {
    return this.request<void>(`/arcs/${arcId}`, {
      method: 'DELETE',
    });
  }

  async mergeArcs(
    arc1Id: string,
    arc2Id: string,
    mergedData: Partial<NarrativeArc>
  ): Promise<ApiResponse<NarrativeArc>> {
    return this.request<NarrativeArc>('/arcs/merge', {
      method: 'POST',
      body: JSON.stringify({
        arc_id_1: arc1Id,
        arc_id_2: arc2Id,
        ...mergedData,
      }),
    });
  }

  // Character endpoints
  async getCharacters(series: string): Promise<ApiResponse<Character[]>> {
    return this.request<Character[]>(`/characters/${series}`);
  }

  async createCharacter(series: string, characterData: Partial<Character>): Promise<ApiResponse<Character>> {
    return this.request<Character>(`/characters/${series}`, {
      method: 'POST',
      body: JSON.stringify(characterData),
    });
  }

  async updateCharacter(series: string, characterData: Partial<Character>): Promise<ApiResponse<Character>> {
    return this.request<Character>(`/characters/${series}`, {
      method: 'PATCH',
      body: JSON.stringify(characterData),
    });
  }

  async deleteCharacter(series: string, entityName: string): Promise<ApiResponse<void>> {
    return this.request<void>(`/characters/${series}/${entityName}`, {
      method: 'DELETE',
    });
  }

  async mergeCharacters(
    series: string,
    data: {
      character1_id: string;
      character2_id: string;
      keep_character: 'character1' | 'character2';
    }
  ): Promise<ApiResponse<void>> {
    return this.request<void>(`/characters/${series}/merge`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Vector store endpoints
  async searchVectorStore(
    series: string, 
    query?: string
  ): Promise<ApiResponse<VectorStoreEntry[]>> {
    const endpoint = query 
      ? `/vector-store/${series}?query=${encodeURIComponent(query)}`
      : `/vector-store/${series}`;
    return this.request<VectorStoreEntry[]>(endpoint);
  }

  async getArcClusters(
    series: string,
    params: {
      threshold?: number;
      min_cluster_size?: number;
      max_clusters?: number;
    } = {}
  ): Promise<ApiResponse<ArcCluster[]>> {
    const queryParams = new URLSearchParams();
    if (params.threshold) queryParams.append('threshold', params.threshold.toString());
    if (params.min_cluster_size) queryParams.append('min_cluster_size', params.min_cluster_size.toString());
    if (params.max_clusters) queryParams.append('max_clusters', params.max_clusters.toString());

    const endpoint = `/vector-store/${series}/clusters${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.request<ArcCluster[]>(endpoint);
  }

  async compareArcs(arcIds: string[]): Promise<ApiResponse<{ distance: number }>> {
    return this.request<{ distance: number }>('/vector-store/compare', {
      method: 'POST',
      body: JSON.stringify(arcIds),
    });
  }

  async updateProgression(progressionId: string, data: Partial<ArcProgression>): Promise<ApiResponse<ArcProgression>> {
    const formattedData = {
      content: data.content,
      interfering_characters: data.interfering_characters || []
    };

    return this.request<ArcProgression>(`/progressions/${progressionId}`, {
      method: 'PATCH',
      body: JSON.stringify(formattedData),
    });
  }

  async createProgression(data: CreateProgressionData): Promise<ApiResponse<ArcProgression>> {
    // Format the data before sending
    const formattedData = {
      ...data,
      interfering_characters: Array.isArray(data.interfering_characters)
        ? data.interfering_characters.join(';')
        : data.interfering_characters
    };

    return this.request<ArcProgression>('/progressions', {
      method: 'POST',
      body: JSON.stringify(formattedData),
    });
  }

  async deleteProgression(progressionId: string): Promise<ApiResponse<void>> {
    return this.request<void>(
      `/progressions/${progressionId}`,
      {
        method: 'DELETE'
      }
    );
  }

  async generateProgression(
    arcId: string | null,
    series: string,
    season: string,
    episode: string,
    title?: string,
    description?: string
  ): Promise<ApiProgressionResponse> {
    try {
      const response = await this.request<GenerateProgressionResponse>(
        `/progressions/generate?series=${series}&season=${season}&episode=${episode}`,
        {
          method: 'POST',
          body: JSON.stringify({
            arc_id: arcId,
            arc_title: title || null,
            arc_description: description || null,
            delete_existing: true
          }),
        }
      );

      // Handle error response
      if ('error' in response) {
        console.error('Generation error:', response.error);
        return {
          data: null,
          error: response.error
        };
      }

      // Handle NO_PROGRESSION case
      if (response.data?.content === "NO_PROGRESSION") {
        return {
          data: null,
          error: "No progression found for this arc in this episode"
        };
      }

      // Handle missing or invalid content
      if (!response.data?.content) {
        return {
          data: null,
          error: "Failed to generate progression content"
        };
      }

      // Return successful response
      return {
        data: {
          content: response.data.content,
          interfering_characters: response.data.interfering_characters || []
        }
      };
    } catch (error) {
      console.error('Generation error:', error);
      return {
        data: null,
        error: error instanceof Error ? error.message : 'Unknown error occurred'
      };
    }
  }
} 