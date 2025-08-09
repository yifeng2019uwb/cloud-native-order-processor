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

          // Get user data from storage
          const { user } = authUtils.getStoredAuthData();

          if (user) {
            setState({
              user,
              token,
              isAuthenticated: true,
              isLoading: false,
              error: null
            });
          } else {
            // If no user data in storage, clear auth
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
      // Make the API call
      const loginResponse = await apiService.login(credentials);

      // Get the real user profile from the backend
      const profileResponse = await apiService.getProfile();

      const token = loginResponse.access_token || loginResponse.data?.access_token;
      if (!token) {
        throw new Error('No access token received from login');
      }

      // Set token in API service for subsequent requests
      apiService.setAuthToken(token);

      // Store auth data
      authUtils.saveAuthData(token, profileResponse.user);

      // Set authenticated state with real user data
      setState({
        user: profileResponse.user,
        token: token,
        isAuthenticated: true,
        isLoading: false,
        error: null
      });

      console.log('✅ Login successful with real profile data!');
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
      console.log('🚀 Starting registration with data:', userData);
      const response: AuthResponse = await apiService.register(userData);

      console.log('🔍 Registration response type:', typeof response);
      console.log('🔍 Registration response keys:', Object.keys(response || {}));
      console.log('🔍 Registration response:', JSON.stringify(response, null, 2));
      console.log('🔍 Response.success value:', response?.success);
      console.log('🔍 Response.success type:', typeof response?.success);

      if (response && response.success === true) {
        // Registration successful! Backend doesn't provide token/user data for registration
        console.log('✅ Registration successful:', response.message);

        // Just update loading state - user needs to login separately after registration
        setState(prev => ({
          ...prev,
          isLoading: false,
          error: null
        }));

        // Registration complete - no auto-login
        console.log('✅ Registration flow completed successfully');
        return;
      } else {
        console.log('❌ Registration failed - response.success is not true');
        console.log('❌ Response object:', response);
        throw new Error(`Registration failed: ${response?.message || 'Unknown error'}`);
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
      // Fetch fresh profile data from the API
      const profileResponse = await apiService.getProfile();

      // Update state with fresh data
      setState(prev => ({
        ...prev,
        user: profileResponse.user
      }));

      // Update stored data
      const { token } = authUtils.getStoredAuthData();
      if (token) {
        authUtils.saveAuthData(token, profileResponse.user);
      }
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