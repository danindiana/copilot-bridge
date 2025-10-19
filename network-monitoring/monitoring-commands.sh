#!/bin/bash
# Network Activity Monitoring Commands
# Useful commands for viewing and analyzing Copilot network activity

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Copilot Network Activity Monitoring Commands           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Live monitoring with pretty formatting
echo -e "${GREEN}1. Live Monitoring (Pretty JSON)${NC}"
echo "   python3 ../proxy_instrumented.py 2>&1 1>/dev/null | jq '.'"
echo ""

# 2. Watch only key metrics
echo -e "${GREEN}2. Watch Key Metrics Only${NC}"
echo "   python3 ../proxy_instrumented.py 2>&1 1>/dev/null | jq '{route, tokens: .total_tokens, latency_ms, cost_saved_usd}'"
echo ""

# 3. Save to file
echo -e "${GREEN}3. Save Metrics to File${NC}"
echo "   python3 ../proxy_instrumented.py 2>copilot-metrics.jsonl"
echo ""

# 4. Test with custom prompt
echo -e "${GREEN}4. Test with Custom Prompt${NC}"
echo "   python3 ../proxy_instrumented.py --prompt 'Your prompt here' --task 'docstring' 2>&1 | tail -1 | jq '.'"
echo ""

# 5. Monitor and filter by route
echo -e "${GREEN}5. Filter by Route (Local Only)${NC}"
echo "   python3 ../proxy_instrumented.py 2>&1 1>/dev/null | jq 'select(.route == \"local\")'"
echo ""

# 6. Calculate real-time cost savings
echo -e "${GREEN}6. Show Only Cost Savings${NC}"
echo "   python3 ../proxy_instrumented.py 2>&1 1>/dev/null | jq '.cost_saved_usd'"
echo ""

# Analysis commands (require saved logs)
echo -e "${YELLOW}Analysis Commands (require copilot-metrics.jsonl):${NC}"
echo ""

# 7. Total cost saved
echo -e "${GREEN}7. Calculate Total Cost Saved${NC}"
echo "   cat copilot-metrics.jsonl | jq -s 'map(.cost_saved_usd) | add'"
echo ""

# 8. Request counts by route
echo -e "${GREEN}8. Count Requests by Route${NC}"
echo "   cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({route: .[0].route, count: length})'"
echo ""

# 9. Average latency
echo -e "${GREEN}9. Average Latency by Route${NC}"
echo "   cat copilot-metrics.jsonl | jq -s 'group_by(.route) | map({route: .[0].route, avg_latency_ms: (map(.latency_ms) | add / length)})'"
echo ""

# 10. Total tokens processed
echo -e "${GREEN}10. Total Tokens Processed${NC}"
echo "    cat copilot-metrics.jsonl | jq -s 'map(.total_tokens) | add'"
echo ""

# 11. Task distribution
echo -e "${GREEN}11. Distribution by Task Type${NC}"
echo "    cat copilot-metrics.jsonl | jq -s 'group_by(.task) | map({task: .[0].task, count: length})'"
echo ""

# 12. Latest 10 requests
echo -e "${GREEN}12. Show Latest 10 Requests${NC}"
echo "    tail -10 copilot-metrics.jsonl | jq -s '.'"
echo ""

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Tip: Install jq if not available: sudo apt install jq -y${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
