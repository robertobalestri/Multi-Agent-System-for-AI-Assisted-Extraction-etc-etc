export interface ApiErrorResponse {
  error: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface ApiSuccessResponse<T> {
  data: T;
  meta?: {
    total?: number;
    page?: number;
    limit?: number;
  };
}

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export const isApiError = (response: unknown): response is ApiErrorResponse => {
  return typeof response === 'object' && response !== null && 'error' in response;
};

export const isApiSuccess = <T>(response: unknown): response is ApiSuccessResponse<T> => {
  return typeof response === 'object' && response !== null && 'data' in response;
}; 