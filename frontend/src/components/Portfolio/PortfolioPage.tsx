import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import AssetTransactionHistory from './AssetTransactionHistory';
import { orderApiService } from '@/services/orderApi';
import { portfolioApiService } from '@/services/portfolioApi';
import type { Order } from '@/types';

const PortfolioPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [portfolio, setPortfolio] = useState<any>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showTransactionHistory, setShowTransactionHistory] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<{ id: string; name: string } | null>(null);

  const handleLogout = () => {
    logout();
  };

  const handleAssetClick = (assetId: string) => {
    setSelectedAsset({ id: assetId, name: assetId }); // Using assetId as name for now
    setShowTransactionHistory(true);
  };

  const handleBackToPortfolio = () => {
    setShowTransactionHistory(false);
    setSelectedAsset(null);
  };

  useEffect(() => {
    loadPortfolioData();
  }, [user]);

  const loadPortfolioData = async () => {
    if (!user?.username) return;

    try {
      setIsLoading(true);
      setError(null);

      console.log('Loading portfolio data for user:', user.username);

      const [portfolioRes, ordersRes] = await Promise.all([
        portfolioApiService.getPortfolio(user.username).catch((err) => {
          console.error('Portfolio API error:', err);
          return null;
        }),
        orderApiService.listOrders().catch(() => ({ success: false, message: '', data: [], has_more: false, timestamp: '' }))
      ]);

      console.log('Portfolio response:', portfolioRes);
      console.log('Orders response:', ordersRes);

      if (portfolioRes) {
        setPortfolio(portfolioRes);
      } else {
        setError('Failed to load portfolio data');
      }

      if (ordersRes.success) {
        setOrders(ordersRes.data);
      }
    } catch (err) {
      setError('Failed to load portfolio data');
      console.error('Portfolio load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const portfolioAssets = portfolio?.assets || [];
  const totalValue = portfolio?.assets?.reduce((sum: number, asset: any) => {
    return sum + (parseFloat(asset.market_value?.toString() || '0'));
  }, 0) || 0;

  console.log('Portfolio state:', portfolio);
  console.log('Portfolio assets:', portfolioAssets);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Portfolio</h1>
              <p className="text-sm text-gray-600">View your asset holdings and performance</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome, {user?.username}!
              </span>
              <Link
                to="/dashboard"
                className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
              >
                Dashboard
              </Link>
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

      {/* Portfolio Summary */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">📊 Portfolio Overview</h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-blue-600">
                ${totalValue.toFixed(2)}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Assets Owned</p>
              <p className="text-2xl font-bold text-gray-900">
                {portfolioAssets?.length || 0}
              </p>
            </div>
          </div>


        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {showTransactionHistory && selectedAsset ? (
            <AssetTransactionHistory
              assetId={selectedAsset.id}
              assetName={selectedAsset.name}
              onBack={handleBackToPortfolio}
            />
          ) : (
            <>
              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  {error}
                </div>
              )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Asset Balances */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    📈 Your Asset Balances
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    Click on any asset to view its transaction history
                  </p>
                </div>

                {portfolioAssets && portfolioAssets.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Current Price</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Market Value</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Allocation</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {(portfolioAssets || []).map((asset: any) => (
                          <tr
                            key={asset.asset_id}
                            className="hover:bg-gray-50 cursor-pointer transition-colors"
                            onClick={() => handleAssetClick(asset.asset_id)}
                          >
                            <td className="px-3 py-2 text-sm">
                              <div>
                                <div className="font-medium text-gray-900">{asset.asset_id}</div>
                              </div>
                            </td>
                            <td className="px-3 py-2 text-sm text-gray-900">
                              {parseFloat(asset.quantity.toString()).toFixed(6)}
                            </td>
                            <td className="px-3 py-2 text-sm text-gray-900">
                              ${parseFloat(asset.current_price.toString()).toFixed(2)}
                            </td>
                            <td className="px-3 py-2 text-sm text-gray-900">
                              ${parseFloat(asset.market_value.toString()).toFixed(2)}
                            </td>
                            <td className="px-3 py-2 text-sm text-gray-900">
                              {parseFloat(asset.percentage.toString()).toFixed(2)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">You don't own any assets yet</p>
                    <Link
                      to="/trading"
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
                    >
                      Start Trading →
                    </Link>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Orders */}
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">
                  📋 Recent Orders
                </h3>

                {orders && orders.length > 0 ? (
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Asset</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Quantity</th>
                          <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {(orders || []).slice(0, 10).map(order => (
                          <tr key={order.order_id}>
                            <td className="px-3 py-2 text-sm text-gray-900">{order.asset_id}</td>
                            <td className="px-3 py-2 text-sm">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                order.order_type.toLowerCase().includes('buy')
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {order.order_type.replace('_', ' ')}
                              </span>
                            </td>
                            <td className="px-3 py-2 text-sm text-gray-900">
                              {order.quantity}
                              <div className="text-gray-500 text-xs">
                                @${parseFloat(order.price).toFixed(2)}
                              </div>
                            </td>
                            <td className="px-3 py-2 text-sm">
                              <span className={`px-2 py-1 text-xs rounded-full ${
                                (order.status || 'completed') === 'completed'
                                  ? 'bg-green-100 text-green-800'
                                  : (order.status || 'completed') === 'pending'
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : (order.status || 'completed') === 'failed'
                                  ? 'bg-red-100 text-red-800'
                                  : (order.status || 'completed') === 'cancelled'
                                  ? 'bg-gray-100 text-gray-700'
                                  : 'bg-green-100 text-green-800' // Default to green for completed
                              }`}>
                                {order.status || 'completed'}
                              </span>
                              <div className="text-gray-500 text-xs">
                                {new Date(order.created_at).toLocaleDateString()}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">No orders yet</p>
                    <Link
                      to="/trading"
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
                    >
                      Create First Order →
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/trading"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                📈 Trade Assets
              </Link>
              <Link
                to="/account"
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                💰 Manage Balance
              </Link>
              <button
                onClick={loadPortfolioData}
                disabled={isLoading}
                className="bg-gray-600 hover:bg-gray-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                {isLoading ? '🔄 Refreshing...' : '🔄 Refresh Data'}
              </button>
            </div>
          </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
};

export default PortfolioPage;