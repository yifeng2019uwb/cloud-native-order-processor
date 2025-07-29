import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type {
  AssetListRequest,
  AssetListResponse,
  AssetDetailResponse,
  InventoryApiError
} from '@/types';

class InventoryApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: '/api/v1/inventory', // Uses gateway in both dev and prod
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000,
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Response interceptor - Handle errors
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        return Promise.reject(this.formatError(error));
      }
    );
  }

  private formatError(error: AxiosError): InventoryApiError {
    if (error.response?.data) {
      const responseData = error.response.data as any;

      // Handle FastAPI HTTPException format
      if (responseData.detail && typeof responseData.detail === 'object') {
        return responseData.detail as InventoryApiError;
      }

      // Handle direct error response format
      if (responseData.success === false) {
        return responseData as InventoryApiError;
      }

      // Fallback to direct data
      return responseData as InventoryApiError;
    }

    return {
      success: false,
      error: 'NETWORK_ERROR',
      message: error.message || 'Network error occurred',
      timestamp: new Date().toISOString()
    };
  }

  // Inventory API methods
  async listAssets(params?: AssetListRequest): Promise<AssetListResponse> {
    const queryParams = new URLSearchParams();

    if (params?.active_only !== undefined) {
      queryParams.append('active_only', params.active_only.toString());
    }

    if (params?.limit) {
      queryParams.append('limit', params.limit.toString());
    }

    const url = `/assets${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const response = await this.api.get<AssetListResponse>(url);
    return response.data;
  }

  async getAssetById(assetId: string): Promise<AssetDetailResponse> {
    const response = await this.api.get<AssetDetailResponse>(`/assets/${assetId}`);
    return response.data;
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/assets/health');
    return response.data;
  }

  async debugInfo(): Promise<any> {
    const response = await this.api.get('/assets/debug');
    return response.data;
  }
}

// Export singleton instance
export const inventoryApiService = new InventoryApiService();
export default inventoryApiService;