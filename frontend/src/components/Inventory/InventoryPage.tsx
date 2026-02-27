import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import AssetList from './AssetList';
import AssetDetail from './AssetDetail';
import type { Asset } from '@/types';

const InventoryPage: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [showDetail, setShowDetail] = useState(false);

  const handleAssetClick = (asset: Asset) => {
    setSelectedAsset(asset);
    setShowDetail(true);
  };

  const handleBackToList = () => {
    setShowDetail(false);
    setSelectedAsset(null);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Market
              </h1>
              <p className="text-sm text-gray-600">
                Browse the market
              </p>
            </div>

            <div className="flex items-center space-x-4">
              {isAuthenticated ? (
                <>
                  <span className="text-sm text-gray-700">
                    Welcome, {user?.first_name} {user?.last_name}!
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
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                  >
                    Login
                  </Link>
                  <Link
                    to="/register"
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                  >
                    Register
                  </Link>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Content Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">Available Assets</h2>
              <p className="mt-2 text-gray-600">
                Browse and explore the market
              </p>
            </div>

            {showDetail && (
              <button
                onClick={handleBackToList}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Assets
              </button>
            )}
          </div>
        </div>

        {/* Content */}
        {showDetail && selectedAsset ? (
          <AssetDetail
            assetId={selectedAsset.asset_id}
            onBack={handleBackToList}
          />
        ) : (
          <AssetList onAssetClick={handleAssetClick} />
        )}
      </div>
    </div>
  );
};

export default InventoryPage;