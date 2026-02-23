import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { orderApiService } from '@/services/orderApi';
import { balanceApiService } from '@/services/balanceApi';
import { inventoryApiService } from '@/services/inventoryApi';
import { portfolioApiService } from '@/services/portfolioApi';
import { UI_STRINGS, UI_PATTERNS, formatString, MAX_ORDER_VALUE_USD } from '@/constants/ui';
import type { Asset, Order, CreateOrderRequest, Balance } from '@/types';

const TradingPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [searchParams] = useSearchParams();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [filteredAssets, setFilteredAssets] = useState<Asset[]>([]);
  const [balance, setBalance] = useState<Balance | null>(null);
  const [portfolio, setPortfolio] = useState<any>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [orderForm, setOrderForm] = useState({
    quantity: '',
    orderType: 'market_buy' as 'market_buy' | 'market_sell'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [orderPreview, setOrderPreview] = useState<any>(null);

  const handleLogout = () => {
    logout();
  };

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  // Handle URL parameters for asset and action
  useEffect(() => {
    const assetParam = searchParams.get('asset');
    const actionParam = searchParams.get('action');

    if (assetParam && assets.length > 0) {
      const foundAsset = assets.find(asset => asset.asset_id === assetParam);
      if (foundAsset) {
        setSelectedAsset(foundAsset);
      }
    }

    if (actionParam === 'buy' || actionParam === 'sell') {
      setOrderForm(prev => ({
        ...prev,
        orderType: actionParam === 'buy' ? 'market_buy' : 'market_sell'
      }));
    }
  }, [assets, searchParams]);

  // Update filtered assets when order type changes
  useEffect(() => {
    if (orderForm.orderType === 'market_sell') {
      // For sell orders, only show assets user owns
      const ownedAssets = assets.filter(asset =>
        portfolio?.assets?.some((pa: any) => pa.asset_id === asset.asset_id)
      );
      setFilteredAssets(ownedAssets);
    } else {
      // For buy orders, show all assets
      setFilteredAssets(assets);
    }
  }, [orderForm.orderType, assets, portfolio]);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [assetsRes, balanceRes, portfolioRes, ordersRes] = await Promise.all([
        inventoryApiService.listAssets(),
        balanceApiService.getBalance().catch(() => null),
        portfolioApiService.getPortfolio(user?.username || '').catch(() => null),
        orderApiService.listOrders().catch(() => ({ data: [], has_more: false }))
      ]);

      if (assetsRes.data) {
        // Sort assets alphabetically by name for easier selection
        const sortedAssets = [...assetsRes.data].sort((a, b) =>
          a.name.localeCompare(b.name, undefined, { sensitivity: 'base' })
        );
        setAssets(sortedAssets);
        setFilteredAssets(sortedAssets); // Initialize filtered assets with sorted assets
        // Don't auto-select first asset - let user choose
        setSelectedAsset(null);
      }

      if (balanceRes) {
        // Convert the BalanceResponse to Balance format
        const balanceData = {
          username: '', // Not provided by API
          balance: parseFloat(balanceRes.current_balance),
          currency: 'USD',
          last_updated: balanceRes.updated_at
        };
        setBalance(balanceData);
      }

      if (portfolioRes) {
        setPortfolio(portfolioRes);
      }

      // Backend returns { data, has_more } (no success field); treat any response with data array as success
      if (ordersRes && Array.isArray(ordersRes.data)) {
        setOrders(ordersRes.data);
      } else {
        setOrders([]);
      }
    } catch (err) {
      setError(UI_STRINGS.TRADING_ERROR || 'Failed to load trading data');
      console.error('Trading data load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const calculateOrderPreview = () => {
    if (!selectedAsset || !orderForm.quantity) return null;

    const quantity = parseFloat(orderForm.quantity);
    const price = selectedAsset.price_usd || 0;
    const total = quantity * price;
    const totalValueCheck = total <= MAX_ORDER_VALUE_USD;

    if (orderForm.orderType === 'market_buy') {
      const remainingBalance = (balance?.balance || 0) - total;
      return {
        asset: selectedAsset,
        quantity,
        price,
        total,
        orderType: UI_STRINGS.BUY,
        balanceAfter: remainingBalance,
        balanceCheck: remainingBalance >= 0,
        totalValueCheck
      };
    } else {
      const assetBalance = portfolio?.assets?.find((pa: any) => pa.asset_id === selectedAsset.asset_id);
      const availableQuantity = parseFloat(assetBalance?.quantity?.toString() || '0');
      const remainingQuantity = availableQuantity - quantity;
      return {
        asset: selectedAsset,
        quantity,
        price,
        total,
        orderType: UI_STRINGS.SELL,
        quantityAfter: remainingQuantity,
        quantityCheck: remainingQuantity >= 0,
        totalValueCheck
      };
    }
  };

  const handleOrderSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAsset || !orderForm.quantity) return;

    const preview = calculateOrderPreview();
    if (!preview) return;

    // Check validation
    if (orderForm.orderType === 'market_buy' && !preview.balanceCheck) {
      setError(UI_STRINGS.INSUFFICIENT_BALANCE);
      return;
    }

    if (orderForm.orderType === 'market_sell' && !preview.quantityCheck) {
      setError(UI_STRINGS.INSUFFICIENT_BALANCE);
      return;
    }

    if (!preview.totalValueCheck) {
      setError(UI_STRINGS.ORDER_MAX_VALUE_EXCEEDED);
      return;
    }

    setOrderPreview(preview);
    setShowConfirmation(true);
    setError(null);
  };

  const handleCancelConfirm = () => {
    setShowConfirmation(false);
    setError(null);
  };

  const confirmOrder = async () => {
    if (!selectedAsset || !orderForm.quantity) return;

    try {
      setIsLoading(true);
      // Market orders: omit price (backend uses current market price). Limit orders would require price.
      const orderData: CreateOrderRequest = {
        asset_id: selectedAsset.asset_id,
        quantity: parseFloat(orderForm.quantity),
        ...(orderForm.orderType.startsWith('limit_')
          ? { price: selectedAsset.price_usd || 0 }
          : {}),
        order_type: orderForm.orderType
      };

      await orderApiService.createOrder(orderData);

      // Order created successfully (backend returns { data: Order })
      // Reset form
      setOrderForm({ quantity: '', orderType: 'market_buy' });
      setShowConfirmation(false);
      setOrderPreview(null);

      // Reload data
      await loadData();

      alert(UI_STRINGS.ORDER_SUCCESS);
    } catch (err: any) {
      const msg = err?.message ?? err?.detail ?? UI_STRINGS.ORDER_FAILED;
      setError(msg);
      console.error('Order creation error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const preview = calculateOrderPreview();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{UI_STRINGS.TRADING_TITLE}</h1>
              <p className="text-sm text-gray-600">{UI_STRINGS.TRADING_SUBTITLE}</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
{formatString(UI_STRINGS.WELCOME_USER, { username: user?.username || '' })}
              </span>
              <Link
                to="/dashboard"
                className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
              >
{UI_STRINGS.DASHBOARD}
              </Link>
              <button
                onClick={handleLogout}
                className={UI_PATTERNS.DANGER_BUTTON}
              >
                {UI_STRINGS.LOGOUT}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Balance Display */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-medium text-gray-900">💰 {UI_STRINGS.TOTAL_BALANCE}</h3>
              <p className="text-2xl font-bold text-green-600">
                ${balance?.balance?.toFixed(2) || '0.00'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">{UI_STRINGS.ASSET_HOLDINGS}</p>
              <p className="text-lg font-medium">
                {portfolio?.assets?.length || 0} assets owned
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

            {/* Order Form */}
          <div id="trading-order-form" className="bg-white overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">
                  📝 {UI_STRINGS.CREATE_ORDER || 'Create Order'}
              </h2>
              <p className="text-xs text-gray-500 mb-4">Max order value: ${MAX_ORDER_VALUE_USD.toLocaleString()}</p>

                {error && (
                  <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                    {error}
                  </div>
                )}

                <form onSubmit={handleOrderSubmit} className="space-y-4">
                  {/* Asset Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {UI_STRINGS.ASSET}
                    </label>

                                        {/* Asset Search */}
                    <div className="mb-2">
                      <input
                        type="text"
                        placeholder={orderForm.orderType === 'market_sell' ?
                          "Search assets you own by name or symbol..." :
                          "Search assets by name or symbol..."
                        }
                        className="w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                        onChange={(e) => {
                          const searchTerm = e.target.value.toLowerCase();
                          if (searchTerm) {
                            // For sell orders, only search through assets user owns
                            const assetsToSearch = orderForm.orderType === 'market_sell' ?
                              assets.filter(asset => portfolio?.assets?.some((pa: any) => pa.asset_id === asset.asset_id)) :
                              assets;

                            const filtered = assetsToSearch.filter(asset =>
                              asset.name.toLowerCase().includes(searchTerm) ||
                              asset.asset_id.toLowerCase().includes(searchTerm)
                            );

                            // Smart sorting: exact matches first, then starts with, then by popularity
                            const sortedFiltered = filtered.sort((a, b) => {
                              const aName = a.name.toLowerCase();
                              const aSymbol = a.asset_id.toLowerCase();
                              const bName = b.name.toLowerCase();
                              const bSymbol = b.asset_id.toLowerCase();

                              // Exact matches get highest priority
                              if (aSymbol === searchTerm) return -1;
                              if (bSymbol === searchTerm) return 1;
                              if (aName === searchTerm) return -1;
                              if (bName === searchTerm) return 1;

                              // Starts with matches get second priority
                              if (aSymbol.startsWith(searchTerm)) return -1;
                              if (bSymbol.startsWith(searchTerm)) return 1;
                              if (aName.startsWith(searchTerm)) return -1;
                              if (bName.startsWith(searchTerm)) return 1;

                              // Then sort by market cap rank (popularity) - lower rank = more popular
                              if (a.market_cap_rank && b.market_cap_rank) {
                                return a.market_cap_rank - b.market_cap_rank;
                              }

                              // Finally alphabetical for similar relevance
                              return aName.localeCompare(bName);
                            });

                            setFilteredAssets(sortedFiltered);
                          } else {
                            // For sell orders, only show assets user owns
                            const assetsToShow = orderForm.orderType === 'market_sell' ?
                              assets.filter(asset => portfolio?.assets?.some((pa: any) => pa.asset_id === asset.asset_id)) :
                              assets;
                            setFilteredAssets(assetsToShow);
                          }
                        }}
                      />
                      <div className="text-xs text-gray-500 mt-1">
                        {filteredAssets.length} of {orderForm.orderType === 'market_sell' ?
                          assets.filter(asset => portfolio?.assets?.some((pa: any) => pa.asset_id === asset.asset_id)).length :
                          assets.length
                        } assets
                        {orderForm.orderType === 'market_sell' && (
                          <span className="text-blue-600"> (assets you own)</span>
                        )}
                      </div>

                      {/* Quick Asset Selection from Search Results */}
                      {filteredAssets.length > 0 && filteredAssets.length < assets.length && (
                        <div className="mt-2 space-y-1">
                          {filteredAssets.slice(0, 5).map(asset => (
                            <button
                              key={asset.asset_id}
                              type="button"
                              onClick={() => setSelectedAsset(asset)}
                              className="w-full text-left p-2 text-sm bg-gray-50 hover:bg-gray-100 rounded border border-gray-200 transition-colors"
                            >
                              <div className="font-medium">{asset.name}</div>
                              <div className="text-xs text-gray-500">
                                {asset.asset_id} - ${asset.price_usd?.toFixed(2)}
                                {orderForm.orderType === 'market_sell' && (
                                  <span className="text-blue-600">
                                    {' '}(Own: {portfolio?.assets?.find((pa: any) => pa.asset_id === asset.asset_id)?.quantity || '0'})
                                  </span>
                                )}
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    <select
                      value={selectedAsset?.asset_id || ''}
                      onChange={(e) => {
                        const asset = assets.find(a => a.asset_id === e.target.value);
                        setSelectedAsset(asset || null);
                      }}
                      className="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      required
                    >
                      <option value="">
                        {orderForm.orderType === 'market_sell' ? 'Select an asset you own' : 'Select an asset'}
                      </option>
                      {(filteredAssets || assets).map(asset => (
                        <option key={asset.asset_id} value={asset.asset_id}>
                          {asset.name} ({asset.asset_id}) - ${asset.price_usd?.toFixed(2)}
                          {orderForm.orderType === 'market_sell' && (
                            ` - Own: ${portfolio?.assets?.find((pa: any) => pa.asset_id === asset.asset_id)?.quantity || '0'}`
                          )}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Order Type */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {UI_STRINGS.ORDER_TYPE}
                    </label>
                    <div className="flex space-x-4">
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="market_buy"
                          checked={orderForm.orderType === 'market_buy'}
                          onChange={(e) => {
                            setOrderForm(prev => ({ ...prev, orderType: e.target.value as any }));
                            // Clear selected asset when switching order types
                            setSelectedAsset(null);
                            // Update filtered assets based on new order type
                            if (e.target.value === 'market_buy') {
                              // For buy orders, show all assets
                              setFilteredAssets(assets);
                            } else {
                              // For sell orders, only show assets user owns
                              const ownedAssets = assets.filter(asset =>
                                portfolio?.assets?.some((pa: any) => pa.asset_id === asset.asset_id)
                              );
                              setFilteredAssets(ownedAssets);
                            }
                          }}
                          className="mr-2"
                        />
                        Buy
                      </label>
                      <label className="flex items-center">
                        <input
                          type="radio"
                          value="market_sell"
                          checked={orderForm.orderType === 'market_sell'}
                          onChange={(e) => {
                            setOrderForm(prev => ({ ...prev, orderType: e.target.value as any }));
                            // Clear selected asset when switching order types
                            setSelectedAsset(null);
                            // Update filtered assets based on new order type
                            if (e.target.value === 'market_sell') {
                              // For sell orders, only show assets user owns
                              const ownedAssets = assets.filter(asset =>
                                portfolio?.assets?.some((pa: any) => pa.asset_id === asset.asset_id)
                              );
                              setFilteredAssets(ownedAssets);
                            } else {
                              // For buy orders, show all assets
                              setFilteredAssets(assets);
                            }
                          }}
                          className="mr-2"
                        />
                        Sell
                      </label>
                    </div>
                  </div>

                  {/* Quantity */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quantity
                    </label>
                    <input
                      type="number"
                      step="any"
                      min="0"
                      value={orderForm.quantity}
                      onChange={(e) => setOrderForm(prev => ({ ...prev, quantity: e.target.value }))}
                      className="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                      placeholder="Enter quantity"
                      required
                    />
                  </div>

                  {/* Order Preview */}
                  {preview && selectedAsset && (
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-medium mb-2">Order Preview</h4>
                      <div className="space-y-1 text-sm">
                        <div className="flex justify-between">
                          <span>Asset:</span>
                          <span>{selectedAsset.name}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Price:</span>
                          <span>${preview.price.toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Quantity:</span>
                          <span>{preview.quantity}</span>
                        </div>
                        <div className="flex justify-between font-medium">
                          <span>Total:</span>
                          <span>${preview.total.toFixed(2)}</span>
                        </div>

                                                {orderForm.orderType === 'market_buy' && preview.balanceAfter !== undefined && (
                          <div className={`flex justify-between ${preview.balanceCheck ? 'text-green-600' : 'text-red-600'}`}>
                            <span>Balance After:</span>
                            <span>${preview.balanceAfter.toFixed(2)}</span>
                          </div>
                        )}

                        {orderForm.orderType === 'market_sell' && preview.quantityAfter !== undefined && (
                          <div className={`flex justify-between ${preview.quantityCheck ? 'text-green-600' : 'text-red-600'}`}>
                            <span>Quantity After:</span>
                            <span>{preview.quantityAfter.toFixed(6)}</span>
                          </div>
                        )}

                        <div className={`flex justify-between ${preview.totalValueCheck ? 'text-green-600' : 'text-red-600'}`}>
                          <span>Order Value:</span>
                          <span>${preview.total.toFixed(2)} {!preview.totalValueCheck && '(exceeds max)'}</span>
                        </div>
                      </div>
                    </div>
                  )}

                  <button
                    type="submit"
                    disabled={isLoading || !selectedAsset || !orderForm.quantity}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-3 rounded-md font-medium transition-colors"
                                          >
                          {isLoading ? 'Processing...' : `${orderForm.orderType === 'market_buy' ? 'Buy' : 'Sell'} ${selectedAsset?.asset_id || 'Asset'}`}
                        </button>
                </form>
              </div>
            </div>

            {/* Market Data & Order History */}
            <div className="space-y-6">
              {/* Market Data */}
              {selectedAsset && (
                <div className="bg-white overflow-hidden shadow rounded-lg">
                  <div className="px-4 py-5 sm:p-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      📊 {selectedAsset.asset_id} - {selectedAsset.name}
                    </h3>
                    {/* Quick order buttons at top */}
                    <div className="flex items-center gap-3 mb-4">
                      <span className="text-sm text-gray-500">Quick order:</span>
                      <button
                        type="button"
                        onClick={() => {
                          setOrderForm(prev => ({ ...prev, orderType: 'market_buy' }));
                          setFilteredAssets(assets);
                          document.getElementById('trading-order-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }}
                        className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md ${
                          orderForm.orderType === 'market_buy'
                            ? 'bg-green-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-green-50 hover:text-green-700'
                        }`}
                      >
                        Buy
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setOrderForm(prev => ({ ...prev, orderType: 'market_sell' }));
                          const owned = assets.filter(a => portfolio?.assets?.some((pa: any) => pa.asset_id === a.asset_id));
                          setFilteredAssets(owned);
                          document.getElementById('trading-order-form')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                        }}
                        className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-md ${
                          orderForm.orderType === 'market_sell'
                            ? 'bg-red-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-red-50 hover:text-red-700'
                        }`}
                      >
                        Sell
                      </button>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span>Current Price:</span>
                        <span className="font-medium">${selectedAsset.price_usd?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Category:</span>
                        <span>{selectedAsset.category}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Status:</span>
                        <span className={`px-2 py-1 text-xs rounded-full ${selectedAsset.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {selectedAsset.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </div>
                      {selectedAsset.description && (
                        <div className="flex justify-between">
                          <span>Description:</span>
                          <span className="text-sm text-gray-600">{selectedAsset.description}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

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
                          {(orders || []).slice(0, 5).map(order => (
                            <tr key={order.order_id}>
                              <td className="px-3 py-2 text-sm text-gray-900">{order.asset_id}</td>
                              <td className="px-3 py-2 text-sm">
                                <span className={`px-2 py-1 text-xs rounded-full ${order.order_type.includes('buy') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                  {order.order_type.replace('_', ' ')}
                                </span>
                              </td>
                              <td className="px-3 py-2 text-sm text-gray-900">{order.quantity}</td>
                              <td className="px-3 py-2 text-sm">
                                <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                                  {order.status || 'completed'}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-4">
                      <p className="text-gray-500 mb-2">No orders yet</p>
                      {error && error.includes('log in') && (
                        <p className="text-sm text-blue-600">
                          💡 Orders require authentication - please log in first
                        </p>
                      )}
                    </div>
                  )}
                  <div className="mt-4">
                <Link
                      to="/portfolio"
                  className="text-indigo-600 hover:text-indigo-500 text-sm font-medium"
                >
                      View All Orders →
                </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Order Confirmation Modal */}
      {showConfirmation && orderPreview && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Confirm Order</h3>

              <div className="space-y-2 text-sm text-left mb-6">
                <div className="flex justify-between">
                  <span>Asset:</span>
                  <span className="font-medium">{orderPreview.asset.name}</span>
                </div>
                <div className="flex justify-between">
                  <span>Order Type:</span>
                  <span className="font-medium">{orderPreview.orderType}</span>
                </div>
                <div className="flex justify-between">
                  <span>Quantity:</span>
                  <span className="font-medium">{orderPreview.quantity}</span>
                </div>
                <div className="flex justify-between">
                  <span>Price:</span>
                  <span className="font-medium">${orderPreview.price.toFixed(2)}</span>
                </div>
                <div className="flex justify-between font-medium border-t pt-2">
                  <span>Total:</span>
                  <span>${orderPreview.total.toFixed(2)}</span>
                </div>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
                <p className="text-sm text-yellow-800">
                  ⚠️ This is a market order and will execute immediately at current market price.
                </p>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded text-sm">
                  {error}
                </div>
              )}

              <div className="flex space-x-3">
                <button
                  onClick={handleCancelConfirm}
                  className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md font-medium transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={confirmOrder}
                  disabled={isLoading}
                  className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
                >
                  {isLoading ? 'Processing...' : 'Confirm Order'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TradingPage;
