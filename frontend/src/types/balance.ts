// Balance related types
export interface Balance {
  username: string;
  balance: number;
  currency: string;
  last_updated: string;
}

export interface BalanceTransaction {
  transaction_id: string;
  username: string;
  transaction_type: 'deposit' | 'withdrawal' | 'order_debit' | 'order_credit';
  amount: number;
  balance_before: number;
  balance_after: number;
  description?: string;
  reference_id?: string; // Order ID for order-related transactions
  created_at: string;
}

export interface DepositRequest {
  amount: number;
  description?: string;
}

export interface WithdrawRequest {
  amount: number;
  description?: string;
}

export interface BalanceTransactionListRequest {
  limit?: number;
  offset?: number;
  transaction_type?: 'deposit' | 'withdrawal' | 'order_debit' | 'order_credit';
}

export interface BalanceResponse {
  success: boolean;
  balance: Balance;
  timestamp: string;
}

export interface BalanceTransactionResponse {
  success: boolean;
  transactions: BalanceTransaction[];
  total_count: number;
  limit: number;
  offset: number;
  timestamp: string;
}

export interface BalanceApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
  validation_errors?: Record<string, string[]>;
}

export type BalanceApiResponse = BalanceResponse | BalanceTransactionResponse | BalanceApiError;
