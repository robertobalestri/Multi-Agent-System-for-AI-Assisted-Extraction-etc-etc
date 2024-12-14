import { useState, useCallback } from 'react';
import type { ApiResponse } from '@/architecture/types';
import { ApiClient } from '@/services/api/ApiClient';

export function useApi() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = useCallback(async <T>(
    apiCall: () => Promise<ApiResponse<T>>
  ): Promise<T | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiCall();
      if (response.error) {
        throw new Error(response.error);
      }
      return response.data;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return {
    isLoading,
    error,
    request,
  };
} 