import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { useAssetDetail } from '@/hooks/useInventory';

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

  const Row = ({ label, value, className = '' }: { label: string; value: React.ReactNode; className?: string }) => (
    <div className={`flex justify-between gap-2 py-2 ${className}`}>
      <dt className="text-sm text-gray-500 shrink-0">{label}</dt>
      <dd className="text-sm text-gray-900 text-right min-w-0">{value}</dd>
    </div>
  );

  return (
    <div className="bg-white shadow rounded-lg overflow-hidden">
      {/* Header: name, price, actions in one row */}
      <div className="px-6 py-4 border-b border-gray-200 flex flex-wrap items-center gap-4">
        {asset.image && (
          <img
            src={asset.image}
            alt={asset.name}
            className="h-14 w-14 rounded-full shrink-0"
            onError={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
          />
        )}
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-xl font-bold text-gray-900 truncate">{asset.name}</h1>
            {asset.symbol && <span className="text-sm px-2.5 py-1 rounded bg-indigo-100 text-indigo-800">{asset.symbol}</span>}
            {asset.market_cap_rank != null && <span className="text-sm text-gray-500">#{asset.market_cap_rank}</span>}
          </div>
          <p className="text-base text-gray-600 mt-1">
            {formatCurrency(asset.price_usd)}
            {asset.price_change_percentage_24h != null && (
              <span className={`ml-2 ${getPercentageColor(asset.price_change_percentage_24h)}`}>
                {formatPercentage(asset.price_change_percentage_24h)} 24h
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={onBack}
            className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md border border-gray-300 text-gray-700 bg-white hover:bg-gray-50"
          >
            ← Back
          </button>
          {isAuthenticated && asset.is_active && (
            <>
              <Link to={`/trading?asset=${asset.asset_id}&action=buy`} className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700">Buy</Link>
              <Link to={`/trading?asset=${asset.asset_id}&action=sell`} className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700">Sell</Link>
            </>
          )}
          <button onClick={refetch} className="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200">Refresh</button>
        </div>
      </div>

      {/* All info in one grid */}
      <div className="px-6 py-5">
        {asset.description && <p className="text-sm text-gray-500 mb-4 line-clamp-2">{asset.description}</p>}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-0">
          <Row label="Asset ID" value={asset.asset_id} />
          <Row label="Category" value={asset.category} />
          <Row label="Status" value={<span className={`inline-flex px-2 py-1 rounded text-sm font-medium ${getAvailabilityColor(asset.availability_status)}`}>{getAvailabilityText(asset.availability_status)}</span>} />
          <Row label="Active" value={asset.is_active ? 'Yes' : 'No'} />
          <Row label="Price (USD)" value={formatCurrency(asset.price_usd)} />
          <Row label="24h" value={<span className={getPercentageColor(asset.price_change_percentage_24h)}>{formatPercentage(asset.price_change_percentage_24h)}</span>} />
          <Row label="7d" value={<span className={getPercentageColor(asset.price_change_percentage_7d)}>{formatPercentage(asset.price_change_percentage_7d)}</span>} />
          <Row label="30d" value={<span className={getPercentageColor(asset.price_change_percentage_30d)}>{formatPercentage(asset.price_change_percentage_30d)}</span>} />
          <Row label="24h High" value={formatCurrency(asset.high_24h)} />
          <Row label="24h Low" value={formatCurrency(asset.low_24h)} />
          <Row label="Market Cap" value={formatCurrency(asset.market_cap)} />
          <Row label="24h Volume" value={formatCurrency(asset.total_volume_24h)} />
          <Row label="Circ. Supply" value={asset.circulating_supply != null ? asset.circulating_supply.toLocaleString() : 'N/A'} />
          <Row label="Total Supply" value={asset.total_supply != null ? asset.total_supply.toLocaleString() : 'N/A'} />
          <Row label="Max Supply" value={asset.max_supply != null ? asset.max_supply.toLocaleString() : 'N/A'} />
          <Row label="ATH" value={formatCurrency(asset.ath)} />
          <Row label="ATH %" value={<span className={getPercentageColor(asset.ath_change_percentage)}>{formatPercentage(asset.ath_change_percentage)}</span>} />
          <Row label="ATH Date" value={formatDate(asset.ath_date)} />
          <Row label="ATL" value={formatCurrency(asset.atl)} />
          <Row label="ATL %" value={<span className={getPercentageColor(asset.atl_change_percentage)}>{formatPercentage(asset.atl_change_percentage)}</span>} />
          <Row label="ATL Date" value={formatDate(asset.atl_date)} />
          <Row label="Last Updated" value={formatDateTime(asset.last_updated)} className="lg:col-span-2" />
        </div>
        {asset.sparkline_7d?.price && asset.sparkline_7d.price.length > 0 && (
          <div className="mt-5 pt-5 border-t border-gray-200">
            <p className="text-sm text-gray-500 mb-2">7d trend · {asset.sparkline_7d.price.length} points</p>
            <div className="h-24 bg-gray-50 rounded-lg flex items-center justify-center">
              <span className="text-sm text-gray-500">Chart: {asset.sparkline_7d.price.length} price points</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssetDetail;