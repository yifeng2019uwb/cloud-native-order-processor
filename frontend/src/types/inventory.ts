// Inventory API Types
// Based on inventory service API models

export interface Asset {
  asset_id: string;
  name: string;
  description?: string;
  category: string;
  price_usd: number;
  is_active: boolean;
}

export interface AssetDetail extends Asset {
  availability_status: 'available' | 'limited' | 'out_of_stock' | 'unavailable';
}

export interface AssetListRequest {
  active_only?: boolean;
  limit?: number;
}

export interface AssetListResponse {
  assets: Asset[];
  total_count: number;
  filtered_count: number;
  active_count: number;
  filters_applied: {
    active_only?: boolean;
    limit?: number;
  };
}

export interface AssetDetailResponse {
  asset_id: string;
  name: string;
  description?: string;
  category: string;
  price_usd: number;
  is_active: boolean;
  availability_status: 'available' | 'limited' | 'out_of_stock' | 'unavailable';
}

// Error responses
export interface InventoryApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
}

// Success responses
export interface InventoryApiSuccess<T> {
  success: true;
  data: T;
  timestamp: string;
}

export type InventoryApiResponse<T> = InventoryApiSuccess<T> | InventoryApiError;