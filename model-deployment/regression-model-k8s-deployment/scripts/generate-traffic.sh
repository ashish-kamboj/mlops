#!/bin/bash

#######################################
# Traffic Generator for ML Model Inference
# 
# Usage: ./generate-traffic.sh [options]
#   -n, --count NUM       Number of requests to send (default: 100)
#   -d, --delay MS        Delay between requests in milliseconds (default: 50)
#   -u, --url URL         Model endpoint URL (default: http://localhost:5000)
#   -h, --help            Show this help message
#
# Example:
#   ./generate-traffic.sh -n 200 -d 100
#######################################

set -e

# Default values
REQUEST_COUNT=100
DELAY_MS=50
BASE_URL="http://localhost:5000"
PREDICT_ENDPOINT="$BASE_URL/api/v1/predict"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -n|--count)
      REQUEST_COUNT="$2"
      shift 2
      ;;
    -d|--delay)
      DELAY_MS="$2"
      shift 2
      ;;
    -u|--url)
      BASE_URL="$2"
      PREDICT_ENDPOINT="$BASE_URL/api/v1/predict"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [options]"
      echo "  -n, --count NUM       Number of requests to send (default: 100)"
      echo "  -d, --delay MS        Delay between requests in milliseconds (default: 50)"
      echo "  -u, --url URL         Model endpoint URL (default: http://localhost:5000)"
      echo "  -h, --help            Show this help message"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Convert delay to seconds for sleep command
DELAY_SEC=$(awk "BEGIN {print $DELAY_MS/1000}")

# Function to generate random float between -2.0 and 2.0
random_float() {
  awk -v min=-2.0 -v max=2.0 'BEGIN{srand(); print min+rand()*(max-min)}'
}

# Check if jq is available (optional, for pretty output)
JQ_AVAILABLE=false
if command -v jq &> /dev/null; then
  JQ_AVAILABLE=true
fi

echo -e "${CYAN}======================================${NC}"
echo -e "${CYAN}ML Model Traffic Generator${NC}"
echo -e "${CYAN}======================================${NC}"
echo -e "Endpoint:     $PREDICT_ENDPOINT"
echo -e "Requests:     $REQUEST_COUNT"
echo -e "Delay:        ${DELAY_MS}ms"
echo -e "${CYAN}======================================${NC}\n"

# Check if service is reachable
echo -e "${YELLOW}Checking service health...${NC}"
if curl -s -f "$BASE_URL/health" > /dev/null 2>&1; then
  echo -e "${GREEN}✓ Service is healthy${NC}\n"
else
  echo -e "${RED}✗ Error: Cannot reach service at $BASE_URL${NC}"
  echo -e "${YELLOW}Make sure port-forward is running:${NC}"
  echo -e "  kubectl port-forward svc/regression-model-service 5000:5000"
  exit 1
fi

# Statistics counters
SUCCESS_COUNT=0
ERROR_COUNT=0
START_TIME=$(date +%s)

echo -e "${CYAN}Starting load test...${NC}\n"

# Main loop
for ((i=1; i<=REQUEST_COUNT; i++)); do
  # Generate 8 random features
  FEATURE1=$(random_float)
  FEATURE2=$(random_float)
  FEATURE3=$(random_float)
  FEATURE4=$(random_float)
  FEATURE5=$(random_float)
  FEATURE6=$(random_float)
  FEATURE7=$(random_float)
  FEATURE8=$(random_float)
  
  # Create JSON payload
  JSON_PAYLOAD=$(cat <<EOF
{
  "features": [
    $FEATURE1,
    $FEATURE2,
    $FEATURE3,
    $FEATURE4,
    $FEATURE5,
    $FEATURE6,
    $FEATURE7,
    $FEATURE8
  ],
  "request_id": "load-test-$i"
}
EOF
)
  
  # Send request
  RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X POST "$PREDICT_ENDPOINT" \
    -H "Content-Type: application/json" \
    -d "$JSON_PAYLOAD" \
    2>/dev/null)
  
  # Extract HTTP status code (last line)
  HTTP_CODE=$(echo "$RESPONSE" | tail -n 1)
  
  # Extract response body (everything except last line)
  RESPONSE_BODY=$(echo "$RESPONSE" | head -n -1)
  
  # Check status
  if [ "$HTTP_CODE" -eq 200 ]; then
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    
    # Extract prediction value
    if [ "$JQ_AVAILABLE" = true ]; then
      PREDICTION=$(echo "$RESPONSE_BODY" | jq -r '.prediction // "N/A"')
    else
      PREDICTION=$(echo "$RESPONSE_BODY" | grep -o '"prediction":[^,}]*' | cut -d':' -f2 | tr -d ' ')
    fi
    
    echo -e "${GREEN}[$i/$REQUEST_COUNT] ✓${NC} Prediction: $PREDICTION"
  else
    ERROR_COUNT=$((ERROR_COUNT + 1))
    
    # Extract error message if available
    if [ "$JQ_AVAILABLE" = true ]; then
      ERROR_MSG=$(echo "$RESPONSE_BODY" | jq -r '.detail // "Unknown error"' 2>/dev/null || echo "Unknown error")
    else
      ERROR_MSG="HTTP $HTTP_CODE"
    fi
    
    echo -e "${RED}[$i/$REQUEST_COUNT] ✗${NC} Error: $ERROR_MSG"
  fi
  
  # Delay before next request (except for last one)
  if [ $i -lt $REQUEST_COUNT ]; then
    sleep "$DELAY_SEC"
  fi
done

# Calculate statistics
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
SUCCESS_RATE=$(awk "BEGIN {printf \"%.2f\", ($SUCCESS_COUNT/$REQUEST_COUNT)*100}")
REQUESTS_PER_SEC=$(awk "BEGIN {printf \"%.2f\", $REQUEST_COUNT/$DURATION}")

# Print summary
echo -e "\n${CYAN}======================================${NC}"
echo -e "${CYAN}Summary${NC}"
echo -e "${CYAN}======================================${NC}"
echo -e "Total requests:    $REQUEST_COUNT"
echo -e "${GREEN}Successful:        $SUCCESS_COUNT${NC}"
echo -e "${RED}Failed:            $ERROR_COUNT${NC}"
echo -e "Success rate:      ${SUCCESS_RATE}%"
echo -e "Duration:          ${DURATION}s"
echo -e "Throughput:        ${REQUESTS_PER_SEC} req/s"
echo -e "${CYAN}======================================${NC}\n"

echo -e "${YELLOW}Check metrics at:${NC}"
echo -e "  Metrics endpoint: $BASE_URL/metrics"
echo -e "  Prometheus:       http://localhost:9090"
echo -e "  Grafana:          http://localhost:3000"
echo -e ""

# Exit with error code if any requests failed
if [ $ERROR_COUNT -gt 0 ]; then
  exit 1
fi