export interface CnyClaimRequest {
  phrase: string;
}

export interface CnyClaimResponse {
  success: boolean;
  message: string;
  amount: number;
  got_red_pocket: boolean;
  timestamp: string;
}
