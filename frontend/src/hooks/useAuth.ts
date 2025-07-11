import React, { useState, useEffect, useCallback, createContext, useContext, ReactNode } from 'react';
import { apiService } from '@/services/api';
import { authUtils } from '@/utils/auth';
import type { User, LoginRequest, RegisterRequest, AuthResponse } from '@/types';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  refreshProfile: () => Promise<void>;
}

// Create Auth Context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Custom hook to use auth context
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Auth hook implementation
const useAuthState = () => {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
    error: null
  });

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const { token } = authUtils.getStoredAuthData();

        if (token && authUtils.hasValidToken()) {
          apiService.setAuthToken(token);

          try {
            const profileResponse = await apiService.getProfile();
            setState({
              user: profileResponse.user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
          } catch {
            authUtils.clearAuthData();
            setState({
              user: null,
              token: null,
              isAuthenticated: false,
              isLoading: false,
              error: null
            });
          }
        } else {
          setState(prev => ({ ...prev, isLoading: false }));
        }
      } catch {
        setState({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: 'Failed to initialize authentication'
        });
      }
    };

    initializeAuth();
  }, []);

  const login = useCallback(async (credentials: LoginRequest) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response: AuthResponse = await apiService.login(credentials);
      console.log('Registration response:', response);

      if (response.success === true) {
        authUtils.saveAuthData(response.access_token, response.user);

        setState({
          user: response.user,
          token: response.access_token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
      } else {
        throw new Error('Invalid login response');
      }
    } catch (error: unknown) {
      setState(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Login failed'
      }));
      throw error;
    }
  }, []);

  const register = useCallback(async (userData: RegisterRequest) => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response: AuthResponse = await apiService.register(userData);

      if (response.success === true && response.access_token) {
        authUtils.saveAuthData(response.access_token, response.user);

        setState({
          user: response.user,
          token: response.access_token,
          isAuthenticated: true,
          isLoading: false,
          error: null
        });
      } else {
        throw new Error('Invalid registration response');
      }
    } catch (error: unknown) {
      console.log('Registration error:', error);

      // Handle different types of errors
      if (error && typeof error === 'object' && 'validation_errors' in error) {
        // Validation errors are handled by the component
        setState(prev => ({ ...prev, isLoading: false }));
        throw error; // Re-throw for component to handle
      } else if (error && typeof error === 'object' && 'message' in error) {
        // API error with message
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: (error as { message: string }).message
        }));
        throw error;
      } else {
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: error instanceof Error ? error.message : 'Registration failed'
        }));
        throw error;
      }
    }
  }, []);

  const logout = useCallback(() => {
    authUtils.clearAuthData();
    apiService.clearAuthToken();

    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null
    });
  }, []);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  const refreshProfile = useCallback(async () => {
    if (!state.isAuthenticated) return;

    try {
      const response = await apiService.getProfile();
      setState(prev => ({
        ...prev,
        user: response.user
      }));
    } catch (error) {
      console.error('Failed to refresh profile:', error);
    }
  }, [state.isAuthenticated]);

  return {
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshProfile
  };
};

// Auth Provider Component
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const auth = useAuthState();

  return React.createElement(AuthContext.Provider, { value: auth }, children);
};