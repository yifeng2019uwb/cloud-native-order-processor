# 🤖 Insights Service

> AI-powered portfolio insights service using LLM (Google Gemini) to analyze user portfolios and provide actionable summaries

## 🚀 Quick Start
- **Prerequisites**: Python 3.11+, pip, virtual environment, Google Gemini API key (`GOOGLE_GEMINI_API_KEY`)
- **Build & Test**: `./dev.sh` (builds and runs unit tests)
- **Deploy**: `./deploy.sh` (deploy to Docker or K8s)
- **Integration Tests**: `./integration_tests/run_all_tests.sh`
- **Example**: `curl http://localhost:8004/health`

## ✨ Key Features
- AI-powered portfolio analysis using Google Gemini LLM
- Portfolio data aggregation from User, Order, and Inventory services
- Real-time insights generation with actionable recommendations
- Comprehensive error handling (timeout, rate limits, API errors)
- Structured logging and monitoring integration

## 📁 Project Structure
```
insights_service/
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── api_info_enum.py             # Service metadata and API paths
│   ├── constants.py                 # Service constants (no hardcoded strings)
│   ├── controllers/                 # API controllers and endpoints
│   │   ├── health.py                # Health check endpoint
│   │   ├── dependencies.py         # Dependency injection
│   │   └── insights/
│   │       └── portfolio_insights.py # Main insights endpoint
│   ├── services/                    # Business logic services
│   │   ├── llm_service.py          # Google Gemini LLM integration
│   │   └── data_aggregator.py      # Portfolio data aggregation
│   └── api_models/                  # API request/response models
│       └── insights/
│           ├── insights_models.py   # API response models
│           └── portfolio_context.py # Internal data models
├── tests/                           # Unit tests
│   ├── controllers/                 # Controller tests
│   ├── services/                    # Service tests
│   ├── api_models/                  # Model validation tests
│   └── test_main.py                 # Application tests
├── requirements.txt                 # Python dependencies
├── setup.py                         # Package configuration
├── pytest.ini                       # Pytest configuration with coverage
├── dev.sh                           # Development script (build, test, run, clean)
└── README.md                        # This file
```

## 🔗 Quick Links
- [Services Overview](../README.md)
- [API Documentation](http://localhost:8004/docs)
- [Common Package](../common/README.md)
- [Design Document](../../docs/design-docs/ai-insights-design.md)

## 📊 Status
- **Current Status**: 🔄 **IN PROGRESS** - Backend complete, deployment & frontend integration pending
- **Last Updated**: January 31, 2026

---

**Note**: This is a focused README for quick start and essential information. For detailed technical information, see the design documents and guides.
