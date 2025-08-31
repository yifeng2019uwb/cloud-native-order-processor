import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useAssetDetail } from '@/hooks/useInventory';
import AssetCard from './AssetCard';

interface AssetDetailProps {
  assetId: string;
  onBack: () => void;
}

const AssetDetail: React.FC<AssetDetailProps> = ({ assetId, onBack }) => {
  const { isAuthenticated } = useAuth();
  const { asset, loading, error, refetch } = useAssetDetail(assetId);

  // Helper functions for formatting
  const formatCurrency = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A';
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    return `$${value.toLocaleString()}`;
  };

  const formatPercentage = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'N/A';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const getPercentageColor = (value: number | undefined): string => {
    if (value === undefined || value === null) return 'text-gray-500';
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const formatDateTime = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const getAvailabilityColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800';
      case 'limited':
        return 'bg-yellow-100 text-yellow-800';
      case 'out_of_stock':
        return 'bg-red-100 text-red-800';
      case 'unavailable':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getAvailabilityText = (status: string) => {
    switch (status) {
      case 'available':
        return 'Available';
      case 'limited':
        return 'Limited Stock';
      case 'out_of_stock':
        return 'Out of Stock';
      case 'unavailable':
        return 'Unavailable';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading asset details...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error loading asset</h3>
            <p className="mt-1 text-sm text-red-700">{error.message}</p>
          </div>
          <div className="ml-auto pl-3">
            <button
              onClick={refetch}
              className="text-red-400 hover:text-red-600"
            >
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!asset) {
    return (
      <div className="text-center py-12">
        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">Asset not found</h3>
        <p className="mt-1 text-sm text-gray-500">
          The asset you're looking for doesn't exist or has been removed.
        </p>
        <div className="mt-6">
          <button
            onClick={onBack}
            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Back to Assets
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Asset Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-6">
          <div className="flex items-center space-x-6">
            {asset.image && (
              <div className="flex-shrink-0">
                <img
                  src={asset.image}
                  alt={asset.name}
                  className="h-20 w-20 rounded-full"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                  }}
                />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-3">
                <h1 className="text-3xl font-bold text-gray-900">{asset.name}</h1>
                {asset.symbol && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                    {asset.symbol}
                  </span>
                )}
                {asset.market_cap_rank && (
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                    Rank #{asset.market_cap_rank}
                  </span>
                )}
              </div>
              <p className="mt-2 text-lg text-gray-600">
                {formatCurrency(asset.price_usd)} USD
                {asset.price_change_percentage_24h !== undefined && (
                  <span className={`ml-3 ${getPercentageColor(asset.price_change_percentage_24h)}`}>
                    {formatPercentage(asset.price_change_percentage_24h)} (24h)
                  </span>
                )}
              </p>
              {asset.description && (
                <p className="mt-2 text-sm text-gray-500">{asset.description}</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Asset Card */}
      <AssetCard asset={asset} showDetails={true} />

      {/* Detailed Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Asset Details</h3>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Asset ID</dt>
              <dd className="mt-1 text-sm text-gray-900">{asset.asset_id}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Symbol</dt>
              <dd className="mt-1 text-sm text-gray-900">{asset.symbol || 'N/A'}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Name</dt>
              <dd className="mt-1 text-sm text-gray-900">{asset.name}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Market Cap Rank</dt>
              <dd className="mt-1 text-sm text-gray-900">{asset.market_cap_rank || 'N/A'}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Category</dt>
              <dd className="mt-1 text-sm text-gray-900 capitalize">{asset.category}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getAvailabilityColor(asset.availability_status)}`}>
                  {getAvailabilityText(asset.availability_status)}
                </span>
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Active</dt>
              <dd className="mt-1">
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  asset.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {asset.is_active ? 'Yes' : 'No'}
                </span>
              </dd>
            </div>

            {asset.description && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-sm text-gray-900">{asset.description}</dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* Price Information */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Price Information</h3>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Current Price (USD)</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.price_usd)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">24h Change</dt>
              <dd className="mt-1 text-sm">
                <span className={getPercentageColor(asset.price_change_percentage_24h)}>
                  {formatPercentage(asset.price_change_percentage_24h)}
                </span>
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">7d Change</dt>
              <dd className="mt-1 text-sm">
                <span className={getPercentageColor(asset.price_change_percentage_7d)}>
                  {formatPercentage(asset.price_change_percentage_7d)}
                </span>
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">30d Change</dt>
              <dd className="mt-1 text-sm">
                <span className={getPercentageColor(asset.price_change_percentage_30d)}>
                  {formatPercentage(asset.price_change_percentage_30d)}
                </span>
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">24h High</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.high_24h)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">24h Low</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.low_24h)}</dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Market Data */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Market Data</h3>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Market Cap</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.market_cap)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">24h Volume</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.total_volume_24h)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Circulating Supply</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {asset.circulating_supply ? asset.circulating_supply.toLocaleString() : 'N/A'}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Total Supply</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {asset.total_supply ? asset.total_supply.toLocaleString() : 'N/A'}
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Max Supply</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {asset.max_supply ? asset.max_supply.toLocaleString() : 'N/A'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Historical Data */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Historical Data</h3>
        </div>
        <div className="px-6 py-4">
          <dl className="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">All-Time High</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.ath)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">ATH Change</dt>
              <dd className="mt-1 text-sm">
                <span className={getPercentageColor(asset.ath_change_percentage)}>
                  {formatPercentage(asset.ath_change_percentage)}
                </span>
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">ATH Date</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(asset.ath_date)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">All-Time Low</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatCurrency(asset.atl)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">ATL Change</dt>
              <dd className="mt-1 text-sm">
                <span className={getPercentageColor(asset.atl_change_percentage)}>
                  {formatPercentage(asset.atl_change_percentage)}
                </span>
              </dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">ATL Date</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDate(asset.atl_date)}</dd>
            </div>

            <div>
              <dt className="text-sm font-medium text-gray-500">Last Updated</dt>
              <dd className="mt-1 text-sm text-gray-900">{formatDateTime(asset.last_updated)}</dd>
            </div>
          </dl>
        </div>
      </div>

      {/* 7-Day Price Chart */}
      {asset.sparkline_7d?.price && asset.sparkline_7d.price.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">7-Day Price Trend</h3>
          </div>
          <div className="px-6 py-4">
            <div className="h-32 bg-gray-50 rounded-lg flex items-center justify-center">
              <p className="text-sm text-gray-500">
                Chart visualization would go here for {asset.sparkline_7d.price.length} data points
              </p>
            </div>
            <p className="mt-2 text-xs text-gray-500 text-center">
              {asset.sparkline_7d.price.length} price points over the last 7 days
            </p>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-between items-center">
        <button
          onClick={onBack}
          className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Assets
        </button>

        <div className="flex items-center space-x-3">
          {isAuthenticated && asset.is_active && (
            <>
              <Link
                to={`/trading?asset=${asset.asset_id}&action=buy`}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Buy
              </Link>
              <Link
                to={`/trading?asset=${asset.asset_id}&action=sell`}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 12H6" />
                </svg>
                Sell
              </Link>
            </>
          )}

          <button
            onClick={refetch}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>
  );
};

export default AssetDetail;