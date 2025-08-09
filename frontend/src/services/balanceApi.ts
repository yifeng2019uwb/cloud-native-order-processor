import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type {
  DepositRequest,
  WithdrawRequest,
  BalanceTransactionListRequest,
  BalanceResponse,
  BalanceTransactionResponse,
  BalanceApiError
} from '@/types';

class BalanceApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1/balance', // Uses gateway proxy
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

  private formatError(error: AxiosError): BalanceApiError {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format
      if (responseData.detail && typeof responseData.detail === 'object') {
        return responseData.detail as BalanceApiError;
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as BalanceApiError;
      }

      // Fallback to direct data
      return responseData as BalanceApiError;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  // Balance API methods
  async getBalance(): Promise<BalanceResponse> {
    const response = await this.api.get<BalanceResponse>('');
    return response.data;
  }

  async deposit(depositData: DepositRequest): Promise<{success: boolean, message: string, transaction_id: string, timestamp: string}> {
    const response = await this.api.post<{success: boolean, message: string, transaction_id: string, timestamp: string}>('/deposit', depositData);
    return response.data;
  }

  async withdraw(withdrawData: WithdrawRequest): Promise<{success: boolean, message: string, transaction_id: string, timestamp: string}> {
    const response = await this.api.post<{success: boolean, message: string, transaction_id: string, timestamp: string}>('/withdraw', withdrawData);
    return response.data;
  }

  async getTransactions(params?: BalanceTransactionListRequest): Promise<BalanceTransactionResponse> {
    const queryParams = new URLSearchParams();

    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }

    if (params?.offset) {
      queryParams.append('offset', params.offset.toString());
    }

    if (params?.transaction_type) {
      queryParams.append('transaction_type', params.transaction_type);
    }

    const url = `/transactions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await this.api.get<BalanceTransactionResponse>(url);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const balanceApiService = new BalanceApiService();
export default balanceApiService;
