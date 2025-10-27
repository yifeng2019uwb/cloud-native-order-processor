// Inventory API Types
// Based on inventory service API models

export interface Asset {
  asset_id: string;
  name: string;
  description?: string;
  category: string;
  price_usd: number;
  is_active: boolean;

  // Enhanced CoinGecko fields
  symbol?: string;
  image?: string;
  market_cap_rank?: number;
  market_cap?: number;
  price_change_24h?: number;
  price_change_percentage_24h?: number;
  price_change_percentage_7d?: number;
  price_change_percentage_30d?: number;
  high_24h?: number;
  low_24h?: number;
  total_volume_24h?: number;
  circulating_supply?: number;
  total_supply?: number;
  max_supply?: number;
  ath?: number;
  ath_change_percentage?: number;
  ath_date?: string;
  atl?: number;
  atl_change_percentage?: number;
  atl_date?: string;
  last_updated?: string;
  sparkline_7d?: {
    price: number[];
  };
}

export interface AssetDetail extends Asset {
  availability_status: 'available' | 'limited' | 'out_of_stock' | 'unavailable';
}

export interface AssetListRequest {
  active_only?: boolean;
  limit?: number;
}

// Backend returns: { data: Asset[], total_count: int, active_count: int }
export interface AssetListResponse {
  data: Asset[];
  total_count: number;
  active_count: number;
}

export interface AssetDetailResponse {
  asset_id: string;
  name: string;
  description?: string;
  category: string;
  price_usd: number;
  is_active: boolean;
  availability_status: 'available' | 'limited' | 'out_of_stock' | 'unavailable';

  // Enhanced CoinGecko fields
  symbol?: string;
  image?: string;
  market_cap_rank?: number;
  market_cap?: number;
  price_change_24h?: number;
  price_change_percentage_24h?: number;
  price_change_percentage_7d?: number;
  price_change_percentage_30d?: number;
  high_24h?: number;
  low_24h?: number;
  total_volume_24h?: number;
  circulating_supply?: number;
  total_supply?: number;
  max_supply?: number;
  ath?: number;
  ath_change_percentage?: number;
  ath_date?: string;
  atl?: number;
  atl_change_percentage?: number;
  atl_date?: string;
  last_updated?: string;
  sparkline_7d?: {
    price: number[];
  };
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