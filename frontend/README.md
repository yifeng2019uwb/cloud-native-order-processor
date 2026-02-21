# 🎨 Frontend Application

> Modern React-based trading platform frontend with complete authentication, trading, and portfolio management capabilities

## 🚀 Quick Start
- **Prerequisites**: Node.js 18+, npm or yarn
- **Build & Test**: `./build.sh` (builds and runs tests)
- **Run Locally**: `npm run dev`
- **Deploy**: From repo root: `./docker/deploy.sh local deploy` (local) or `./docker/deploy.sh frontend deploy` (dev/AWS), or K8s (see [Docker](../docker/README.md), [Kubernetes](../kubernetes/README.md))
- **Example**: Open http://localhost:3000

## ✨ Key Features
- Complete trading platform with 7 functional pages
- JWT authentication and protected routes
- Real-time portfolio updates and transaction history
- Mobile responsive professional UI
- Seamless API integration with backend services

## 📁 Project Structure
```
frontend/
├── src/
│   ├── components/            # React components
│   │   ├── auth/             # Authentication components
│   │   ├── trading/          # Trading components
│   │   └── portfolio/        # Portfolio components
│   ├── pages/                # Page components
│   │   ├── Login.tsx         # Login page
│   │   ├── Dashboard.tsx     # Dashboard page
│   │   └── Trading.tsx       # Trading page
│   ├── services/             # API services
│   │   └── api.ts            # API client
│   ├── hooks/                # Custom React hooks
│   ├── utils/                # Utility functions
│   └── App.tsx               # Main app component
├── public/                   # Static assets
├── tests/                    # Unit and integration tests
├── docker/                   # Docker configuration
├── build.sh                  # Build and test script
├── dev.sh                    # Development script
└── deploy.sh                 # Deployment script
```

## 🔗 Quick Links
- [Design Documentation](../docs/design-docs/frontend-design.md)
- [Services Overview](../services/README.md)
- [API Gateway](../gateway/README.md)

## 📊 Status
- **Current Status**: ✅ **PRODUCTION READY** - All features implemented and working
- **Last Updated**: February 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and code.