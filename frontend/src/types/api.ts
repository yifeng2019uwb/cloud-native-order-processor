export interface ApiResponse<T = unknown> {
    success: boolean;
    data?: T;
    message?: string;
    timestamp: string;
  }

  export interface ApiError {
    success: false;
    error: string;
    message: string;
    details?: unknown;
    timestamp: string;
  }

  export interface ValidationError {
    field: string;
    message: string;
  }

  export interface ApiErrorResponse {
    success: false;
    error: string;
    message: string;
    validation_errors?: ValidationError[];
    timestamp: string;
  }

  export type ApiResult<T> = ApiResponse<T> | ApiErrorResponse;