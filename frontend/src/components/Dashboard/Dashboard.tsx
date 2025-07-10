import React from 'react';
import { useAuth } from '@/hooks/useAuth';

const Dashboard: React.FC = () => {
  const { user, logout, refreshProfile } = useAuth();

  const handleLogout = () => {
    logout();
  };

  const handleRefreshProfile = () => {
    refreshProfile();
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
                Welcome, {user.first_name} {user.last_name}!
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
          {/* User Profile Card */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-medium text-gray-900">
                  User Profile
                </h2>
                <button
                  onClick={handleRefreshProfile}
                  className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                >
                  Refresh
                </button>
              </div>

              <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Username
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user.username}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Full Name
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user.first_name} {user.last_name}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Email Address
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user.email}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Phone Number
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user.phone || 'Not provided'}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Date of Birth
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user.date_of_birth
                      ? new Date(user.date_of_birth).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })
                      : 'Not provided'
                    }
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Marketing Emails
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {user.marketing_emails_consent ? 'Subscribed' : 'Not subscribed'}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Member Since
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(user.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </dd>
                </div>

                <div>
                  <dt className="text-sm font-medium text-gray-500">
                    Last Updated
                  </dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(user.updated_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="border border-gray-200 rounded-lg p-4 text-center">
                  <div className="text-2xl text-gray-400 mb-2">📦</div>
                  <h4 className="text-sm font-medium text-gray-900">Orders</h4>
                  <p className="text-xs text-gray-500 mt-1">Manage your orders</p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4 text-center">
                  <div className="text-2xl text-gray-400 mb-2">👤</div>
                  <h4 className="text-sm font-medium text-gray-900">Profile</h4>
                  <p className="text-xs text-gray-500 mt-1">Update your information</p>
                </div>

                <div className="border border-gray-200 rounded-lg p-4 text-center">
                  <div className="text-2xl text-gray-400 mb-2">⚙️</div>
                  <h4 className="text-sm font-medium text-gray-900">Settings</h4>
                  <p className="text-xs text-gray-500 mt-1">Account preferences</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;