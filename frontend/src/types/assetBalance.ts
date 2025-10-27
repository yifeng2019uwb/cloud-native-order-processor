// Asset Balance related types
export interface AssetBalance {
  asset_id: string;
  quantity: string; // Backend returns as string
  created_at: string;
  updated_at: string;
  // New fields from enhanced API response
  asset_name: string;
  current_price: number;
  total_value: number;
  // Optional computed fields (may be added by frontend)
  username?: string;
  average_cost?: number;
  total_cost?: number;
  current_value?: number;
  unrealized_pnl?: number;
  unrealized_pnl_percentage?: number;
}

export interface AssetTransaction {
  transaction_id: string;
  username: string;
  asset_id: string;
  transaction_type: 'buy' | 'sell';
  quantity: number;
  price: number;
  total_amount: number;
  order_id?: string;
  balance_before: number;
  balance_after: number;
  created_at: string;
}

export interface AssetBalanceListRequest {
  limit?: number;
  offset?: number;
  minimum_balance?: number;
}

export interface AssetTransactionListRequest {
  limit?: number;
  offset?: number;
  transaction_type?: 'buy' | 'sell';
}

export interface AssetBalanceListResponse {
  success: boolean;
  message: string;
  data: AssetBalance[];
  timestamp: string;
}

// Backend returns AssetBalance directly without wrapper
export type AssetBalanceDetailResponse = AssetBalance;

export interface AssetTransactionListResponse {
  success: boolean;
  transactions: AssetTransaction[];
  total_count: number;
  limit: number;
  offset: number;
  timestamp: string;
}

export interface AssetBalanceApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
}

export type AssetBalanceApiResponse = AssetBalanceListResponse | AssetBalanceDetailResponse | AssetTransactionListResponse | AssetBalanceApiError;
