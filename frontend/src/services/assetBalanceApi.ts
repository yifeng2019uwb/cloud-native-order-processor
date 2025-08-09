import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type {
  AssetBalanceListRequest,
  AssetTransactionListRequest,
  AssetBalanceListResponse,
  AssetTransactionListResponse,
  AssetBalanceDetailResponse,
  AssetBalanceApiError
} from '@/types';

class AssetBalanceApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1/assets', // Uses gateway proxy
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

  private formatError(error: AxiosError): AssetBalanceApiError {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format
      if (responseData.detail && typeof responseData.detail === 'object') {
        return responseData.detail as AssetBalanceApiError;
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as AssetBalanceApiError;
      }

      // Fallback to direct data
      return responseData as AssetBalanceApiError;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  // Asset Balance API methods
  async listAssetBalances(params?: AssetBalanceListRequest): Promise<AssetBalanceListResponse> {
    const queryParams = new URLSearchParams();

    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }

    if (params?.offset) {
      queryParams.append('offset', params.offset.toString());
    }

    if (params?.minimum_balance) {
      queryParams.append('minimum_balance', params.minimum_balance.toString());
    }

    const url = `/balances${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await this.api.get<AssetBalanceListResponse>(url);
    return response.data;
  }

  async getAssetBalance(assetId: string): Promise<AssetBalanceDetailResponse> {
    const response = await this.api.get<AssetBalanceDetailResponse>(`/${assetId}/balance`);
    return response.data;
  }

  async getAssetTransactions(assetId: string, params?: AssetTransactionListRequest): Promise<AssetTransactionListResponse> {
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

    const url = `/${assetId}/transactions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await this.api.get<AssetTransactionListResponse>(url);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/health');
    return response.data;
  }
}

// Export singleton instance
export const assetBalanceApiService = new AssetBalanceApiService();
export default assetBalanceApiService;
