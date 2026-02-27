import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { balanceApiService } from '@/services/balanceApi';
import type { Balance, BalanceTransaction } from '@/types';

const AccountPage: React.FC = () => {
  const { user, logout } = useAuth();
  const [balance, setBalance] = useState<Balance | null>(null);
  const [transactions, setTransactions] = useState<BalanceTransaction[]>([]);
  const [activeTab, setActiveTab] = useState<'balance' | 'history'>('balance');
  const [depositAmount, setDepositAmount] = useState('');
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleLogout = () => {
    logout();
  };

  // Load balance and transaction data
  useEffect(() => {
    loadAccountData();
  }, []);

  const loadAccountData = async () => {
    try {
      setIsLoading(true);
      const [balanceRes, transactionsRes] = await Promise.all([
        balanceApiService.getBalance().catch(() => null),
        balanceApiService.getTransactions().catch(() => ({ transactions: [], total_count: 0 }))
      ]);

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

      if (transactionsRes && transactionsRes.transactions) {
        // Sort transactions by date in descending order (most recent first)
        const sortedTransactions = [...transactionsRes.transactions].sort((a, b) =>
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setTransactions(sortedTransactions);
      }
    } catch (err) {
      setError('Failed to load account data');
      console.error('Account data load error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!depositAmount || parseFloat(depositAmount) <= 0) {
      setError('Please enter a valid deposit amount');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setSuccessMessage(null);

      const result = await balanceApiService.deposit({
        amount: parseFloat(depositAmount),
        description: 'Manual deposit'
      });

      if (result.success) {
        setSuccessMessage(`Successfully deposited $${depositAmount}`);
        setDepositAmount('');
        await loadAccountData();
      }
    } catch (err: any) {
      setError(err?.message ?? err?.detail ?? 'Failed to process deposit');
    } finally {
      setIsLoading(false);
    }
  };

  const handleWithdraw = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!withdrawAmount || parseFloat(withdrawAmount) <= 0) {
      setError('Please enter a valid withdrawal amount');
      return;
    }

    const amount = parseFloat(withdrawAmount);
    if (amount > (balance?.balance || 0)) {
      setError('Insufficient balance for withdrawal');
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      setSuccessMessage(null);

      const result = await balanceApiService.withdraw({
        amount,
        description: 'Manual withdrawal'
      });

      if (result.success) {
        setSuccessMessage(`Successfully withdrew $${withdrawAmount}`);
        setWithdrawAmount('');
        await loadAccountData();
      }
    } catch (err: any) {
      setError(err?.message ?? err?.detail ?? 'Failed to process withdrawal');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Account</h1>
              <p className="text-sm text-gray-600">Manage your balance and transactions</p>
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

      {/* Balance Display */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="text-center">
            <h2 className="text-lg font-medium text-gray-900 mb-2">💰 Current Balance</h2>
            <p className="text-4xl font-bold text-green-600">
              ${balance?.balance?.toFixed(2) || '0.00'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Last Updated: {balance?.last_updated ? new Date(balance.last_updated).toLocaleString() : 'Never'}
            </p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">

          {/* Tab Navigation */}
          <div className="bg-white shadow rounded-lg">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                <button
                  onClick={() => setActiveTab('balance')}
                  className={`py-4 px-6 text-sm font-medium border-b-2 ${
                    activeTab === 'balance'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  💰 Balance Management
                </button>
                <button
                  onClick={() => setActiveTab('history')}
                  className={`py-4 px-6 text-sm font-medium border-b-2 ${
                    activeTab === 'history'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  📋 Transaction History
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {error && (
                <div className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
                  {error}
                </div>
              )}

              {successMessage && (
                <div className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded">
                  {successMessage}
                </div>
              )}

              {activeTab === 'balance' && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                    {/* Deposit Form */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">💵 Deposit Funds</h3>
                      <p className="text-xs text-gray-500 mb-3">Daily limit: $10,000</p>
                      <form onSubmit={handleDeposit} className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Amount
                          </label>
                          <div className="relative">
                            <span className="absolute left-3 top-3 text-gray-500">$</span>
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              value={depositAmount}
                              onChange={(e) => setDepositAmount(e.target.value)}
                              className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                              placeholder="0.00"
                              required
                            />
                          </div>
                        </div>
                        <button
                          type="submit"
                          disabled={isLoading || !depositAmount}
                          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-3 rounded-md font-medium transition-colors"
                        >
                          {isLoading ? 'Processing...' : 'Deposit'}
                        </button>
                      </form>
                    </div>

                    {/* Withdraw Form */}
                    <div className="bg-gray-50 p-6 rounded-lg">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">💸 Withdraw Funds</h3>
                      <p className="text-xs text-gray-500 mb-3">Daily limit: $5,000</p>
                      <form onSubmit={handleWithdraw} className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Amount
                          </label>
                          <div className="relative">
                            <span className="absolute left-3 top-3 text-gray-500">$</span>
                            <input
                              type="number"
                              step="0.01"
                              min="0"
                              max={balance?.balance || 0}
                              value={withdrawAmount}
                              onChange={(e) => setWithdrawAmount(e.target.value)}
                              className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
                              placeholder="0.00"
                              required
                            />
                          </div>
                          <p className="mt-1 text-xs text-gray-500">
                            Available: ${balance?.balance?.toFixed(2) || '0.00'}
                          </p>
                        </div>
                        <button
                          type="submit"
                          disabled={isLoading || !withdrawAmount || parseFloat(withdrawAmount) > (balance?.balance || 0)}
                          className="w-full bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white px-4 py-3 rounded-md font-medium transition-colors"
                        >
                          {isLoading ? 'Processing...' : 'Withdraw'}
                        </button>
                      </form>
                    </div>
                  </div>

                  {/* Quick Actions */}
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Quick Actions</h4>
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => setDepositAmount('100')}
                        className="px-3 py-1 bg-blue-200 text-blue-800 rounded text-sm hover:bg-blue-300 transition-colors"
                      >
                        +$100
                      </button>
                      <button
                        onClick={() => setDepositAmount('500')}
                        className="px-3 py-1 bg-blue-200 text-blue-800 rounded text-sm hover:bg-blue-300 transition-colors"
                      >
                        +$500
                      </button>
                      <button
                        onClick={() => setDepositAmount('1000')}
                        className="px-3 py-1 bg-blue-200 text-blue-800 rounded text-sm hover:bg-blue-300 transition-colors"
                      >
                        +$1,000
                      </button>
                      <button
                        onClick={() => setWithdrawAmount('100')}
                        className="px-3 py-1 bg-orange-200 text-orange-800 rounded text-sm hover:bg-orange-300 transition-colors"
                      >
                        -$100
                      </button>
                      <button
                        onClick={() => setWithdrawAmount((balance?.balance || 0).toString())}
                        className="px-3 py-1 bg-red-200 text-red-800 rounded text-sm hover:bg-red-300 transition-colors"
                      >
                        Withdraw All
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'history' && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">📋 Account Balance History</h3>

                  {transactions.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {transactions.map(transaction => (
                            <tr key={transaction.transaction_id}>
                              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                {new Date(transaction.created_at).toLocaleDateString()}
                                <div className="text-xs text-gray-500">
                                  {new Date(transaction.created_at).toLocaleTimeString()}
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                                  transaction.transaction_type === 'deposit' ? 'bg-green-100 text-green-800' :
                                  transaction.transaction_type === 'withdraw' ? 'bg-red-100 text-red-800' :
                                  transaction.transaction_type === 'order_debit' ? 'bg-orange-100 text-orange-800' :
                                  'bg-blue-100 text-blue-800'
                                }`}>
                                  {transaction.transaction_type.replace('_', ' ')}
                                </span>
                              </td>
                              <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${
                                transaction.transaction_type === 'deposit' || transaction.transaction_type === 'order_credit'
                                  ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {transaction.transaction_type === 'deposit' || transaction.transaction_type === 'order_credit' ? '+' : ''}
                                ${Math.abs(parseFloat(transaction.amount)).toFixed(2)}
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-sm">
                                <span className={`px-2 py-1 text-xs rounded-full font-medium ${
                                  transaction.status === 'completed' ? 'bg-green-100 text-green-800' :
                                  transaction.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                  'bg-red-100 text-red-800'
                                }`}>
                                  {transaction.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <p className="text-gray-500 mb-4">No transactions yet</p>
                      <button
                        onClick={() => setActiveTab('balance')}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
                      >
                        Make Your First Transaction →
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Navigation Links */}
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Navigation</h3>
            <p className="text-sm text-gray-600 mb-3">
              Go to <strong>Market</strong> to view all assets and choose one to trade or research. Use <strong>Start Trading</strong> to place buy/sell orders.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link
                to="/market"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                📋 Market — view all assets
              </Link>
              <Link
                to="/trading"
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                📈 Start Trading
              </Link>
              <Link
                to="/portfolio"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                📊 View Portfolio
              </Link>
                <Link
                  to="/profile"
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
                >
                👤 Manage Profile
                </Link>
              <button
                onClick={loadAccountData}
                disabled={isLoading}
                className="bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                {isLoading ? '🔄 Refreshing...' : '🔄 Refresh Data'}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AccountPage;
