import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URLS } from '@/constants';
import type {
  AssetTransactionListRequest,
  AssetTransactionListResponse,
  AssetBalance,
  AssetBalanceApiError
} from '@/types';
import { API_PATHS, buildQueryString } from '@/constants';

class AssetBalanceApiService {
  private api: AxiosInstance;
  private balanceApi: AxiosInstance;

  constructor() {
    // Balance API for asset balance (user service)
    this.api = axios.create({
      baseURL: API_URLS.BALANCE,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    // Assets API for asset transactions (order service)
    this.balanceApi = axios.create({
      baseURL: API_URLS.ASSETS,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Setup for balance API
    this.setupInterceptorForApi(this.api);
    // Setup for assets API
    this.setupInterceptorForApi(this.balanceApi);
  }

  private setupInterceptorForApi(api: AxiosInstance) {
    // Request interceptor - Add JWT token to requests
    api.interceptors.request.use(
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
    api.interceptors.response.use(
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
  async getAssetBalance(assetId: string): Promise<AssetBalance> {
    // Backend returns AssetBalance directly without wrapper
    const response = await this.api.get<AssetBalance>(API_PATHS.BALANCE_ASSET(assetId));
    return response.data;
  }

  async getAssetTransactions(assetId: string, params?: AssetTransactionListRequest): Promise<AssetTransactionListResponse> {
    const queryString = buildQueryString({
      limit: params?.limit?.toString(),
      offset: params?.offset?.toString(),
      transaction_type: params?.transaction_type
    });
    const url = `/${assetId}/transactions${queryString}`;
    // Use assets API (order service) for transaction history
    const response = await this.balanceApi.get<AssetTransactionListResponse>(url);
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
