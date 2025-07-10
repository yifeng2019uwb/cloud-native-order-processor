import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import type { RegisterRequest } from '@/types';

interface RegisterProps {
  onSwitchToLogin?: () => void;
}

interface RegisterFormData extends RegisterRequest {
  confirmPassword: string;
}

const Register: React.FC<RegisterProps> = ({ onSwitchToLogin }) => {
  const navigate = useNavigate();
  const { register, isLoading, error, clearError } = useAuth();
  const [formData, setFormData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    date_of_birth: '',
    marketing_emails_consent: false
  });
  const [formErrors, setFormErrors] = useState<Partial<RegisterFormData>>({});

  const validateForm = (): boolean => {
    const errors: Partial<RegisterFormData> = {};

    // Username validation (matching backend)
    if (!formData.username) {
      errors.username = 'Username is required';
    } else if (formData.username.length < 6 || formData.username.length > 30) {
      errors.username = 'Username must be 3-30 characters';
    } else if (!/^[a-zA-Z0-9][a-zA-Z0-9_]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$/.test(formData.username)) {
      errors.username = 'Username can only contain letters, numbers, and underscores. Cannot start/end with underscore.';
    } else if (formData.username.includes('__')) {
      errors.username = 'Username cannot contain consecutive underscores';
    }

    // Email validation
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
    }

    // First name validation (matching backend)
    if (!formData.first_name) {
      errors.first_name = 'First name is required';
    } else if (formData.first_name.length > 50) {
      errors.first_name = 'First name must be 50 characters or less';
    } else if (!/^[a-zA-Z]+$/.test(formData.first_name)) {
      errors.first_name = 'First name can only contain letters';
    }

    // Last name validation (matching backend)
    if (!formData.last_name) {
      errors.last_name = 'Last name is required';
    } else if (formData.last_name.length > 50) {
      errors.last_name = 'Last name must be 50 characters or less';
    } else if (!/^[a-zA-Z]+$/.test(formData.last_name)) {
      errors.last_name = 'Last name can only contain letters';
    }

    // Password validation (matching backend: 8-128 characters)
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 12 || formData.password.length > 20) {
      errors.password = 'Password must be 12-20 characters';
    }

    // Phone validation (optional, but if provided must match backend rules)
    if (formData.phone && formData.phone.trim()) {
      const digitsOnly = formData.phone.replace(/\D/g, '');
      if (digitsOnly.length < 10) {
        errors.phone = 'Phone number must contain at least 10 digits';
      } else if (digitsOnly.length > 15) {
        errors.phone = 'Phone number must contain no more than 15 digits';
      }
    }

    // Date of birth validation (optional, but if provided must be valid)
    if (formData.date_of_birth && formData.date_of_birth.trim()) {
      const birthDate = new Date(formData.date_of_birth);
      const today = new Date();

      if (isNaN(birthDate.getTime())) {
        errors.date_of_birth = 'Please enter a valid date';
      } else if (birthDate > today) {
        errors.date_of_birth = 'Date of birth cannot be in the future';
      } else {
        // Check minimum age (13 years for COPPA compliance)
        const thirteenYearsAgo = new Date();
        thirteenYearsAgo.setFullYear(today.getFullYear() - 13);
        if (birthDate > thirteenYearsAgo) {
          errors.date_of_birth = 'Must be at least 13 years old to register';
        }

        // Check maximum reasonable age (120 years)
        const maxAge = new Date();
        maxAge.setFullYear(today.getFullYear() - 120);
        if (birthDate < maxAge) {
          errors.date_of_birth = 'Invalid date of birth';
        }
      }
    }

    // Confirm password validation
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
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

    try {
      const { confirmPassword, ...registerData } = formData;

      // Clean up optional fields - only send if they have values
      const cleanedData: RegisterRequest = {
        username: registerData.username,
        email: registerData.email,
        password: registerData.password,
        first_name: registerData.first_name,
        last_name: registerData.last_name,
        marketing_emails_consent: registerData.marketing_emails_consent
      };

      // Only include optional fields if they have values
      if (registerData.phone && registerData.phone.trim()) {
        cleanedData.phone = registerData.phone.trim();
      }

      if (registerData.date_of_birth && registerData.date_of_birth.trim()) {
        cleanedData.date_of_birth = registerData.date_of_birth;
      }

      await register(cleanedData);
    } catch (error) {
      // Error is handled by the useAuth hook
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    const fieldValue = type === 'checkbox' ? checked : value;

    setFormData(prev => ({ ...prev, [name]: fieldValue }));

    // Clear field error when user starts typing
    if (formErrors[name as keyof RegisterFormData]) {
      setFormErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSwitchToLogin = () => {
    if (onSwitchToLogin) {
      onSwitchToLogin();
    } else {
      navigate('/login');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join the Order Processor platform
          </p>
        </div>

        <div className="mt-8 space-y-6">
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

          <div className="space-y-4">
            {/* Name Fields */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="first_name" className="block text-sm font-medium text-gray-700">
                  First Name *
                </label>
                <input
                  id="first_name"
                  name="first_name"
                  type="text"
                  required
                  maxLength={50}
                  className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                    formErrors.first_name
                      ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                  } rounded-md focus:outline-none sm:text-sm`}
                  placeholder="First name"
                  value={formData.first_name}
                  onChange={handleChange}
                />
                {formErrors.first_name && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.first_name}</p>
                )}
              </div>

              <div>
                <label htmlFor="last_name" className="block text-sm font-medium text-gray-700">
                  Last Name *
                </label>
                <input
                  id="last_name"
                  name="last_name"
                  type="text"
                  required
                  maxLength={50}
                  className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                    formErrors.last_name
                      ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                      : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                  } rounded-md focus:outline-none sm:text-sm`}
                  placeholder="Last name"
                  value={formData.last_name}
                  onChange={handleChange}
                />
                {formErrors.last_name && (
                  <p className="mt-1 text-sm text-red-600">{formErrors.last_name}</p>
                )}
              </div>
            </div>

            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username *
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                minLength={3}
                maxLength={30}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  formErrors.username
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-md focus:outline-none sm:text-sm`}
                placeholder="Username (3-30 characters)"
                value={formData.username}
                onChange={handleChange}
              />
              {formErrors.username && (
                <p className="mt-1 text-sm text-red-600">{formErrors.username}</p>
              )}
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address *
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  formErrors.email
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-md focus:outline-none sm:text-sm`}
                placeholder="Email address"
                value={formData.email}
                onChange={handleChange}
              />
              {formErrors.email && (
                <p className="mt-1 text-sm text-red-600">{formErrors.email}</p>
              )}
            </div>

            {/* Optional Fields */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700">
                Phone Number (Optional)
              </label>
              <input
                id="phone"
                name="phone"
                type="tel"
                minLength={10}
                maxLength={20}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  formErrors.phone
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-md focus:outline-none sm:text-sm`}
                placeholder="+1-555-123-4567"
                value={formData.phone}
                onChange={handleChange}
              />
              {formErrors.phone && (
                <p className="mt-1 text-sm text-red-600">{formErrors.phone}</p>
              )}
            </div>

            <div>
              <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700">
                Date of Birth (Optional)
              </label>
              <input
                id="date_of_birth"
                name="date_of_birth"
                type="date"
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  formErrors.date_of_birth
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-md focus:outline-none sm:text-sm`}
                value={formData.date_of_birth}
                onChange={handleChange}
              />
              {formErrors.date_of_birth && (
                <p className="mt-1 text-sm text-red-600">{formErrors.date_of_birth}</p>
              )}
            </div>

            {/* Password Fields */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password *
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                maxLength={128}
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  formErrors.password
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-md focus:outline-none sm:text-sm`}
                placeholder="Password (8-128 characters)"
                value={formData.password}
                onChange={handleChange}
              />
              {formErrors.password && (
                <p className="mt-1 text-sm text-red-600">{formErrors.password}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Password *
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                className={`mt-1 appearance-none relative block w-full px-3 py-2 border ${
                  formErrors.confirmPassword
                    ? 'border-red-300 text-red-900 placeholder-red-300 focus:ring-red-500 focus:border-red-500'
                    : 'border-gray-300 text-gray-900 placeholder-gray-500 focus:ring-indigo-500 focus:border-indigo-500'
                } rounded-md focus:outline-none sm:text-sm`}
                placeholder="Confirm password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
              {formErrors.confirmPassword && (
                <p className="mt-1 text-sm text-red-600">{formErrors.confirmPassword}</p>
              )}
            </div>

            {/* Marketing Consent */}
            <div className="flex items-center">
              <input
                id="marketing_emails_consent"
                name="marketing_emails_consent"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                checked={formData.marketing_emails_consent}
                onChange={handleChange}
              />
              <label htmlFor="marketing_emails_consent" className="ml-2 block text-sm text-gray-900">
                I consent to receive marketing emails
              </label>
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
              {isLoading ? 'Creating account...' : 'Create account'}
            </button>
          </div>

          {/* Switch to Login - Always show */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{' '}
              <button
                type="button"
                onClick={handleSwitchToLogin}
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Sign in here
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;