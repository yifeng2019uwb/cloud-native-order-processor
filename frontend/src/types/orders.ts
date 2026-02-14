// Order related types
export interface Order {
  order_id: string;
  asset_id: string;
  quantity: string; // Backend returns as string
  price: string; // Backend returns as string
  order_type: 'market_buy' | 'market_sell' | 'limit_buy' | 'limit_sell';
  created_at: string;
  // Optional fields that may be added by frontend or other services
  username?: string;
  status?: 'pending' | 'completed' | 'failed' | 'cancelled';
  total_cost?: number; // For buy orders
  total_received?: number; // For sell orders
  updated_at?: string;
  completed_at?: string;
}

export interface CreateOrderRequest {
  asset_id: string;
  quantity: number;
  /** Omit or null for market orders; required for limit orders */
  price?: number | null;
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
  message: string;
  data: Order[];
  has_more: boolean;
  timestamp: string;
}

// Backend returns: { data: OrderData }
export type OrderCreateResponse = Order;

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

export type OrderApiResponse = OrderCreateResponse | OrderDetailResponse | OrderListResponse | OrderApiError;
