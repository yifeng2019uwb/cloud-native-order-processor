export interface User {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone?: string;
  date_of_birth?: string; // ISO date string
  marketing_emails_consent: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string; // Changed from email to username
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  phone?: string;
  date_of_birth?: string; // ISO date string (YYYY-MM-DD)
  marketing_emails_consent?: boolean;
}

export interface AuthResponse {
  success: boolean;
  message: string;
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  timestamp: string;
}

export interface AuthError {
  success: false;
  error: string;
  message: string;
  details?: unknown;
  timestamp: string;
}