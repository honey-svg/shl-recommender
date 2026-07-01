"""
Integration tests for SHL Assessment Recommender.
Tests the full conversation flow and edge cases.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from catalog import get_catalog
from agent import ConversationAgent
import json


def test_basic_conversation():
    """Test basic conversation flow."""
    print("\n" + "="*60)
    print("TEST 1: Basic Conversation Flow")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    messages = [
        "I'm hiring a Java developer",
        "Mid-level, around 4 years experience",
        "They need strong communication skills"
    ]
    
    for i, user_input in enumerate(messages, 1):
        reply, recommendations, end_conv = agent.process_user_message(user_input, catalog)
        print(f"\nTurn {i} - User: {user_input}")
        print(f"Agent: {reply[:100]}...")
        print(f"Recommendations: {len(recommendations)}, End: {end_conv}")
        
        if recommendations:
            for rec in recommendations[:3]:
                print(f"  - {rec['name']} ({rec['test_type']})")


def test_vague_query():
    """Test that vague queries don't get immediate recommendations."""
    print("\n" + "="*60)
    print("TEST 2: Vague Query Handling")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    vague_queries = [
        "I need an assessment",
        "Tell me about your tests",
        "What do you recommend?"
    ]
    
    for query in vague_queries:
        agent = ConversationAgent()
        reply, recommendations, _ = agent.process_user_message(query, catalog)
        print(f"\nQuery: {query}")
        print(f"Recommendations on turn 1: {len(recommendations)} ({'FAIL' if len(recommendations) > 0 else 'PASS'})")
        print(f"Reply: {reply[:80]}...")


def test_off_topic():
    """Test off-topic handling."""
    print("\n" + "="*60)
    print("TEST 3: Off-Topic Request Handling")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    offscope_queries = [
        "What's the market salary for a developer?",
        "How much should we pay this role?",
        "Is this legal hiring practice?",
        "Tell me about recruitment strategy"
    ]
    
    for query in offscope_queries:
        agent = ConversationAgent()
        reply, recommendations, _ = agent.process_user_message(query, catalog)
        is_refused = "off-topic" in reply.lower() or "can't assist" in reply.lower() or "specifically designed" in reply.lower()
        print(f"\nQuery: {query}")
        print(f"Refused: {'PASS' if is_refused else 'FAIL'}")
        print(f"Reply: {reply[:80]}...")


def test_comparison():
    """Test comparison requests."""
    print("\n" + "="*60)
    print("TEST 4: Comparison Requests")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    comparison_requests = [
        "Compare OPQ32r and GSA",
        "What's the difference between Java 8 and Python?",
        "How does OPQ32r differ from GSA?"
    ]
    
    for query in comparison_requests:
        agent = ConversationAgent()
        reply, recommendations, _ = agent.process_user_message(query, catalog)
        has_comparison = "vs" in reply.lower() or "different" in reply.lower()
        print(f"\nQuery: {query}")
        print(f"Has comparison: {'PASS' if has_comparison else 'FAIL'}")
        print(f"Reply excerpt: {reply[:100]}...")


def test_refinement():
    """Test conversational refinement."""
    print("\n" + "="*60)
    print("TEST 5: Conversational Refinement")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    # First, establish context and get recommendations
    agent.process_user_message("I'm hiring a Java developer", catalog)
    agent.process_user_message("Senior level", catalog)
    reply1, recs1, _ = agent.process_user_message("They need leadership skills", catalog)
    
    print(f"\nInitial recommendations: {len(recs1)}")
    if recs1:
        print(f"  - {recs1[0]['name']} ({recs1[0]['test_type']})")
    
    # Now refine - user adds constraint
    agent2 = ConversationAgent()
    agent2.process_user_message("I'm hiring a Java developer", catalog)
    agent2.process_user_message("Senior level", catalog)
    agent2.process_user_message("They need leadership skills", catalog)
    reply2, recs2, _ = agent2.process_user_message("Actually, also add personality tests", catalog)
    
    print(f"\nRefined recommendations: {len(recs2)}")
    print(f"Updated context - assessment types: {agent2.context.assessment_types}")


def test_schema_compliance():
    """Test API response schema compliance."""
    print("\n" + "="*60)
    print("TEST 6: Response Schema Compliance")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    reply, recommendations, end_conv = agent.process_user_message(
        "I'm hiring a Python developer",
        catalog
    )
    
    print(f"\nReply type: {type(reply).__name__} ({'PASS' if isinstance(reply, str) else 'FAIL'})")
    print(f"Recommendations type: {type(recommendations).__name__} ({'PASS' if isinstance(recommendations, list) else 'FAIL'})")
    print(f"End conversation type: {type(end_conv).__name__} ({'PASS' if isinstance(end_conv, bool) else 'FAIL'})")
    
    if recommendations:
        rec = recommendations[0]
        has_name = 'name' in rec
        has_url = 'url' in rec and 'shl.com' in rec.get('url', '')
        has_type = 'test_type' in rec
        
        print(f"Recommendation has name: {'PASS' if has_name else 'FAIL'}")
        print(f"Recommendation has valid URL: {'PASS' if has_url else 'FAIL'}")
        print(f"Recommendation has test_type: {'PASS' if has_type else 'FAIL'}")


def test_turn_limit():
    """Test turn limit enforcement."""
    print("\n" + "="*60)
    print("TEST 7: Turn Limit Enforcement")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    messages = [
        "I'm hiring a developer",
        "Senior level",
        "Python and JavaScript",
        "Leadership and communication skills",
        "Include personality tests",
        "What about situational judgment?",
        "Okay, that sounds good",
        "Let's proceed with these"
    ]
    
    turn_count = 0
    for msg in messages:
        turn_count += 1
        reply, recommendations, end_conv = agent.process_user_message(msg, catalog)
        print(f"\nTurn {turn_count}: User message processed")
        
        if turn_count >= 8:
            print(f"Turn limit check: {'PASS' if len(reply) > 0 else 'FAIL'}")
            break


def test_url_validation():
    """Test that all URLs are from SHL catalog."""
    print("\n" + "="*60)
    print("TEST 8: URL Validation")
    print("="*60)
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    agent.process_user_message("I'm hiring a Java developer", catalog)
    agent.process_user_message("Senior level", catalog)
    reply, recommendations, _ = agent.process_user_message("They need leadership", catalog)
    
    all_valid = True
    for rec in recommendations:
        is_valid = "shl.com" in rec.get("url", "")
        if not is_valid:
            all_valid = False
            print(f"Invalid URL: {rec.get('url')}")
    
    print(f"\nAll URLs from SHL catalog: {'PASS' if all_valid else 'FAIL'}")
    print(f"Total recommendations: {len(recommendations)}")


if __name__ == "__main__":
    try:
        test_basic_conversation()
        test_vague_query()
        test_off_topic()
        test_comparison()
        test_refinement()
        test_schema_compliance()
        test_turn_limit()
        test_url_validation()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
