import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/hooks/useAuth';
import Login from '@/components/Auth/Login';
import Register from '@/components/Auth/Register';
import Dashboard from '@/components/Dashboard/Dashboard';
import InventoryPage from '@/components/Inventory/InventoryPage';

// Protected Route Wrapper
interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public Route Wrapper (redirects to dashboard if already authenticated)
interface PublicRouteProps {
  children: React.ReactNode;
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
};

// Auth Navigation Component
const AuthNav: React.FC = () => {
  const [currentView, setCurrentView] = React.useState<'login' | 'register'>('login');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex justify-center pt-8">
        <div className="bg-white rounded-lg shadow-md p-1 inline-flex">
          <button
            onClick={() => setCurrentView('login')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              currentView === 'login'
                ? 'bg-indigo-600 text-white'
                : 'text-gray-700 hover:text-indigo-600'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setCurrentView('register')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              currentView === 'register'
                ? 'bg-indigo-600 text-white'
                : 'text-gray-700 hover:text-indigo-600'
            }`}
          >
            Register
          </button>
        </div>
      </div>

      {currentView === 'login' ? (
        <Login onSwitchToRegister={() => setCurrentView('register')} />
      ) : (
        <Register onSwitchToLogin={() => setCurrentView('login')} />
      )}
    </div>
  );
};

// Main App Routes
const AppRoutes: React.FC = () => {
  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path="/login"
        element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        }
      />
      <Route
        path="/register"
        element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        }
      />
      <Route
        path="/auth"
        element={
          <PublicRoute>
            <AuthNav />
          </PublicRoute>
        }
      />
      <Route
        path="/inventory"
        element={<InventoryPage />}
      />

      {/* Protected Routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />

      {/* Default Redirects */}
      <Route path="/" element={<Navigate to="/inventory" replace />} />
      <Route path="*" element={<Navigate to="/inventory" replace />} />
    </Routes>
  );
};

// Main App Component
const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
};

export default App;