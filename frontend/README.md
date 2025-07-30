# Order Processor Frontend

A modern React-based frontend application for the Cloud-Native Order Processor system, built with TypeScript, Vite, and Tailwind CSS.

## 🏗️ Architecture Overview

The frontend serves as the user interface for the order processor system, providing:

- **User Authentication**: Login, registration, and profile management
- **Inventory Browsing**: Public asset browsing and details
- **Dashboard**: User dashboard with authenticated features
- **API Integration**: Seamless integration with the Go API Gateway

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend       │
│   (React)       │◄──►│   (Go/Gin)      │◄──►│   Services      │
│   - Auth        │    │   - Auth        │    │   - User        │
│   - Dashboard   │    │   - Proxy       │    │   - Inventory   │
│   - Inventory   │    │   - Security    │    │   - Orders      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Features

### **✅ Authentication System**
- User registration with validation
- Secure login with JWT tokens
- Profile management
- Logout functionality
- Protected route handling

### **✅ Inventory Management**
- Public asset browsing (no auth required)
- Asset details and information
- Search and filtering capabilities
- Responsive design

### **✅ User Dashboard**
- User profile display
- Account management
- Session handling
- Responsive layout

### **✅ API Integration**
- Seamless integration with Go API Gateway
- Automatic token management
- Error handling and retry logic
- Type-safe API calls

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.tsx          # Login component
│   │   │   └── Register.tsx       # Registration component
│   │   ├── Dashboard/
│   │   │   └── Dashboard.tsx      # User dashboard
│   │   └── Inventory/
│   │       ├── AssetCard.tsx      # Asset display card
│   │       ├── AssetDetail.tsx    # Asset details view
│   │       ├── AssetList.tsx      # Asset listing
│   │       └── InventoryPage.tsx  # Main inventory page
│   ├── hooks/
│   │   ├── useAuth.ts             # Authentication hook
│   │   └── useInventory.ts        # Inventory data hook
│   ├── services/
│   │   ├── api.ts                 # Auth API service
│   │   └── inventoryApi.ts        # Inventory API service
│   ├── types/
│   │   ├── auth.ts                # Authentication types
│   │   ├── inventory.ts           # Inventory types
│   │   └── index.ts               # Shared types
│   ├── utils/
│   │   └── auth.ts                # Auth utilities
│   ├── App.tsx                    # Main application component
│   └── main.tsx                   # Application entry point
├── public/                        # Static assets
├── build.sh                       # Build and test script
├── package.json                   # Dependencies and scripts
├── vite.config.ts                 # Vite configuration
├── tailwind.config.js             # Tailwind CSS configuration
└── tsconfig.json                  # TypeScript configuration
```

## 🛠️ Technology Stack

### **Core Framework**
- **React 18**: Modern React with hooks and functional components
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and development server

### **Styling & UI**
- **Tailwind CSS**: Utility-first CSS framework
- **Responsive Design**: Mobile-first approach
- **Modern UI**: Clean and intuitive interface

### **State Management**
- **React Hooks**: useState, useEffect, useContext
- **Custom Hooks**: useAuth, useInventory for data management

### **API Integration**
- **Fetch API**: Modern HTTP client
- **JWT Tokens**: Secure authentication
- **Type-safe APIs**: Full TypeScript integration

## 🚀 Quick Start

### **Prerequisites**
- Node.js 18+
- npm or yarn

### **Installation**
```bash
cd frontend
npm install
```

### **Development**
```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### **Using Build Script**
```bash
# Build and test
./frontend/build.sh

# Build only
./frontend/build.sh --build-only

# Test only
./frontend/build.sh --test-only

# Verbose output
./frontend/build.sh -v
```

## 🔧 Configuration

### **Environment Variables**
```bash
# API Gateway URL (development)
VITE_API_GATEWAY_URL=http://localhost:30000

# API Gateway URL (production)
VITE_API_GATEWAY_URL=https://api.order-processor.com
```

### **Vite Configuration**
The frontend uses Vite with proxy configuration for development:

```typescript
// vite.config.ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:30000',
        changeOrigin: true
      }
    }
  }
})
```

## 🔐 Authentication Flow

### **Registration Process**
1. User fills registration form
2. Frontend validates input
3. API call to `/api/v1/auth/register`
4. JWT token received and stored
5. User redirected to dashboard

### **Login Process**
1. User enters credentials
2. API call to `/api/v1/auth/login`
3. JWT token received and stored
4. User redirected to dashboard

### **Protected Routes**
- Routes requiring authentication are wrapped with auth checks
- JWT tokens are automatically included in API requests
- Expired tokens trigger automatic logout

## 📱 Components

### **Authentication Components**
- **Login**: User login form with validation
- **Register**: User registration with comprehensive validation
- **AuthProvider**: Context provider for authentication state

### **Dashboard Components**
- **Dashboard**: Main user dashboard
- **Profile**: User profile management
- **Navigation**: Responsive navigation menu

### **Inventory Components**
- **AssetList**: Grid/list view of inventory assets
- **AssetCard**: Individual asset display card
- **AssetDetail**: Detailed asset information view
- **InventoryPage**: Main inventory page with filtering

## 🎨 Styling

### **Tailwind CSS**
- Utility-first CSS framework
- Responsive design classes
- Custom color scheme
- Component-based styling

### **Design System**
- Consistent spacing and typography
- Color palette for branding
- Responsive breakpoints
- Accessibility considerations

## 🧪 Testing

### **Unit Tests**
```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Watch mode
npm run test:watch
```

### **Type Checking**
```bash
# TypeScript type checking
npm run type-check
```

### **Linting**
```bash
# ESLint
npm run lint

# ESLint with fixes
npm run lint:fix
```

## 🚀 Deployment

### **Docker Deployment**
```bash
# Build Docker image
docker build -f docker/frontend/Dockerfile -t order-processor-frontend:latest .

# Run container
docker run -p 3000:80 order-processor-frontend:latest
```

### **Kubernetes Deployment**
```bash
# Deploy to Kubernetes
kubectl apply -k kubernetes/dev/

# Port forward for access
kubectl port-forward svc/frontend 30004:80 -n order-processor
```

### **Static Hosting**
The built application can be deployed to any static hosting service:
- AWS S3 + CloudFront
- Netlify
- Vercel
- GitHub Pages

## 🔗 API Integration

### **Authentication API**
```typescript
// Login
POST /api/v1/auth/login
{
  "username": "user",
  "password": "password"
}

// Register
POST /api/v1/auth/register
{
  "username": "user",
  "email": "user@example.com",
  "password": "password",
  "first_name": "John",
  "last_name": "Doe"
}

// Get Profile
GET /api/v1/auth/me
Authorization: Bearer <JWT_TOKEN>

// Logout
POST /api/v1/auth/logout
Authorization: Bearer <JWT_TOKEN>
```

### **Inventory API**
```typescript
// List Assets (Public)
GET /api/v1/inventory/assets?limit=10&offset=0

// Get Asset Details (Public)
GET /api/v1/inventory/assets/{asset_id}
```

## 🐛 Troubleshooting

### **Common Issues**

**Build Failures**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**API Connection Issues**
```bash
# Check if API Gateway is running
curl http://localhost:30000/health

# Verify proxy configuration in vite.config.ts
```

**TypeScript Errors**
```bash
# Run type checking
npm run type-check

# Check for missing types
npm install @types/react @types/react-dom
```

## 📈 Performance

### **Optimizations**
- **Code Splitting**: Automatic route-based code splitting
- **Tree Shaking**: Unused code elimination
- **Image Optimization**: Optimized asset loading
- **Caching**: Browser caching strategies

### **Bundle Analysis**
```bash
# Analyze bundle size
npm run build:analyze
```

## 🔮 Future Enhancements

### **Planned Features**
- **Real-time Updates**: WebSocket integration
- **Advanced Filtering**: Search and filter capabilities
- **Pagination**: Efficient data loading
- **Offline Support**: Service worker implementation

### **Performance Improvements**
- **Lazy Loading**: Component and route lazy loading
- **Virtual Scrolling**: Large list optimization
- **Caching**: Advanced caching strategies
- **PWA**: Progressive Web App features

---

**This frontend provides a modern, responsive, and user-friendly interface for the Order Processor system with comprehensive authentication and inventory management capabilities.** 🚀
