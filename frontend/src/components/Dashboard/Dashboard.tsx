import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { balanceApiService } from '@/services/balanceApi';
import { portfolioApiService } from '@/services/portfolioApi';
import type { Balance } from '@/types';

const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [balance, setBalance] = useState<Balance | null>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);

  const handleLogout = () => {
    logout();
  };

  useEffect(() => {
    if (user?.username) {
      loadDashboardData();
    }
  }, [user]);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const [balanceRes, portfolioRes] = await Promise.all([
        balanceApiService.getBalance().catch(() => null),
        portfolioApiService.getPortfolio(user?.username || '').catch(() => null)
      ]);

      if (balanceRes && typeof balanceRes.current_balance === 'string') {
        setBalance({
          username: user?.username || '',
          balance: parseFloat(balanceRes.current_balance),
          currency: 'USD',
          last_updated: balanceRes.updated_at
        });
      }

      if (portfolioRes) {
        setPortfolio(portfolioRes);
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateTotalAssetValue = () => {
    if (!portfolio?.assets || portfolio.assets.length === 0) return 0;

    // Calculate total using market_value from portfolio API
    return portfolio.assets.reduce((total: number, asset: any) => {
      return total + parseFloat(asset.market_value?.toString() || '0');
    }, 0);
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
          {/* Account Summary */}
          <div className="mb-8">
            <h2 className="text-lg font-medium text-gray-900 mb-4">Account Overview</h2>

            {isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-white overflow-hidden shadow rounded-lg animate-pulse">
                    <div className="p-5">
                      <div className="h-4 bg-gray-200 rounded w-1/2 mb-2"></div>
                      <div className="h-8 bg-gray-200 rounded w-3/4"></div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Account Balance */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="text-2xl">💰</div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Account Balance
                          </dt>
                          <dd className="text-2xl font-bold text-gray-900">
                            ${balance?.balance?.toFixed(2) || '0.00'}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-5 py-3">
                    <div className="text-xs text-gray-500">
                      Last updated: {balance?.last_updated ? new Date(balance.last_updated).toLocaleString() : 'Never'}
                    </div>
                  </div>
                </div>

                {/* Total Asset Value */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="text-2xl">📊</div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Asset Value
                          </dt>
                          <dd className="text-2xl font-bold text-gray-900">
                            ${calculateTotalAssetValue().toFixed(2)}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-5 py-3">
                    <div className="text-xs text-gray-500">
                      {portfolio?.assets?.length || 0} asset{(portfolio?.assets?.length || 0) !== 1 ? 's' : ''} held
                    </div>
                  </div>
                </div>

                {/* Total Portfolio Value */}
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="p-5">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="text-2xl">💎</div>
                      </div>
                      <div className="ml-5 w-0 flex-1">
                        <dl>
                          <dt className="text-sm font-medium text-gray-500 truncate">
                            Total Portfolio
                          </dt>
                          <dd className="text-2xl font-bold text-gray-900">
                            ${((balance?.balance || 0) + calculateTotalAssetValue()).toFixed(2)}
                          </dd>
                        </dl>
                      </div>
                    </div>
                  </div>
                  <div className="bg-gray-50 px-5 py-3">
                    <div className="text-xs text-gray-500">
                      Cash + Assets
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <Link
                  to="/trading"
                  className="border border-gray-200 rounded-lg p-4 text-center hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  <div className="text-2xl text-indigo-600 mb-2">📈</div>
                  <h4 className="text-sm font-medium text-gray-900">Trade</h4>
                  <p className="text-xs text-gray-500 mt-1">Create buy/sell orders</p>
                </Link>

                <Link
                  to="/inventory"
                  className="border border-gray-200 rounded-lg p-4 text-center hover:border-indigo-300 hover:bg-indigo-50 transition-colors"
                >
                  <div className="text-2xl text-indigo-600 mb-2">🏪</div>
                  <h4 className="text-sm font-medium text-gray-900">Inventory</h4>
                  <p className="text-xs text-gray-500 mt-1">Browse available assets</p>
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