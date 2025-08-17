import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URLS } from '@/constants';
import type { AssetTransactionHistoryResponse } from '@/types';

class AssetTransactionApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URLS.ASSETS,
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
          // Token expired or invalid - redirect to login
          localStorage.removeItem('auth_token');
          localStorage.removeItem('user_data');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Get transaction history for a specific asset
   */
  async getAssetTransactions(
    assetId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<AssetTransactionHistoryResponse> {
    const response = await this.api.get<AssetTransactionHistoryResponse>(
      `/${assetId}/transactions?limit=${limit}&offset=${offset}`
    );
    return response.data;
  }
}

export const assetTransactionApiService = new AssetTransactionApiService();
