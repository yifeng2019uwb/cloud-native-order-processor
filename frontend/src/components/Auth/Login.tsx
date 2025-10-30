import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { apiService } from '@/services/api';
import { authUtils } from '@/utils/auth';
import { UI_STRINGS } from '@/constants/ui';
import type { LoginRequest } from '@/types';
import { BACKEND_VALIDATION_RULES } from '@/types';

const Login: React.FC = () => {
  const location = useLocation();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);
  const [formData, setFormData] = useState<LoginRequest>({
    username: '',
    password: ''
  });
  const [formErrors, setFormErrors] = useState<Partial<LoginRequest>>({});

  // Get registration success info from navigation state
  const registrationSuccess = location.state?.registrationSuccess;
  const registeredUsername = location.state?.username;

  const validateForm = (): boolean => {
    const errors: Partial<LoginRequest> = {};

    // Username validation (matching backend)
    if (!formData.username) {
      errors.username = UI_STRINGS.USERNAME_REQUIRED;
    } else if (formData.username.length < BACKEND_VALIDATION_RULES.username.minLength ||
               formData.username.length > BACKEND_VALIDATION_RULES.username.maxLength) {
      errors.username = `Username must be ${BACKEND_VALIDATION_RULES.username.minLength}-${BACKEND_VALIDATION_RULES.username.maxLength} characters`;
    } else if (!BACKEND_VALIDATION_RULES.username.pattern.test(formData.username)) {
      errors.username = BACKEND_VALIDATION_RULES.username.message;
    }

    // Password validation (matching backend)
    if (!formData.password) {
      errors.password = UI_STRINGS.PASSWORD_REQUIRED;
    } else if (formData.password.length < BACKEND_VALIDATION_RULES.password.minLength ||
               formData.password.length > BACKEND_VALIDATION_RULES.password.maxLength) {
      errors.password = `Password must be ${BACKEND_VALIDATION_RULES.password.minLength}-${BACKEND_VALIDATION_RULES.password.maxLength} characters`;
    } else if (!BACKEND_VALIDATION_RULES.password.pattern.test(formData.password)) {
      errors.password = BACKEND_VALIDATION_RULES.password.message;
    }


    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

    const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Sanitize login data
      const loginData = {
        username: formData.username.trim(),
        password: formData.password
      };

                  const response = await apiService.login(loginData);

      // Check if response has the expected structure
      const authData = response.data || response;
      const token = authData.access_token || response.access_token;
      const user = (authData as any).user || (response as any).user;

      if (!token) {
        throw new Error('Invalid login response - missing access token');
      }

            // For login, if user data is not in response, we'll fetch it after login
      if (user) {
        authUtils.saveAuthData(token, user);
      } else {
        // Save token and try to get user profile separately
        authUtils.saveAuthData(token, {
          username: loginData.username,
          email: '', // Will be populated after profile fetch
          first_name: '',
          last_name: '',
          marketing_emails_consent: false,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        } as any);
      }

      // Force a full page reload to reinitialize auth state
      window.location.href = '/dashboard';
    } catch (error: any) {
      setIsLoading(false);
      setError(error?.message || UI_STRINGS.LOGIN_FAILED);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear registration success message when user starts typing
    if (location.state?.registrationSuccess) {
      window.history.replaceState(null, '', location.pathname);
    }

    // Clear field error when user starts typing
    if (formErrors[name as keyof LoginRequest]) {
      setFormErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  // handleSwitchToRegister function removed - using Link component instead

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Access your Order Processor dashboard
          </p>
        </div>

        <div className="mt-8 space-y-6">
          {/* Registration Success Celebration */}
          {registrationSuccess && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    🎉 Welcome to Order Processor!
                  </h3>
                  <p className="text-sm text-green-700 mt-1">
                    Your account <span className="font-medium">{registeredUsername}</span> has been created successfully.
                    Please sign in below to start trading.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Global Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            {/* Username Field */}
            <div>
              <label htmlFor="username" className="sr-only">Username</label>
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  formErrors.username
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-t-md focus:outline-none focus:z-10 sm:text-sm`}
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
              />
              {formErrors.username && (
                <p className="mt-1 text-sm text-red-600">{formErrors.username}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="sr-only">Password</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  formErrors.password
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-b-md focus:outline-none focus:z-10 sm:text-sm`}
                placeholder="Password"
                value={formData.password}
                onChange={handleChange}
              />
              {formErrors.password && (
                <p className="mt-1 text-sm text-red-600">{formErrors.password}</p>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={isLoading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : null}
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>

          {/* Switch to Register - Always show */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{' '}
              <Link
                to="/register"
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Sign up here
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;