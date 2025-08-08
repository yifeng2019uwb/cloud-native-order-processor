# 🚀 Frontend Sprint Tasks - One Day Implementation

## 🎯 **Goal: Demo-Ready Frontend in One Day**
**Focus**: Get everything working quickly, add tests later
**Priority**: Functionality > Security > Polish > Tests
**Approach**: Copy-paste patterns, minimal customization, rapid implementation

---

## ⚡ **Morning Session (3-4 hours)**

### **1. API Gateway Fix (30 minutes)**
**Priority**: CRITICAL - Must be done first
- [ ] Add Order Service routes (`/api/v1/orders/*`)
- [ ] Add Balance routes (`/api/v1/balance/*`)
- [ ] Add Portfolio routes (`/api/v1/portfolio/*`)
- [ ] Add Asset routes (`/api/v1/assets/*`)
- [ ] Add Profile update route (`PUT /api/v1/auth/profile`)
- [ ] Test all routes through gateway

**Files to modify**: `gateway/internal/api/server.go`

### **2. Project Setup (30 minutes)**
**Priority**: HIGH - Foundation
- [ ] Verify React + TypeScript + Tailwind + Vite setup
- [ ] Install required dependencies (React Query, React Router, etc.)
- [ ] Set up basic project structure
- [ ] Configure API base URL to use gateway

**Files to check**: `frontend/package.json`, `frontend/vite.config.ts`

### **3. Landing Page (1 hour)**
**Priority**: HIGH - Public entry point
- [ ] Create basic landing page with asset showcase
- [ ] Display featured assets from `/api/v1/inventory/assets`
- [ ] Add "Get Started" CTA → Login/Register
- [ ] Basic responsive design (desktop first)

**Components**: `LandingPage`, `FeaturedAssets`, `CallToAction`

### **4. Authentication Page (1 hour)**
**Priority**: HIGH - User entry point
- [ ] Create tabbed login/register interface
- [ ] Implement login form with API integration
- [ ] Implement register form with auto-login
- [ ] Basic form validation
- [ ] Redirect to dashboard on success

**Components**: `AuthPage`, `LoginForm`, `RegisterForm`

### **5. Dashboard (1 hour)**
**Priority**: HIGH - Main user hub
- [ ] Display user account balance from `/api/v1/balance`
- [ ] Show asset balances from `/api/v1/assets/balances`
- [ ] Add quick action buttons (Deposit, Trade, Portfolio, Account)
- [ ] Basic portfolio summary

**Components**: `Dashboard`, `AccountBalance`, `AssetBalancesTable`, `QuickActions`

---

## ⚡ **Afternoon Session (3-4 hours)**

### **6. Trading Page (2 hours)**
**Priority**: HIGH - Core functionality
- [ ] Create order form (asset selector, quantity, order type)
- [ ] Display market data and current prices
- [ ] Implement basic order validation
- [ ] Add simple order confirmation (not complex double-confirmation)
- [ ] Connect to `POST /api/v1/orders`
- [ ] Show order history from `GET /api/v1/orders`

**Components**: `TradingPage`, `OrderForm`, `MarketData`, `OrderHistory`

### **7. Portfolio Page (1 hour)**
**Priority**: MEDIUM - User value
- [ ] Display asset balances with current values
- [ ] Show portfolio summary from `/api/v1/portfolio/{username}`
- [ ] Basic asset transaction history (click to view)
- [ ] Simple modal for transaction details

**Components**: `PortfolioPage`, `PortfolioSummary`, `AssetBalancesTable`, `TransactionModal`

### **8. Account Page (30 minutes)**
**Priority**: MEDIUM - Balance management
- [ ] Display current balance
- [ ] Add deposit/withdraw forms
- [ ] Show transaction history from `/api/v1/balance/transactions`
- [ ] Basic tabbed interface

**Components**: `AccountPage`, `BalanceManager`, `TransactionHistory`

### **9. Basic Routing (30 minutes)**
**Priority**: HIGH - Navigation
- [ ] Set up React Router with protected routes
- [ ] Implement basic route protection (check token)
- [ ] Add navigation between pages
- [ ] Handle logout and redirect

**Components**: `App`, `ProtectedRoute`, `Navigation`

---

## ⚡ **Evening Session (2 hours)**

### **10. API Integration (1 hour)**
**Priority**: HIGH - Make everything work
- [ ] Connect all pages to backend APIs through gateway
- [ ] Implement basic error handling
- [ ] Add loading states for API calls
- [ ] Test all API integrations

**Services**: `apiService`, `authService`, `orderService`, `portfolioService`

### **11. Basic Testing & Polish (1 hour)**
**Priority**: MEDIUM - Demo readiness
- [ ] Manual testing of core user flow
- [ ] Fix any obvious bugs
- [ ] Ensure all pages are accessible
- [ ] Basic responsive design check

**Test Flow**: Register → Login → Dashboard → Trade → Portfolio → Account

---

## 🎯 **Success Criteria**

### **✅ Must Work (Demo-Ready)**
- [ ] All 7 pages implemented and accessible
- [ ] Complete user flow: Register → Login → Dashboard → Trade → Portfolio
- [ ] Real data displayed from all APIs
- [ ] Basic order creation and portfolio viewing
- [ ] Navigation between all pages works
- [ ] No major bugs or broken functionality

### **✅ Nice to Have (If Time Permits)**
- [ ] Basic responsive design
- [ ] Simple loading states
- [ ] Basic error messages
- [ ] Clean UI/UX

### **❌ Skip for Now (Review Later)**
- [ ] Unit tests (add later)
- [ ] Advanced security features (review later)
- [ ] Complex animations
- [ ] Mobile optimization
- [ ] Accessibility compliance
- [ ] Advanced error handling

---

## 🔧 **Implementation Notes**

### **Quick Development Tips**
- **Copy-paste** from existing frontend components where possible
- **Use Tailwind defaults** - minimal custom styling
- **Simple state management** - useState/useEffect, not complex patterns
- **Basic error handling** - console.log for now, proper handling later
- **Focus on functionality** over perfect UI

### **API Integration Pattern**
```typescript
// Simple API call pattern
const fetchData = async () => {
  try {
    const response = await fetch('/api/v1/endpoint', {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    setData(data);
  } catch (error) {
    console.error('API Error:', error);
  }
};
```

### **Route Protection Pattern**
```typescript
// Simple route protection
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/auth" />;
};
```

---

## 📋 **File Structure to Create**

```
frontend/src/
├── components/
│   ├── pages/
│   │   ├── LandingPage.tsx
│   │   ├── AuthPage.tsx
│   │   ├── Dashboard.tsx
│   │   ├── TradingPage.tsx
│   │   ├── PortfolioPage.tsx
│   │   └── AccountPage.tsx
│   ├── common/
│   │   ├── Navigation.tsx
│   │   ├── ProtectedRoute.tsx
│   │   └── Loading.tsx
│   └── features/
│       ├── auth/
│       ├── trading/
│       └── portfolio/
├── services/
│   ├── apiService.ts
│   ├── authService.ts
│   └── orderService.ts
└── App.tsx
```

---

## 🚨 **Critical Dependencies**

### **Must Fix First**
- [ ] API Gateway routes (blocks everything else)
- [ ] Basic authentication flow
- [ ] API integration patterns

### **Can Skip for Now**
- [ ] Advanced security features
- [ ] Complex state management
- [ ] Unit tests
- [ ] Performance optimization

---

## 🎉 **End of Day Goal**

**A working, demo-ready frontend that showcases:**
- ✅ User registration and authentication
- ✅ Account balance and portfolio overview
- ✅ Asset trading (buy/sell orders)
- ✅ Transaction history and portfolio management
- ✅ Real data from all backend APIs

**Ready for demo and later enhancement!** 🚀

---

*Created for: One-day frontend sprint*
*Priority: Functionality over perfection*
*Next: Security review and unit tests (later)*
