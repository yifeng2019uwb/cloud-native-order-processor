import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type {
  PortfolioResponse,
  PortfolioApiError
} from '@/types';

class PortfolioApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1/portfolio', // Uses gateway proxy
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

  private formatError(error: AxiosError): PortfolioApiError {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format
      if (responseData.detail && typeof responseData.detail === 'object') {
        return responseData.detail as PortfolioApiError;
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as PortfolioApiError;
      }

      // Fallback to direct data
      return responseData as PortfolioApiError;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  // Portfolio API methods
  async getPortfolio(username: string): Promise<PortfolioResponse> {
    const response = await this.api.get<PortfolioResponse>(`/${username}`);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const portfolioApiService = new PortfolioApiService();
export default portfolioApiService;
