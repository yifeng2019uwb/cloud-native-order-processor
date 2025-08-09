// Asset Balance related types
export interface AssetBalance {
  username: string;
  asset_id: string;
  asset_name?: string;
  quantity: number;
  average_cost?: number;
  total_cost?: number;
  current_price?: number;
  current_value?: number;
  unrealized_pnl?: number;
  unrealized_pnl_percentage?: number;
  created_at: string;
  updated_at: string;
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
  asset_balances: AssetBalance[];
  total_count: number;
  limit: number;
  offset: number;
  timestamp: string;
}

export interface AssetBalanceDetailResponse {
  success: boolean;
  asset_balance: AssetBalance;
  timestamp: string;
}

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
