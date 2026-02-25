import React, { useState, useMemo } from 'react';
import { useInventory } from '@/hooks/useInventory';
import type { Asset } from '@/types';

interface AssetListProps {
  onAssetClick?: (asset: Asset) => void;
  showFilters?: boolean;
}

const AssetList: React.FC<AssetListProps> = ({ onAssetClick, showFilters = true }) => {
  const {
    assets,
    loading,
    error,
    totalCount,
    listAssets,
    clearError
  } = useInventory();

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage, setItemsPerPage] = useState(25);

  // Default sort by market cap rank (ascending - rank 1 first)
  const [sortField, setSortField] = useState<'market_cap_rank' | 'name' | 'price_usd' | 'category' | 'market_cap' | 'total_volume_24h' | 'price_change_percentage_24h'>('market_cap_rank');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  const handleRefresh = async () => {
    await listAssets({ active_only: true, limit: undefined });
  };

  const handleSort = (field: 'market_cap_rank' | 'name' | 'price_usd' | 'category' | 'market_cap' | 'total_volume_24h' | 'price_change_percentage_24h') => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      // Default direction for different fields
      if (field === 'market_cap_rank') {
        setSortDirection('asc'); // Rank 1 first
      } else if (field === 'price_change_percentage_24h') {
        setSortDirection('desc'); // Best performers first
      } else {
        setSortDirection('asc');
      }
    }
    setCurrentPage(1); // Reset to first page when sorting changes
  };

  // Sort all assets
  const sortedAssets = useMemo(() => {
    return [...assets].sort((a, b) => {
      let aValue: any = a[sortField];
      let bValue: any = b[sortField];

      // Handle string values
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = bValue.toLowerCase();
      }

      // Handle null/undefined values
      if (aValue == null && bValue == null) return 0;
      if (aValue == null) return sortDirection === 'asc' ? -1 : 1;
      if (bValue == null) return sortDirection === 'asc' ? 1 : -1;

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [assets, sortField, sortDirection]);

  // Paginate sorted assets
  const paginatedAssets = useMemo(() => {
    // If itemsPerPage is 250 (All assets), show all assets
    if (itemsPerPage >= sortedAssets.length) {
      return sortedAssets;
    }
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return sortedAssets.slice(startIndex, endIndex);
  }, [sortedAssets, currentPage, itemsPerPage]);

  // Calculate pagination info
  const totalPages = itemsPerPage >= sortedAssets.length ? 1 : Math.ceil(sortedAssets.length / itemsPerPage);
  const startItem = itemsPerPage >= sortedAssets.length ? 1 : (currentPage - 1) * itemsPerPage + 1;
  const endItem = itemsPerPage >= sortedAssets.length ? sortedAssets.length : Math.min(currentPage * itemsPerPage, sortedAssets.length);

  // Pagination handlers
  const goToPage = (page: number) => {
    setCurrentPage(Math.max(1, Math.min(page, totalPages)));
  };

  const goToNextPage = () => goToPage(currentPage + 1);
  const goToPrevPage = () => goToPage(currentPage - 1);

  // Format large numbers
  const formatNumber = (num: number | undefined): string => {
    if (num === undefined || num === null) return 'N/A';
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `$${(num / 1e3).toFixed(2)}K`;
    return `$${num.toFixed(2)}`;
  };

  // Format percentage change
  const formatPercentageChange = (change: number | undefined): string => {
    if (change === undefined || change === null) return 'N/A';
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  };

  // Get color for percentage change
  const getPercentageColor = (change: number | undefined): string => {
    if (change === undefined || change === null) return 'text-gray-500';
    return change >= 0 ? 'text-green-600' : 'text-red-600';
  };

  if (loading && assets.length === 0) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading assets...</p>
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
            <h3 className="text-sm font-medium text-red-800">Error loading assets</h3>
            <p className="mt-1 text-sm text-red-700">{error.message}</p>
          </div>
          <div className="ml-auto pl-3">
            <button
              onClick={clearError}
              className="text-red-400 hover:text-red-600"
            >
              <span className="sr-only">Dismiss</span>
              <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293-4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with stats and filters */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Assets</h2>
          <p className="text-gray-600">
            Showing {startItem}-{endItem} of {totalCount} assets
            {totalPages > 1 && ` • Page ${currentPage} of ${totalPages}`}
          </p>
        </div>

        <div className="flex items-center gap-3">
          {showFilters && (
            <div className="flex items-center gap-4">
              <select
                value={itemsPerPage}
                onChange={(e) => {
                  setItemsPerPage(parseInt(e.target.value));
                  setCurrentPage(1); // Reset to first page when changing items per page
                }}
                className="rounded-md border-gray-300 text-sm focus:border-indigo-500 focus:ring-indigo-500"
              >
                <option value="10">10 per page</option>
                <option value="25">25 per page</option>
                <option value="50">50 per page</option>
                <option value="100">100 per page</option>
                <option value="250">All assets</option>
              </select>
            </div>
          )}

          <button
            onClick={handleRefresh}
            disabled={loading}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
            ) : (
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            )}
            <span className="ml-2">Refresh</span>
          </button>
        </div>
      </div>

      {/* Assets Table */}
      {assets.length === 0 ? (
        <div className="text-center py-12">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No assets found</h3>
          <p className="mt-1 text-sm text-gray-500">
            {'No assets available.'}
          </p>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('market_cap_rank')}
                      className="flex items-center space-x-1 hover:text-gray-700 transition-colors"
                    >
                      <span>Rank</span>
                      {sortField === 'market_cap_rank' && (
                        <svg className={`h-3 w-3 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider min-w-[200px] max-w-[300px]">
                    <button
                      onClick={() => handleSort('name')}
                      className="flex items-center space-x-1 hover:text-gray-700 transition-colors"
                    >
                      <span>Asset</span>
                      {sortField === 'name' && (
                        <svg className={`h-3 w-3 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293-4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('price_usd')}
                      className="flex items-center space-x-1 hover:text-gray-700 transition-colors"
                    >
                      <span>Price (USD)</span>
                      {sortField === 'price_usd' && (
                        <svg className={`h-3 w-3 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('price_change_percentage_24h')}
                      className="flex items-center space-x-1 hover:text-gray-700 transition-colors"
                    >
                      <span>24h Change</span>
                      {sortField === 'price_change_percentage_24h' && (
                        <svg className={`h-3 w-3 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('market_cap')}
                      className="flex items-center space-x-1 hover:text-gray-700 transition-colors"
                    >
                      <span>Market Cap</span>
                      {sortField === 'market_cap' && (
                        <svg className={`h-3 w-3 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </th>
                  <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    <button
                      onClick={() => handleSort('total_volume_24h')}
                      className="flex items-center space-x-1 hover:text-gray-700 transition-colors"
                    >
                      <span>Volume (24h)</span>
                      {sortField === 'total_volume_24h' && (
                        <svg className={`h-3 w-3 ${sortDirection === 'desc' ? 'transform rotate-180' : ''}`} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293-4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      )}
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedAssets.map((asset) => (
                  <tr
                    key={asset.asset_id}
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => onAssetClick?.(asset)}
                  >
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {asset.market_cap_rank || 'N/A'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="flex items-center min-w-0">
                        <div className="flex-shrink-0 h-8 w-8">
                          {asset.image ? (
                            <img
                              src={asset.image}
                              alt={asset.name}
                              className="h-8 w-8 rounded-full"
                              onError={(e) => {
                                // Fallback to initials if image fails to load
                                const target = e.target as HTMLImageElement;
                                target.style.display = 'none';
                                target.nextElementSibling?.classList.remove('hidden');
                              }}
                            />
                          ) : null}
                          <div className={`h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center ${asset.image ? 'hidden' : ''}`}>
                            <span className="text-xs font-medium text-indigo-600">
                              {asset.symbol?.substring(0, 2).toUpperCase() || asset.name.substring(0, 2).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="ml-3 min-w-0 flex-1">
                          <div className="text-sm font-medium text-gray-900 truncate" title={asset.name}>
                            {asset.name}
                          </div>
                          <div className="text-sm text-gray-500 truncate" title={asset.symbol || asset.asset_id}>
                            {asset.symbol || asset.asset_id}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      ${asset.price_usd?.toFixed(2) || 'N/A'}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <span className={getPercentageColor(asset.price_change_percentage_24h)}>
                        {formatPercentageChange(asset.price_change_percentage_24h)}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(asset.market_cap)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatNumber(asset.total_volume_24h)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between border-t border-gray-200 bg-white px-4 py-3 sm:px-6">
          <div className="flex flex-1 justify-between sm:hidden">
            <button
              onClick={goToPrevPage}
              disabled={currentPage === 1}
              className="relative inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Previous
            </button>
            <button
              onClick={goToNextPage}
              disabled={currentPage === totalPages}
              className="relative ml-3 inline-flex items-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Next
            </button>
          </div>
          <div className="hidden sm:flex sm:flex-1 sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-gray-700">
                Showing <span className="font-medium">{startItem}</span> to <span className="font-medium">{endItem}</span> of{' '}
                <span className="font-medium">{totalCount}</span> results
              </p>
            </div>
            <div>
              <nav className="isolate inline-flex -space-x-px rounded-md shadow-sm" aria-label="Pagination">
                <button
                  onClick={goToPrevPage}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center rounded-l-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                >
                  <span className="sr-only">Previous</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M12.79 5.23a.75.75 0 01-.02 1.06L8.83 10l3.93 3.71a.75.75 0 11-1.04 1.08l-4.5-4.25a.75.75 0 010-1.06l4.5-4.25a.75.75 0 011.06.02z" clipRule="evenodd" />
                  </svg>
                </button>
                {/* Current Page */}
                <button
                  onClick={() => goToPage(currentPage)}
                  aria-current="page"
                  className="relative z-10 inline-flex items-center bg-indigo-600 px-4 py-2 text-sm font-semibold text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
                >
                  {currentPage}
                </button>
                {/* Next Page */}
                <button
                  onClick={goToNextPage}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center rounded-r-md px-2 py-2 text-gray-400 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 focus:z-20 focus:outline-offset-0"
                >
                  <span className="sr-only">Next</span>
                  <svg className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                    <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.17 10 7.24 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.06l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                  </svg>
                </button>
              </nav>
            </div>
          </div>
        </div>
      )}

      {/* Loading overlay for refresh */}
      {loading && assets.length > 0 && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-600">Refreshing...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AssetList;