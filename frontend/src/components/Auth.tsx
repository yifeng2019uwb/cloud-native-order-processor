import React from 'react';

export const Login: React.FC<{ onSwitchToRegister?: () => void }> = ({ onSwitchToRegister }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to your account
          </h2>
        </div>
        <div className="text-center">
          <button
            onClick={onSwitchToRegister}
            className="text-indigo-600 hover:text-indigo-500"
          >
            Don't have an account? Sign up
          </button>
        </div>
      </div>
    </div>
  );
};

export const Register: React.FC<{ onSwitchToLogin?: () => void }> = ({ onSwitchToLogin }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <div className="text-center">
          <button
            onClick={onSwitchToLogin}
            className="text-indigo-600 hover:text-indigo-500"
          >
            Already have an account? Sign in
          </button>
        </div>
      </div>
    </div>
  );
};