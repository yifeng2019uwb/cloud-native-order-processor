import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { inventoryApiService } from '@/services/inventoryApi';

const LandingPage: React.FC = () => {
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAssetCount = async () => {
      try {
        // We don't need to store the count, just check if API is working
        await inventoryApiService.listAssets({ active_only: true, limit: undefined });
      } catch (error) {
        console.error('Failed to fetch asset count:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchAssetCount();
  }, []);

  const displayCount = loading ? '...' : '200+';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="text-2xl font-bold text-indigo-600">CNOP</div>
              <div className="ml-2 text-gray-600">Cloud Native Order Processor</div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign In
              </Link>
              <Link
                to="/register"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Sign Up
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 sm:text-5xl">
            🚀 Trade {displayCount} Cryptocurrencies
          </h1>
          <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
            Professional trading platform with real-time market data and secure transactions.
          </p>
          <div className="mt-8 flex justify-center space-x-4">
            <Link
              to="/market"
              className="bg-gray-100 hover:bg-gray-200 text-gray-900 px-6 py-3 rounded-md text-lg font-medium transition-colors"
            >
              Browse Assets
            </Link>
            <Link
              to="/register"
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-md text-lg font-medium transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </div>

      {/* Platform Stats */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600">{displayCount}</div>
            <div className="text-gray-600">Assets Available</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600">Live</div>
            <div className="text-gray-600">Prices from API</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600">Real-time</div>
            <div className="text-gray-600">Market Data</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-600">Professional</div>
            <div className="text-gray-600">APIs</div>
          </div>
        </div>
      </div>

      {/* Platform Features */}
      <div className="bg-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900">🔧 Platform Features</h2>
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="text-2xl mb-2">📊</div>
                <div className="font-medium">Real-time Market Data</div>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">🔐</div>
                <div className="font-medium">Secure Authentication</div>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">⚡</div>
                <div className="font-medium">Professional APIs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl mb-2">☁️</div>
                <div className="font-medium">Cloud-Native Architecture</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer CTA */}
      <div className="bg-indigo-600 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white">Ready to Start Trading?</h2>
          <div className="mt-8">
            <Link
              to="/register"
              className="bg-white hover:bg-gray-100 text-indigo-600 px-8 py-3 rounded-md text-lg font-medium transition-colors"
            >
              Create Account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
