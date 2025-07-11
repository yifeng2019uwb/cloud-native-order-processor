import React from 'react';
import type { Asset } from '@/types';

interface AssetCardProps {
  asset: Asset;
  onClick?: (asset: Asset) => void;
  showDetails?: boolean;
}

const AssetCard: React.FC<AssetCardProps> = ({ asset, onClick, showDetails = false }) => {
  const handleClick = () => {
    if (onClick) {
      onClick(asset);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'major':
        return 'bg-blue-100 text-blue-800';
      case 'altcoin':
        return 'bg-green-100 text-green-800';
      case 'stablecoin':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive
      ? 'bg-green-100 text-green-800'
      : 'bg-red-100 text-red-800';
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 border border-gray-200 hover:shadow-lg transition-shadow duration-200 ${
        onClick ? 'cursor-pointer' : ''
      }`}
      onClick={handleClick}
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">{asset.name}</h3>
          <p className="text-sm text-gray-500">{asset.asset_id}</p>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-gray-900">
            ${asset.price_usd.toLocaleString()}
          </p>
          <p className="text-sm text-gray-500">USD</p>
        </div>
      </div>

      {asset.description && (
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {asset.description}
        </p>
      )}

      <div className="flex flex-wrap gap-2">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(asset.category)}`}>
          {asset.category}
        </span>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(asset.is_active)}`}>
          {asset.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>

      {showDetails && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Asset ID:</span>
              <p className="font-medium">{asset.asset_id}</p>
            </div>
            <div>
              <span className="text-gray-500">Category:</span>
              <p className="font-medium capitalize">{asset.category}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetCard;