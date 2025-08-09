// Portfolio related types
export interface PortfolioItem {
  asset_id: string;
  asset_name: string;
  quantity: number;
  current_price: number;
  current_value: number;
  cost_basis?: number;
  unrealized_pnl?: number;
  unrealized_pnl_percentage?: number;
}

export interface Portfolio {
  username: string;
  total_value: number;
  total_cost_basis?: number;
  total_unrealized_pnl?: number;
  total_unrealized_pnl_percentage?: number;
  assets: PortfolioItem[];
  last_updated: string;
}

export interface PortfolioRequest {
  include_market_data?: boolean;
  include_pnl?: boolean;
}

export interface PortfolioResponse {
  success: boolean;
  portfolio: Portfolio;
  timestamp: string;
}

export interface PortfolioApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
}

export type PortfolioApiResponse = PortfolioResponse | PortfolioApiError;
