export interface User {
    email: string;
    name: string;
    phone?: string;
    created_at: string;
    updated_at: string;
  }

  export interface LoginRequest {
    email: string;
    password: string;
  }

  export interface RegisterRequest {
    username: string;
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }

  export interface AuthResponse {
    message: string;
    status: string;
    access_token: string;
    token_type: string;
    expires_in: number;
    user: User;
  }

  export interface AuthError {
    message: string;
    status: string;
    error?: string;
  }