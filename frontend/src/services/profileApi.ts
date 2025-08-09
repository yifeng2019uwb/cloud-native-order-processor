import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type { User, ApiErrorResponse } from '@/types';

export interface ProfileUpdateRequest {
  first_name?: string;
  last_name?: string;
  email?: string;
  phone?: string;
  date_of_birth?: string;
}

export interface ProfileUpdateResponse {
  success: boolean;
  message: string;
  user: User;
  timestamp: string;
}

class ProfileApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1/auth',
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor - Add JWT token to requests
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - Handle errors and token expiration
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          localStorage.removeItem('auth_token');
          window.location.href = '/auth';
        }
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private formatError(error: AxiosError): ApiErrorResponse {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format
      if (responseData.detail && typeof responseData.detail === 'object') {
        return responseData.detail as ApiErrorResponse;
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as ApiErrorResponse;
      }

      // Fallback to direct data
      return responseData as ApiErrorResponse;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  async updateProfile(profileData: ProfileUpdateRequest): Promise<ProfileUpdateResponse> {
    const response = await this.api.put<ProfileUpdateResponse>('/me', profileData);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const profileApiService = new ProfileApiService();
export default profileApiService;
