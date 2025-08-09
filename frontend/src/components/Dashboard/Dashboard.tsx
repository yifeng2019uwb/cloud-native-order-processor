import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500">Loading user data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Order Processor Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user.username}!
              </span>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Quick Actions */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <Link
                  to="/trading"
                  className="border border-gray-200 rounded-lg p-4 text-center hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  <div className="text-2xl text-indigo-600 mb-2">📈</div>
                  <h4 className="text-sm font-medium text-gray-900">Trade</h4>
                  <p className="text-xs text-gray-500 mt-1">Create buy/sell orders</p>
                </Link>

                <Link
                  to="/portfolio"
                  className="border border-gray-200 rounded-lg p-4 text-center hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  <div className="text-2xl text-indigo-600 mb-2">📊</div>
                  <h4 className="text-sm font-medium text-gray-900">Portfolio</h4>
                  <p className="text-xs text-gray-500 mt-1">View asset balances</p>
                </Link>

                <Link
                  to="/account"
                  className="border border-gray-200 rounded-lg p-4 text-center hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  <div className="text-2xl text-indigo-600 mb-2">💰</div>
                  <h4 className="text-sm font-medium text-gray-900">Account</h4>
                  <p className="text-xs text-gray-500 mt-1">Manage balance</p>
                </Link>

                <Link
                  to="/profile"
                  className="border border-gray-200 rounded-lg p-4 text-center hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  <div className="text-2xl text-indigo-600 mb-2">👤</div>
                  <h4 className="text-sm font-medium text-gray-900">Profile</h4>
                  <p className="text-xs text-gray-500 mt-1">Update information</p>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;