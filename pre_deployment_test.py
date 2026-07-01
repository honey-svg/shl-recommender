#!/usr/bin/env python3
"""
Pre-deployment test script
Run this locally to verify everything works before deploying to Render
"""
import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from catalog import get_catalog
from agent import ConversationAgent

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_catalog():
    """Test catalog loading"""
    print_header("TEST 1: Catalog Loading")
    try:
        catalog = get_catalog()
        print(f"✓ Loaded {len(catalog.assessments)} assessments")
        
        # Show sample assessments
        for i, name in enumerate(list(catalog.assessments.keys())[:3]):
            assessment = catalog.assessments[name]
            print(f"  - {name} (Type: {assessment.test_type}, URL: {assessment.url[:40]}...)")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_basic_conversation():
    """Test basic conversation flow"""
    print_header("TEST 2: Basic Conversation Flow")
    try:
        catalog = get_catalog()
        agent = ConversationAgent()
        
        # Turn 1: Initial query
        reply, recs, end = agent.process_user_message(
            "I am hiring a Java developer",
            catalog
        )
        print("Turn 1: User: 'I am hiring a Java developer'")
        print(f"  Agent: {reply[:60]}...")
        print(f"  Recommendations: {len(recs)}")
        
        # Turn 2: Add seniority
        reply, recs, end = agent.process_user_message(
            "Mid-level, around 4 years experience",
            catalog
        )
        print("\nTurn 2: User: 'Mid-level, around 4 years experience'")
        print(f"  Agent: {reply[:60]}...")
        print(f"  Recommendations: {len(recs)}")
        
        # Turn 3: Add soft skills
        reply, recs, end = agent.process_user_message(
            "They need strong communication and leadership skills",
            catalog
        )
        print("\nTurn 3: User: 'They need strong communication and leadership skills'")
        print(f"  Agent: {reply[:60]}...")
        print(f"  Recommendations: {len(recs)} (with names below)")
        
        if recs:
            for i, rec in enumerate(recs[:3], 1):
                print(f"    {i}. {rec['name']} ({rec['test_type']}) - {rec['url'][:40]}...")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_vague_query():
    """Test vague query handling"""
    print_header("TEST 3: Vague Query Handling")
    try:
        catalog = get_catalog()
        agent = ConversationAgent()
        
        reply, recs, end = agent.process_user_message(
            "I need an assessment",
            catalog
        )
        
        is_vague = len(recs) == 0
        print(f"User: 'I need an assessment'")
        print(f"Agent: {reply[:60]}...")
        print(f"Recommendations (should be 0): {len(recs)}")
        print(f"✓ Correct (asks for clarification)" if is_vague else "✗ Incorrect (recommended without context)")
        
        return is_vague
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_offtopic():
    """Test off-topic blocking"""
    print_header("TEST 4: Off-Topic Request Blocking")
    try:
        catalog = get_catalog()
        agent = ConversationAgent()
        
        reply, recs, end = agent.process_user_message(
            "What is the market salary for a Java developer?",
            catalog
        )
        
        is_refused = "can't assist" in reply.lower() or "off-topic" in reply.lower()
        print(f"User: 'What is the market salary for a Java developer?'")
        print(f"Agent: {reply[:60]}...")
        print(f"Recommendations (should be 0): {len(recs)}")
        print(f"✓ Correctly refused" if is_refused else "✗ Didn't refuse properly")
        
        return is_refused
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_schema():
    """Test response schema"""
    print_header("TEST 5: Response Schema Validation")
    try:
        from main import ChatRequest, Message, ChatResponse
        
        # Create valid request
        req = ChatRequest(messages=[
            Message(role="user", content="Java developer"),
            Message(role="assistant", content="Got it"),
            Message(role="user", content="Senior level")
        ])
        
        print(f"✓ Request schema valid")
        print(f"  - {len(req.messages)} messages in history")
        print(f"  - First message role: {req.messages[0].role}")
        
        # Simulate response
        response = ChatResponse(
            reply="Test reply",
            recommendations=[
                {"name": "Test", "url": "https://www.shl.com/test", "test_type": "K"}
            ],
            end_of_conversation=False
        )
        
        print(f"✓ Response schema valid")
        print(f"  - reply: '{response.reply}'")
        print(f"  - recommendations: {len(response.recommendations)} items")
        print(f"  - end_of_conversation: {response.end_of_conversation}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comparison():
    """Test comparison functionality"""
    print_header("TEST 6: Comparison Request")
    try:
        catalog = get_catalog()
        agent = ConversationAgent()
        
        reply, recs, end = agent.process_user_message(
            "Compare OPQ32r and GSA",
            catalog
        )
        
        has_comparison = "vs" in reply.lower() or "different" in reply.lower()
        print(f"User: 'Compare OPQ32r and GSA'")
        print(f"Agent response excerpt:")
        print(f"  {reply[:80]}...")
        print(f"✓ Comparison provided" if has_comparison else "✗ No comparison")
        
        return has_comparison
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def test_urls():
    """Test URL validation"""
    print_header("TEST 7: URL Validation")
    try:
        catalog = get_catalog()
        
        # Check all URLs in catalog
        invalid_urls = []
        for name, assessment in catalog.assessments.items():
            if "shl.com" not in assessment.url:
                invalid_urls.append((name, assessment.url))
        
        if invalid_urls:
            print(f"✗ Found {len(invalid_urls)} invalid URLs:")
            for name, url in invalid_urls:
                print(f"  - {name}: {url}")
            return False
        else:
            print(f"✓ All {len(catalog.assessments)} catalog URLs are from shl.com")
            return True
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False

def main():
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   SHL Assessment Recommender - Pre-Deployment Test Suite   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    tests = [
        ("Catalog Loading", test_catalog),
        ("Basic Conversation", test_basic_conversation),
        ("Vague Query Handling", test_vague_query),
        ("Off-Topic Blocking", test_offtopic),
        ("Schema Validation", test_schema),
        ("Comparison Functionality", test_comparison),
        ("URL Validation", test_urls),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n" + "🎉 "*10)
        print("ALL TESTS PASSED! Ready for deployment to Render.")
        print("🎉 "*10)
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
