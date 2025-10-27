// Portfolio related types
export interface PortfolioItem {
  asset_id: string;
  quantity: number;
  current_price: number;
  market_value: number;
  percentage: number;
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

// Backend returns assets array directly without wrapper
export interface PortfolioResponse {
  assets: PortfolioItem[];
}

export interface PortfolioApiError {
  success: false;
  error: string;
  message: string;
  timestamp: string;
}

export type PortfolioApiResponse = PortfolioResponse | PortfolioApiError;
