export interface AssetTransactionHistory {
  asset_id: string;
  transaction_type: 'buy' | 'sell';
  quantity: string;
  price: string;
  status: 'completed' | 'pending' | 'failed' | 'cancelled';
  timestamp: string;
}

export interface AssetTransactionHistoryResponse {
  success: boolean;
  message: string;
  data: AssetTransactionHistory[];
  has_more: boolean;
  timestamp: string;
}

export interface AssetTransactionHistoryError {
  success: false;
  message: string;
  error_code?: string;
  timestamp: string;
}

export type AssetTransactionHistoryApiResponse = AssetTransactionHistoryResponse | AssetTransactionHistoryError;
