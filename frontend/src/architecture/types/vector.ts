export interface VectorStoreEntry {
  id: string;
  content: string;
  metadata: Record<string, any>;
  embedding?: number[];
  distance?: number;
} 