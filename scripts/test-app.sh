#!/bin/bash
set -euo pipefail
BASE="${1:-http://localhost:8080}"

echo "Health check..."
curl -sf "$BASE/health" | python3 -m json.tool

echo "Access test (normal)..."
curl -sf -X POST "$BASE/api/access" \
  -H "Content-Type: application/json" \
  -d '{"card_id":"SC-10001","session_id":"test-normal","failed_pin_count":0,"requests_per_min":5,"label":"test"}'

echo ""
echo "Access test (attack pattern)..."
curl -sf -X POST "$BASE/api/access" \
  -H "Content-Type: application/json" \
  -d '{"card_id":"SC-99999","session_id":"test-attack","failed_pin_count":5,"requests_per_min":50,"label":"test"}' || true

echo ""
echo "ML analyze test..."
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
curl -sf -X POST "$BASE/api/analyze" -F "file=@$SCRIPT_DIR/../data/testdata.csv" | python3 -c "
import sys, json
d=json.load(sys.stdin)
print('Summary:', json.dumps(d['summary'], indent=2, ensure_ascii=False))
print('Table rows:', len(d.get('table',[])))
print('Charts:', list(d.get('charts',{}).keys()))
"

echo "Done."
