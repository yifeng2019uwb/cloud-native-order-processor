// Order related types
export interface Order {
  order_id: string;
  username: string;
  asset_id: string;
  quantity: number;
  price: number;
  order_type: 'market_buy' | 'market_sell' | 'limit_buy' | 'limit_sell';
  status: 'pending' | 'completed' | 'failed' | 'cancelled';
  total_cost?: number; // For buy orders
  total_received?: number; // For sell orders
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface CreateOrderRequest {
  asset_id: string;
  quantity: number;
  price: number;
  order_type: 'market_buy' | 'market_sell' | 'limit_buy' | 'limit_sell';
}

export interface OrderListRequest {
  limit?: number;
  offset?: number;
  status?: string;
  order_type?: string;
  asset_id?: string;
}

export interface OrderListResponse {
  success: boolean;
  orders: Order[];
  total_count: number;
  limit: number;
  offset: number;
  timestamp: string;
}

export interface OrderDetailResponse {
  success: boolean;
  order: Order;
  timestamp: string;
}

export interface OrderApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
  validation_errors?: Record<string, string[]>;
}

export type OrderApiResponse = OrderDetailResponse | OrderListResponse | OrderApiError;
