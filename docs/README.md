# 📚 Documentation Hub

> Comprehensive documentation for the Cloud Native Order Processor system

## 🎯 Overview

This directory contains all design documentation, guides, and technical specifications for the Cloud Native Order Processor platform.

## 📁 Documentation Structure

### **🏗️ Design Documents**
- `design-docs/` - System architecture and design decisions
  - `system-architecture.md` - High-level system architecture
  - `services-design.md` - Microservices architecture design
  - `gateway-design.md` - API Gateway design decisions
  - `monitoring-design.md` - Monitoring and observability design
  - `kubernetes-design.md` - Kubernetes deployment design
  - `frontend-design.md` - Frontend architecture design

### **📋 Guides**
- `deployment-guide.md` - Complete deployment instructions
- `port-configuration.md` - Port strategy and configuration
- `METRICS.md` - Application metrics (plan + PromQL); single source of truth
- `README_TEMPLATE.md` - Template for creating new documentation

### **🔧 Technical Specifications**
- `logging-standards.md` - Logging format and standards
- `integration-test-design.md` - Testing strategy and implementation
- `iam-redis-setup.md` - IAM and Redis configuration

### **🛡️ Runbooks (Security Ops)**
- `runbooks/failed-login-burst.md` - Incident response: 5 failed logins from same IP (SEC-010); verify → containment (IP block) → evidence → follow-up. Depends on SEC-011 (gateway IP block).

## 🚀 Quick Start

### **For Developers**
- [Deployment Guide](deployment-guide.md) - Setup and run the system
- [Port Configuration](port-configuration.md) - Understand port usage
- [Design Documents](design-docs/) - Technical architecture details

### **For Architects**
- [System Architecture](design-docs/system-architecture.md) - Overall system design
- [Services Design](design-docs/services-design.md) - Microservices architecture
- [Gateway Design](design-docs/gateway-design.md) - API Gateway design

### **For DevOps**
- [Kubernetes Design](design-docs/kubernetes-design.md) - Container orchestration
- [Monitoring Design](design-docs/monitoring-design.md) - Observability stack
- [Metrics](METRICS.md) - Application metrics and PromQL
- [Deployment Guide](deployment-guide.md) - Infrastructure setup
- [Failed-Login Runbook](runbooks/failed-login-burst.md) - Incident response for failed-login burst (SEC-010)

## 🔗 Quick Links

- [Main Project README](../README.md) - Project overview
- [Services Overview](../services/README.md) - Service documentation
- [Metrics](METRICS.md) - Application metrics (plan + PromQL)
- [Quick Start Guide](../QUICK_START.md) - Get started quickly

## 📊 Status

- **Current Status**: ✅ **COMPLETE** - All documentation up to date
- **Last Updated**: Feb 25, 2025

---

**Note**: This documentation hub provides comprehensive information about the system design and implementation. For quick start instructions, see the main project README.