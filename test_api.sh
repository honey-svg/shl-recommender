#!/bin/bash
# API Testing Script
# Usage: bash test_api.sh [URL] [TEST_NAME]
# Default URL: http://localhost:8000

URL=${1:-http://localhost:8000}
TEST=${2:-all}

echo "Testing SHL Assessment Recommender API"
echo "URL: $URL"
echo "======================================="

# Test 1: Health Check
test_health() {
    echo -e "\n[1] Testing /health endpoint..."
    curl -s -X GET "$URL/health" | python -m json.tool
}

# Test 2: Basic Conversation
test_basic_chat() {
    echo -e "\n[2] Testing basic chat flow..."
    
    echo -e "\n  Turn 1: Initial query"
    RESPONSE=$(curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "I am hiring a Java developer"}
        ]
      }')
    echo "$RESPONSE" | python -m json.tool
    
    echo -e "\n  Turn 2: Seniority level"
    RESPONSE=$(curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "I am hiring a Java developer"},
          {"role": "assistant", "content": "Got it! What level of experience?"},
          {"role": "user", "content": "Mid-level, around 4 years"}
        ]
      }')
    echo "$RESPONSE" | python -m json.tool
    
    echo -e "\n  Turn 3: Add soft skills requirement"
    RESPONSE=$(curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "I am hiring a Java developer"},
          {"role": "assistant", "content": "Got it! What level of experience?"},
          {"role": "user", "content": "Mid-level, around 4 years"},
          {"role": "assistant", "content": "Any other requirements?"},
          {"role": "user", "content": "They need strong communication and leadership skills"}
        ]
      }')
    echo "$RESPONSE" | python -m json.tool
}

# Test 3: Off-topic Handling
test_offscope() {
    echo -e "\n[3] Testing off-topic request handling..."
    curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "What is the market salary for a Python developer?"}
        ]
      }' | python -m json.tool
}

# Test 4: Comparison
test_comparison() {
    echo -e "\n[4] Testing comparison request..."
    curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "Compare OPQ32r and GSA"}
        ]
      }' | python -m json.tool
}

# Test 5: Vague Query
test_vague() {
    echo -e "\n[5] Testing vague query (should ask for clarification)..."
    curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "I need an assessment"}
        ]
      }' | python -m json.tool
}

# Test 6: Schema Validation
test_schema() {
    echo -e "\n[6] Validating response schema..."
    RESPONSE=$(curl -s -X POST "$URL/chat" \
      -H "Content-Type: application/json" \
      -d '{
        "messages": [
          {"role": "user", "content": "Hiring a Python developer"},
          {"role": "assistant", "content": "Got it"},
          {"role": "user", "content": "Senior level"}
        ]
      }')
    
    echo "$RESPONSE" | python -c "
import sys, json
data = json.load(sys.stdin)
print('Response keys:', list(data.keys()))
print('Has reply:', 'reply' in data)
print('Has recommendations:', 'recommendations' in data)
print('Has end_of_conversation:', 'end_of_conversation' in data)
print('Recommendations type:', type(data.get('recommendations')))
print('Recommendations count:', len(data.get('recommendations', [])))
if data.get('recommendations'):
    rec = data['recommendations'][0]
    print('First recommendation keys:', list(rec.keys()))
    print('Has valid URL:', 'shl.com' in rec.get('url', ''))
"
}

# Run tests
case $TEST in
    health) test_health ;;
    chat) test_basic_chat ;;
    offscope) test_offscope ;;
    comparison) test_comparison ;;
    vague) test_vague ;;
    schema) test_schema ;;
    *)
        test_health
        test_basic_chat
        test_offscope
        test_comparison
        test_vague
        test_schema
        ;;
esac

echo -e "\n======================================="
echo "Testing complete!"
