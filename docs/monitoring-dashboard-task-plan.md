# Monitoring Dashboard Implementation Task Plan

**Date**: 2025-10-30
**Task**: MON-001 - Comprehensive Monitoring Dashboards
**Goal**: Enable Grafana dashboard to show service health, request metrics, and logs
**Deployment**: Docker Compose only (Kubernetes deployment not included)

---

## Current State Analysis

### ✅ What's Already Working

1. **Grafana**: Running but port conflict issue
   - **PORT CONFLICT**: Frontend uses port 3000 (host), Grafana currently also configured for 3000 (host)
   - **CORRECT PORT**: Grafana should use port 3001 (host) to avoid conflict with Frontend
   - **ACTION NEEDED**: Change Grafana host port mapping from "3000:3000" to "3001:3000" in docker-compose.logs.yml
   - Loki datasource configured
   - Admin user: admin/admin123

2. **Loki**: Log aggregation system running (port 3100)
   - 30-day retention configured

3. **Promtail**: Log collector running
   - Docker container discovery enabled
   - JSON log parsing configured

4. **Services Expose Metrics**: All services have `/metrics` endpoints
   - Gateway: `http://order-processor-gateway:8080/metrics`
   - Auth Service: `http://order-processor-auth_service:8003/metrics`
   - User Service: `http://order-processor-user_service:8000/metrics`
   - Inventory Service: `http://order-processor-inventory_service:8001/metrics`
   - Order Service: `http://order-processor-order_service:8002/metrics`

5. **Services Generate Logs**: All services use BaseLogger
   - Log format: JSON structured logging
   - Log location (in container): `logs/services/{service_name}/{service_name}.log`
   - Services write logs to stdout (Docker) AND files (for Promtail)

### ❌ What's Missing

1. **Prometheus Server**: Not running in docker-compose
   - No metrics collection happening
   - Grafana has no metrics datasource

2. **Prometheus Configuration**: No scrape config exists
   - Need to configure scraping of 5 services + Gateway

3. **Prometheus Datasource**: Not configured in Grafana
   - Only Loki datasource exists

4. **Network Connectivity**: Prometheus needs access to `order-processor-network`
   - Currently monitoring stack is on separate `monitoring` network

5. **Log Collection Path Mismatch**:
   - Promtail expects: `/var/log/services/*/logs/*.log`
   - Services write to: `logs/services/{service_name}/{service_name}.log` (inside container)
   - Promtail config mounts: `../services:/var/log/services:ro`
   - **Issue**: Services write logs inside container, but Promtail looks at host filesystem

6. **No Dashboards**: No Grafana dashboard JSON files exist

---

## Root Cause Analysis

### Why No Data in Grafana?

**Metrics Issue:**
- Prometheus server not running → No metrics collection → Nothing to display

**Logs Issue:**
- Promtail configuration expects logs at `/var/log/services/*/logs/*.log` on host
- Services write logs inside containers at `logs/services/{service_name}/{service_name}.log`
- Promtail uses Docker SD (service discovery) which should collect container stdout logs, but may not be working correctly

**Both Issues:**
- No dashboards configured to display data even if it existed

---

## Solution Design

### Option 1: Use Docker Container Logs (Recommended for Personal Project)

**Approach:**
- Services already log to stdout (Docker containers)
- Promtail already configured with Docker service discovery (`docker_sd_configs`)
- This should work automatically, but needs verification

**Pros:**
- Simplest - no volume mounting needed
- Works immediately if Docker SD is configured correctly
- No filesystem permissions issues

**Cons:**
- Less control over log retention
- Requires Docker socket access (already configured)

### Option 2: Mount Log Volumes

**Approach:**
- Mount log directories from containers to host
- Update Promtail to read from mounted volumes

**Pros:**
- Better control over log files
- Can verify logs are written

**Cons:**
- More complex volume setup
- Need to ensure containers write to mounted paths

**Recommendation**: Start with Option 1 (Docker SD), verify it works, then consider Option 2 if needed.

---

## Implementation Plan

### Phase 1: Add Prometheus for Metrics Collection

#### Step 1.1: Fix Grafana Port Conflict
- Change Grafana port mapping from "3000:3000" to "3001:3000" in docker-compose.logs.yml
- Host port 3001 avoids conflict with Frontend (port 3000)
- Container port remains 3000 (Grafana's default)
- Update all documentation references

#### Step 1.2: Add Prometheus to docker-compose.logs.yml
- Add Prometheus service definition
- Configure network access to `order-processor-network`
- Mount Prometheus config directory
- Expose port 9090 (host:container - standard Prometheus port)

#### Step 1.3: Create Prometheus Configuration
- Create `monitoring/prometheus/prometheus.yml`
- Configure scrape jobs for all 6 services:
  - Gateway (8080)
  - Auth Service (8003)
  - User Service (8000)
  - Inventory Service (8001)
  - Order Service (8002)
- Set scrape interval: 15s (reasonable for personal project)
- Add service labels for filtering

#### Step 1.4: Add Prometheus Datasource to Grafana
- Create `monitoring/grafana/provisioning/datasources/prometheus.yml`
- Configure Prometheus URL: `http://prometheus:9090`
- Set as non-default (Loki remains default)

**Dependencies**: Services must be running for Prometheus to scrape

---

### Phase 2: Verify and Fix Log Collection

#### Step 2.1: Verify Current Log Collection
- Check if Promtail is collecting logs via Docker SD
- Test Loki queries in Grafana Explore:
  - Query: `{container_name=~".*order-processor.*"}`
  - Check if logs appear

#### Step 2.2: Fix Log Collection (If Needed)

**If Docker SD Not Working:**
- Option A: Fix Promtail Docker SD configuration
- Option B: Add volume mounts for log files (Option 2 approach)
- Update Promtail config to match actual log paths

**If Working:**
- Verify log labels (service, level, etc.) are extracted correctly
- Test LogQL queries in Grafana

**Dependencies**: Services must be running and generating logs

---

### Phase 3: Create Unified Dashboard

#### Step 3.1: Design Dashboard Layout

**Single Dashboard Structure:**
1. **Top Section**: Service Health Overview (Panels from Prometheus)
   - Health status indicators (up/down) for all services
   - Last health check time

2. **Metrics Section**: Request Metrics (Panels from Prometheus)
   - Request rate per minute/hour (all services)
   - Request rate breakdown by service
   - Error rate per service
   - Response time (P50, P95, P99) per service

3. **Logs Section**: Service Logs (Panels from Loki)
   - Log viewer with service filter dropdown
   - Log level filter (INFO, WARN, ERROR)
   - Time range selector
   - Search/filter by keyword
   - Log table showing: timestamp, service, level, message

#### Step 3.2: Create Dashboard JSON

**File**: `monitoring/grafana/dashboards/services-overview.json`

**Key Panels:**
- Service Health (Stat panels) - Prometheus query: `up{job="gateway"}` etc.
- Request Rate (Time series) - Prometheus: `rate(gateway_http_requests_total[5m])`
- Error Rate (Time series) - Prometheus: `rate(gateway_http_requests_total{status_code=~"5.."}[5m])`
- Service Logs (Logs panel) - Loki: `{service="gateway"}` with variables

**Variables for Filtering:**
- `$service`: Dropdown (gateway, auth_service, user_service, inventory_service, order_service)
- `$log_level`: Dropdown (INFO, WARN, ERROR)
- `$time_range`: Time range selector

#### Step 3.3: Configure Dashboard Provisioning

**File**: `monitoring/grafana/provisioning/dashboards/dashboards.yml`
- Enable automatic dashboard loading
- Point to dashboard directory

**Update docker-compose.logs.yml:**
- Add dashboard volume mount to Grafana service

---

### Phase 4: Testing and Verification

#### Step 4.1: Start Services and Monitoring Stack
```bash
# Start services
cd docker && docker-compose up -d

# Start monitoring
cd monitoring && docker-compose -f docker-compose.logs.yml up -d
```

#### Step 4.2: Verify Prometheus Scraping
- Access Prometheus UI: http://localhost:9090
- Check Status → Targets
- Verify all 6 services show as "UP"
- Test queries:
  - `up{job="gateway"}`
  - `rate(gateway_http_requests_total[5m])`

#### Step 4.3: Verify Loki Log Collection
- Access Grafana: http://localhost:3001 (matches port-configuration.md)
- Go to Explore → Select Loki
- Test queries:
  - `{container_name=~".*order-processor.*"}`
  - `{service="gateway"}`
- Verify logs appear

#### Step 4.4: Verify Dashboard
- Access Grafana dashboard (http://localhost:3001)
- Test all panels show data
- Test filters (service, log level)
- Test time range selector
- Verify metrics update in real-time

#### Step 4.5: Generate Test Traffic
- Make API calls through Gateway
- Verify metrics appear in dashboard
- Verify logs appear in dashboard

---

## File Changes Required

### New Files to Create

1. `monitoring/prometheus/prometheus.yml` - Prometheus scrape configuration
2. `monitoring/grafana/provisioning/datasources/prometheus.yml` - Prometheus datasource
3. `monitoring/grafana/provisioning/dashboards/dashboards.yml` - Dashboard provisioning config
4. `monitoring/grafana/dashboards/services-overview.json` - Main dashboard

### Files to Modify

1. `monitoring/docker-compose.logs.yml`:
   - **Fix Grafana port**: Change "3000:3000" to "3001:3000" (host:container)
   - Add Prometheus service
   - Add network connection to `order-processor-network`
   - Add dashboard volume mount to Grafana
   - Add prometheus-data volume

2. `monitoring/promtail/config.yml` (if log collection needs fixing):
   - Verify Docker SD config
   - Fix log path matching if needed

---

## Risk Assessment

### Low Risk
- Adding Prometheus service (isolated, won't break existing)
- Adding Prometheus datasource (just configuration)
- Creating dashboards (read-only, won't affect services)

### Medium Risk
- Network changes (connecting Prometheus to order-processor-network)
  - **Mitigation**: Test in isolation first, verify services still accessible
- Promtail configuration changes (if needed)
  - **Mitigation**: Keep backup of current config

### No Risk
- Dashboard JSON files (only affect Grafana UI)

---

## Success Criteria

1. ✅ Prometheus scrapes all 6 services successfully
2. ✅ Grafana can query Prometheus (datasource test passes)
3. ✅ Loki collects logs from all services
4. ✅ Grafana can query Loki (logs appear in Explore)
5. ✅ Dashboard displays service health status
6. ✅ Dashboard displays request metrics (rate, errors, latency)
7. ✅ Dashboard displays service logs with filtering
8. ✅ All panels update with real data (not empty)
9. ✅ Dashboard loads automatically in Grafana

---

## Implementation Order

1. **Phase 1**: Add Prometheus (metrics collection)
   - Lowest risk, most impact
   - Enables metrics dashboard immediately

2. **Phase 2**: Fix logs (if needed)
   - Verify current setup first
   - Fix only if broken

3. **Phase 3**: Create dashboard
   - After both data sources working
   - Can test panels individually

4. **Phase 4**: Test and verify
   - End-to-end verification
   - Document any issues

---

## Notes and Considerations

1. **Network Access**: Prometheus must be able to reach services on `order-processor-network`
   - Use Docker network connection or external_links
   - Verify DNS resolution works (container names)

2. **Service Names**: Prometheus scrape targets must use container names exactly:
   - `order-processor-gateway`
   - `order-processor-auth_service`
   - etc.

3. **Log Paths**: Services write logs inside containers
   - Docker SD should capture stdout automatically
   - If using file-based, need volume mounts

4. **Dashboard Simplicity**: Keep dashboard simple for personal project
   - No complex analytics
   - Basic panels only
   - Easy to understand

5. **Port Conflicts**: Ensure no port conflicts (Docker Compose)
   - **Frontend**: 3000 (host) - ✅ Fixed
   - **Grafana**: 3001 (host) → 3000 (container) - Needs fix
   - **Prometheus**: 9090 (host:container) - OK
   - **Loki**: 3100 (host:container) - OK
   - All ports must be unique on host

---

## Next Steps After Completion

1. Update BACKLOG.md: Mark MON-001 as completed
2. Update DAILY_WORK_LOG.md: Document implementation details
3. Test with real traffic: Generate requests and verify metrics/logs
4. Document dashboard usage: How to use filters, what each panel shows

---

**Status**: Ready for implementation review and approval
