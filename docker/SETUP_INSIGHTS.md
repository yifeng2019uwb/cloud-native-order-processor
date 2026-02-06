# 🚀 Quick Setup: Insights Service with Gemini API

## Step 1: Set Your Gemini API Key

**⚠️ IMPORTANT**: Never commit your API key to git! The `.env` file is already in `.gitignore`.

### Option A: Export as Environment Variable (Recommended for testing)

```bash
export GOOGLE_GEMINI_API_KEY="your-gemini-api-key-here"
```

### Option B: Create/Update `.env` file

Create `docker/.env` file (or add to existing one):

```bash
cd docker
echo 'GOOGLE_GEMINI_API_KEY=your-gemini-api-key-here' >> .env
```

**Note**: The `.env` file is gitignored, so your key is safe.

## Step 2: Deploy Insights Service

```bash
cd docker
./deploy.sh insights deploy
```

Or deploy all services:

```bash
./deploy.sh all deploy
```

## Step 3: Verify Deployment

Check service health:

```bash
# Check if insights service is running
docker ps | grep insights

# Check logs
docker logs order-processor-insights_service

# Test health endpoint (from inside Docker network)
docker exec order-processor-gateway curl http://insights_service:8004/health
```

## Step 4: Test the Endpoint

### Quick Test with Load Test User

```bash
# Login with load test user
TOKEN=$(curl -s -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "load_test_user_1",
    "password": "TestPassword123!"
  }' | jq -r '.access_token')

# Test insights endpoint
curl -X GET http://localhost:8080/api/v1/insights/portfolio \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

**Note**: If you don't have `jq`, copy the `access_token` from the login response manually.

## Troubleshooting

### Service won't start
- Check if API key is set: `echo $GOOGLE_GEMINI_API_KEY`
- Check logs: `docker logs order-processor-insights_service`
- Verify dependencies: `docker ps` (should see user_service, order_service, etc.)

### 401 Unauthorized
- **Rebuild gateway**: `cd docker && ./deploy.sh gateway rebuild` (route code changes require rebuild)
- Make sure you're passing a valid JWT token
- Token should be obtained via `/api/v1/auth/login`
- Check gateway logs: `docker logs order-processor-gateway --tail=50`

### 500 Internal Server Error
- Check insights service logs: `docker logs order-processor-insights_service --tail=50`
- Verify Gemini API key is valid: `docker exec order-processor-insights_service env | grep GOOGLE_GEMINI`
- Check if other services (user, order, inventory) are healthy

## Next Steps

- ✅ Service deployed
- ✅ Gateway route configured
- ⏳ Run integration tests
- ⏳ Frontend integration (optional)
