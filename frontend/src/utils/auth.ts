import type { User } from '@/types';

// Token storage keys
const AUTH_TOKEN_KEY = 'auth_token';
const USER_DATA_KEY = 'user_data';

// Token storage functions
export const tokenStorage = {
  get: (): string | null => {
    try {
      return localStorage.getItem(AUTH_TOKEN_KEY);
    } catch {
      return null;
    }
  },

  set: (token: string): void => {
    try {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    } catch (error) {
      // Silent fail for localStorage errors
    }
  },

  remove: (): void => {
    try {
      localStorage.removeItem(AUTH_TOKEN_KEY);
    } catch (error) {
      // Silent fail for localStorage errors
    }
  }
};

// User data persistence
export const userStorage = {
  get: (): User | null => {
    try {
      const userData = localStorage.getItem(USER_DATA_KEY);
      return userData ? JSON.parse(userData) : null;
    } catch {
      return null;
    }
  },

  set: (user: User): void => {
    try {
      localStorage.setItem(USER_DATA_KEY, JSON.stringify(user));
    } catch (error) {
      // Silent fail for localStorage errors
    }
  },

  remove: (): void => {
    try {
      localStorage.removeItem(USER_DATA_KEY);
    } catch (error) {
      // Silent fail for localStorage errors
    }
  }
};

// Token validation helpers
export const tokenUtils = {
  isExpired: (token: string): boolean => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      return payload.exp < currentTime;
    } catch {
      return true;
    }
  },

  getExpirationTime: (token: string): Date | null => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return new Date(payload.exp * 1000);
    } catch {
      return null;
    }
  },

  getUserEmail: (token: string): string | null => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return payload.sub || null;
    } catch {
      return null;
    }
  }
};

// Auth state helpers
export const authUtils = {
  clearAuthData: (): void => {
    tokenStorage.remove();
    userStorage.remove();
  },

  saveAuthData: (token: string, user: User): void => {
    tokenStorage.set(token);
    userStorage.set(user);
  },

  hasValidToken: (): boolean => {
    const token = tokenStorage.get();
    if (!token) return false;
    return !tokenUtils.isExpired(token);
  },

  getStoredAuthData: (): { token: string | null; user: User | null } => {
    return {
      token: tokenStorage.get(),
      user: userStorage.get()
    };
  }
};