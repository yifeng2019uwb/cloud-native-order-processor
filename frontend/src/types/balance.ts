// Balance related types
export interface Balance {
  username: string;
  balance: number;
  currency: string;
  last_updated: string;
}

export interface BalanceTransaction {
  transaction_id: string;
  transaction_type: 'deposit' | 'withdraw' | 'order_debit' | 'order_credit';
  amount: string; // Backend returns amount as string
  status: 'completed' | 'pending' | 'failed';
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
  transaction_type?: 'deposit' | 'withdraw' | 'order_debit' | 'order_credit';
}

export interface BalanceResponse {
  current_balance: string; // Decimal as string from backend
  updated_at: string;
}

export interface BalanceTransactionResponse {
  transactions: BalanceTransaction[];
  total_count: number;
}

export interface BalanceApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
  validation_errors?: Record<string, string[]>;
}

export type BalanceApiResponse = BalanceResponse | BalanceTransactionResponse | BalanceApiError;
