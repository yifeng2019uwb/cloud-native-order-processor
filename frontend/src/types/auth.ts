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
  username: string;
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

// Backend validation rules
export const BACKEND_VALIDATION_RULES = {
  username: {
    minLength: 6,
    maxLength: 30,
    pattern: /^[a-zA-Z0-9][a-zA-Z0-9_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$/,
    message: "Username can only contain letters, numbers, and underscores. Cannot start/end with underscore."
  },
  password: {
    minLength: 12,
    maxLength: 20,
    pattern: /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+])/,
    message: "Password must contain uppercase, lowercase, number, and special character (!@#$%^&*()-_=+)"
  },
  firstName: {
    pattern: /^[a-zA-Z]+$/,
    message: "First name can only contain letters"
  },
  lastName: {
    pattern: /^[a-zA-Z]+$/,
    message: "Last name can only contain letters"
  }
};

export interface AuthResponse {
  success: boolean;
  message: string;
  access_token: string;
  token_type: string;
  expires_in: number;
  user?: User; // Optional for registration response
  username?: string; // For registration response
  is_new_user?: boolean; // For registration response
  timestamp: string;
}

export interface AuthError {
  success: false;
  error: string;
  message: string;
  details?: unknown;
  timestamp: string;
}