import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { API_URLS, API_PATHS, buildQueryString } from '@/constants';
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
      baseURL: API_URLS.INVENTORY,
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
    const queryString = buildQueryString({
      active_only: params?.active_only?.toString(),
      limit: params?.limit?.toString()
    });
    const url = `${API_PATHS.INVENTORY_ASSETS}${queryString}`;
    const response = await this.api.get<AssetListResponse>(url);
    return response.data;
  }

  async getAssetById(assetId: string): Promise<AssetDetailResponse> {
    const response = await this.api.get<{ data: AssetDetailResponse }>(API_PATHS.INVENTORY_ASSET_BY_ID(assetId));
    return response.data.data;  // Backend returns { data: AssetDetailData }
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await this.api.get<{ status: string }>('/assets/health');
    return response.data;
  }
}

// Export singleton instance
export const inventoryApiService = new InventoryApiService();
export default inventoryApiService;