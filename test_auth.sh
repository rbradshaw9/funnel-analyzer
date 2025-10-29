#!/bin/bash

# Authentication Testing Script
# This script tests all authentication endpoints on your Railway backend

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   Funnel Analyzer Authentication Test Suite${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""

# Check if Railway URL is provided
if [ -z "$1" ]; then
    echo -e "${RED}❌ ERROR: Railway backend URL not provided${NC}"
    echo ""
    echo "Usage: ./test_auth.sh https://your-railway-backend-url.up.railway.app"
    echo ""
    echo "Find your Railway URL:"
    echo "1. Go to Railway dashboard"
    echo "2. Click on your backend service"
    echo "3. Copy the public URL"
    exit 1
fi

BACKEND_URL="$1"

echo -e "${YELLOW}Testing backend at: ${BACKEND_URL}${NC}"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
echo "GET ${BACKEND_URL}/health"
HEALTH_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BACKEND_URL}/health")
HTTP_STATUS=$(echo "$HEALTH_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$HEALTH_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Health check passed${NC}"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}❌ Health check failed with status $HTTP_STATUS${NC}"
    echo "$RESPONSE_BODY"
fi
echo ""

# Test 2: Database Health Check
echo -e "${BLUE}Test 2: Database Health Check${NC}"
echo "GET ${BACKEND_URL}/health/db"
DB_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "${BACKEND_URL}/health/db")
HTTP_STATUS=$(echo "$DB_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$DB_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Database health check passed${NC}"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    
    # Check if admin exists
    if echo "$RESPONSE_BODY" | grep -q "admin_user_exists.*true"; then
        echo -e "${GREEN}✅ Admin user exists in database${NC}"
    else
        echo -e "${RED}❌ Admin user NOT found in database${NC}"
        echo -e "${YELLOW}⚠️  Set DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD in Railway env vars${NC}"
    fi
else
    echo -e "${RED}❌ Database health check failed with status $HTTP_STATUS${NC}"
    echo "$RESPONSE_BODY"
fi
echo ""

# Test 3: Admin Login
echo -e "${BLUE}Test 3: Admin Login${NC}"
echo "POST ${BACKEND_URL}/api/auth/admin/login"
ADMIN_LOGIN=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${BACKEND_URL}/api/auth/admin/login" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "ryan@funnelanalyzerpro.com",
        "password": "FiR43Tx2-"
    }')
HTTP_STATUS=$(echo "$ADMIN_LOGIN" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$ADMIN_LOGIN" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Admin login successful!${NC}"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
    
    # Extract token
    TOKEN=$(echo "$RESPONSE_BODY" | python3 -c "import sys, json; print(json.load(sys.stdin).get('token', ''))" 2>/dev/null)
    if [ -n "$TOKEN" ]; then
        echo -e "${GREEN}✅ JWT token received${NC}"
        echo "Token: ${TOKEN:0:50}..."
    fi
else
    echo -e "${RED}❌ Admin login failed with status $HTTP_STATUS${NC}"
    echo "$RESPONSE_BODY"
    echo ""
    echo -e "${YELLOW}Possible reasons:${NC}"
    echo "  - Admin user not created (missing env vars)"
    echo "  - Wrong password"
    echo "  - Database connection issue"
fi
echo ""

# Test 4: User Registration
echo -e "${BLUE}Test 4: User Registration${NC}"
TEST_EMAIL="test-$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
echo "POST ${BACKEND_URL}/api/auth/register"
echo "Test email: $TEST_EMAIL"
REGISTER_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${BACKEND_URL}/api/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"${TEST_EMAIL}\",
        \"password\": \"${TEST_PASSWORD}\",
        \"full_name\": \"Test User\"
    }")
HTTP_STATUS=$(echo "$REGISTER_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$REGISTER_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ] || [ "$HTTP_STATUS" = "201" ]; then
    echo -e "${GREEN}✅ User registration successful!${NC}"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}❌ User registration failed with status $HTTP_STATUS${NC}"
    echo "$RESPONSE_BODY"
fi
echo ""

# Test 5: Member Login
echo -e "${BLUE}Test 5: Member Login (with newly registered user)${NC}"
echo "POST ${BACKEND_URL}/api/auth/login"
LOGIN_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "${BACKEND_URL}/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"${TEST_EMAIL}\",
        \"password\": \"${TEST_PASSWORD}\"
    }")
HTTP_STATUS=$(echo "$LOGIN_RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
RESPONSE_BODY=$(echo "$LOGIN_RESPONSE" | sed '/HTTP_STATUS/d')

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ Member login successful!${NC}"
    echo "$RESPONSE_BODY" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE_BODY"
else
    echo -e "${RED}❌ Member login failed with status $HTTP_STATUS${NC}"
    echo "$RESPONSE_BODY"
fi
echo ""

# Summary
echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}                  Test Summary${NC}"
echo -e "${BLUE}==================================================${NC}"
echo ""
echo "Backend URL: $BACKEND_URL"
echo ""
echo "Next steps:"
echo "1. If all tests passed ✅ - Configure Vercel frontend"
echo "2. Set NEXT_PUBLIC_API_URL in Vercel to: $BACKEND_URL"
echo "3. Remove old /admin deployment"
echo "4. Test login through Next.js UI at funnelanalyzerpro.com"
echo ""
echo "For detailed instructions, see COMPREHENSIVE_AUTH_FIX.md"
echo ""
