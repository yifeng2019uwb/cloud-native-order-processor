# Script Refactor Task - Two-Layer Architecture

## 📋 **Phase 1: Create Component `dev.sh` Scripts**

- [ ] `frontend/dev.sh` - build, test, clean
- [ ] `gateway/dev.sh` - build, test, clean (already exists, may need updates)
- [ ] `services/user_service/dev.sh` - build, test, clean
- [ ] `services/inventory_service/dev.sh` - build, test, clean
- [ ] `services/order_service/dev.sh` - build, test, clean


## 🚀 **Phase 2: Create Root `deploy.sh` Script**

- [ ] Create root `deploy.sh` script
- [ ] Environment support: dev (Docker + Kind) vs prod (EKS)
- [ ] Commands: `./deploy frontend`, `./deploy gateway`, `./deploy services`, `./deploy all`
- [ ] Reuse all component `dev.sh` scripts internally
- [ ] Proper deployment order: infrastructure → monitoring → services → frontend

## 📊 **Phase 3: Monitoring Integration**

- [ ] Built into deployment flow
- [ ] Deployed as part of `deploy all`
- [ ] Uses existing monitoring infrastructure

## 📁 **Files to Create**

### **Component Scripts:**
- [x] `frontend/dev.sh`
- [ ] `gateway/dev.sh` (already exists, may need updates)
- [ ] `services/user_service/dev.sh`
- [ ] `services/inventory_service/dev.sh`
- [ ] `services/order_service/dev.sh`

### **Root Orchestrator:**
- [ ] `deploy.sh` (root level)

### **Shared Utilities:**
- [ ] `scripts/prerequisites-checker.sh` - Move from scripts/shared to scripts
- [ ] `scripts/logging.sh` - Consistent logging functions
- [ ] `scripts/docker-utils.sh` - Docker build/push functions
- [ ] `scripts/k8s-utils.sh` - Kubernetes deployment functions
- [ ] `scripts/config-loader.sh` - Environment/component config loading

## ✅ **Success Criteria**

- [ ] New `dev.sh` scripts work in all components
- [ ] Root `deploy.sh` orchestrates everything correctly
- [ ] Monitoring integration works with `deploy all`
- [ ] Existing scripts untouched - safe parallel operation
- [ ] Simple, consistent interface across all components
