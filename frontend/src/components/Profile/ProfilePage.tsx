import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { profileApiService } from '@/services/profileApi';
import { apiService } from '@/services/api';

const ProfilePage: React.FC = () => {
  const { user, logout, refreshProfile } = useAuth();
  const [editMode, setEditMode] = useState(false);
  const [profileData, setProfileData] = useState({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    phone: '',
    marketing_emails_consent: false
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'profile' | 'security'>('profile');

  const handleLogout = () => {
    logout();
  };

  // Fetch fresh profile data from backend when component mounts
  useEffect(() => {
    const fetchProfileData = async () => {
      try {
        setIsLoading(true);
        setError(null);

                // Fetch fresh profile data from the backend
        const profileResponse = await apiService.getProfile();

        if (profileResponse && profileResponse.user) {
          setProfileData({
            username: profileResponse.user.username || '',
            email: profileResponse.user.email || '',
            first_name: profileResponse.user.first_name || '',
            last_name: profileResponse.user.last_name || '',
            phone: profileResponse.user.phone || '',
            marketing_emails_consent: profileResponse.user.marketing_emails_consent || false
          });
        }
      } catch (err) {
        console.error('Failed to fetch profile data:', err);
        setError('Failed to load profile data');

        // Fall back to auth context data if API fails
        if (user) {
          setProfileData({
            username: user.username || '',
            email: user.email || '',
            first_name: user.first_name || '',
            last_name: user.last_name || '',
            phone: user.phone || '',
            marketing_emails_consent: user.marketing_emails_consent || false
          });
        }
      } finally {
        setIsLoading(false);
      }
    };

    fetchProfileData();
  }, []); // Run once when component mounts

  // Also update profile data when user changes (fallback)
  useEffect(() => {
    if (user && !isLoading) {
      setProfileData(prev => ({
        username: user.username || prev.username,
        email: user.email || prev.email,
        first_name: user.first_name || prev.first_name,
        last_name: user.last_name || prev.last_name,
        phone: user.phone || prev.phone,
        marketing_emails_consent: user.marketing_emails_consent || prev.marketing_emails_consent
      }));
    }
  }, [user, isLoading]);

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setIsLoading(true);
      setError(null);
      setSuccessMessage(null);

      // Prepare update data - only send changed fields
      const updateData: any = {};
      if (profileData.first_name !== user?.first_name) {
        updateData.first_name = profileData.first_name;
      }
      if (profileData.last_name !== user?.last_name) {
        updateData.last_name = profileData.last_name;
      }
      if (profileData.email !== user?.email) {
        updateData.email = profileData.email;
      }
      if (profileData.phone !== user?.phone) {
        updateData.phone = profileData.phone;
      }

      // Only make API call if there are changes
      if (Object.keys(updateData).length > 0) {
        const result = await profileApiService.updateProfile(updateData);

        if (result.success) {
          setSuccessMessage(result.message || 'Profile updated successfully!');

          // Refresh the user profile from backend
          await refreshProfile();
        } else {
          throw new Error(result.message || 'Failed to update profile');
        }
      } else {
        setSuccessMessage('No changes to save');
      }

      setEditMode(false);

    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (field: string, value: string | boolean) => {
    setProfileData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const cancelEdit = () => {
    if (user) {
      setProfileData({
        username: user.username || '',
        email: user.email || '',
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        marketing_emails_consent: user.marketing_emails_consent || false
      });
    }
    setEditMode(false);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
              <p className="text-sm text-gray-600">Manage your personal information</p>
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

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">

          {/* Tab Navigation */}
          <div className="bg-white shadow rounded-lg">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex">
                <button
                  onClick={() => setActiveTab('profile')}
                  className={`py-4 px-6 text-sm font-medium border-b-2 ${
                    activeTab === 'profile'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  👤 Profile Information
                </button>
                <button
                  onClick={() => setActiveTab('security')}
                  className={`py-4 px-6 text-sm font-medium border-b-2 ${
                    activeTab === 'security'
                      ? 'border-indigo-500 text-indigo-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  🔒 Security Settings
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

              {activeTab === 'profile' && (
                <div>
                  <div className="flex justify-between items-center mb-6">
                    <h3 className="text-lg font-medium text-gray-900">👤 Profile Information</h3>
                    {!editMode && (
                      <button
                        onClick={() => setEditMode(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
                      >
                        Edit Profile
                      </button>
                    )}
                  </div>

                  <form onSubmit={handleProfileSubmit} className="space-y-6">

                    {/* Personal Details */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-4">Personal Details</h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            First Name
                          </label>
                          <input
                            type="text"
                            value={profileData.first_name}
                            onChange={(e) => handleInputChange('first_name', e.target.value)}
                            disabled={!editMode}
                            className="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:text-gray-600"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Last Name
                          </label>
                          <input
                            type="text"
                            value={profileData.last_name}
                            onChange={(e) => handleInputChange('last_name', e.target.value)}
                            disabled={!editMode}
                            className="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:text-gray-600"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Contact Information */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-4">Contact Information</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Email
                          </label>
                          <input
                            type="email"
                            value={profileData.email}
                            onChange={(e) => handleInputChange('email', e.target.value)}
                            disabled={!editMode}
                            className="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:text-gray-600"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Phone Number
                          </label>
                          <input
                            type="tel"
                            value={profileData.phone}
                            onChange={(e) => handleInputChange('phone', e.target.value)}
                            disabled={!editMode}
                            placeholder="+1-555-123-4567"
                            className="w-full p-3 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 disabled:bg-gray-100 disabled:text-gray-600"
                          />
                        </div>
                      </div>
                    </div>

                    {/* Account Information */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-4">Account Information</h4>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Username
                          </label>
                          <input
                            type="text"
                            value={profileData.username}
                            disabled={true}
                            className="w-full p-3 border border-gray-300 rounded-md bg-gray-100 text-gray-600"
                          />
                          <p className="mt-1 text-xs text-gray-500">Username cannot be changed</p>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">Member Since:</span>
                          <span className="ml-2 font-medium">
                            {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                          </span>
                        </div>
                        <div className="text-sm">
                          <span className="text-gray-600">Last Updated:</span>
                          <span className="ml-2 font-medium">
                            {user?.updated_at ? new Date(user.updated_at).toLocaleDateString() : 'Never'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Preferences */}
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-4">Preferences</h4>
                      <div className="space-y-4">
                        <div className="flex items-center">
                          <input
                            type="checkbox"
                            id="marketing_emails"
                            checked={profileData.marketing_emails_consent}
                            onChange={(e) => handleInputChange('marketing_emails_consent', e.target.checked)}
                            disabled={!editMode}
                            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded disabled:opacity-50"
                          />
                          <label htmlFor="marketing_emails" className="ml-2 text-sm text-gray-700">
                            Receive marketing emails and updates
                          </label>
                        </div>
                      </div>
                    </div>

                    {editMode && (
                      <div className="flex space-x-4">
                        <button
                          type="submit"
                          disabled={isLoading}
                          className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white px-6 py-3 rounded-md font-medium transition-colors"
                        >
                          {isLoading ? 'Saving...' : 'Save Changes'}
                        </button>
                        <button
                          type="button"
                          onClick={cancelEdit}
                          disabled={isLoading}
                          className="bg-gray-300 hover:bg-gray-400 disabled:bg-gray-200 text-gray-800 px-6 py-3 rounded-md font-medium transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    )}
                  </form>
                </div>
              )}

              {activeTab === 'security' && (
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-6">🔒 Security Settings</h3>

                  {/* Feature Not Available Message */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <div className="flex items-center mb-4">
                      <div className="text-2xl mr-3">🚧</div>
                      <h4 className="font-medium text-yellow-900">Password Change Not Available</h4>
                    </div>
                    <p className="text-yellow-800 mb-3">
                      Password change functionality is currently under development. The backend API endpoint for secure password changes has not been implemented yet.
                    </p>
                    <p className="text-sm text-yellow-700">
                      This feature will require current password verification and will be available in a future update.
                    </p>
                  </div>

                  {/* Current Security Information */}
                  <div className="mt-6 bg-blue-50 p-4 rounded-lg">
                    <h4 className="font-medium text-blue-900 mb-2">Current Security Features</h4>
                    <div className="text-sm text-blue-800 space-y-1">
                      <p>• Your account is secured with JWT token authentication</p>
                      <p>• Sessions automatically expire after 24 hours</p>
                      <p>• All API communications are encrypted</p>
                      <p>• Profile updates require authentication</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Navigation Links */}
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Navigation</h3>
            <div className="flex flex-wrap gap-4">
                <Link
                  to="/account"
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                💰 Manage Account
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
                to="/dashboard"
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
              >
                🏠 Dashboard
                </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ProfilePage;
