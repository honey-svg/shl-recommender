"""
Testing module for the SHL Assessment Recommender agent.
Evaluates against conversation traces.
"""
import json
import logging
from typing import List, Dict, Any
from pathlib import Path
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from catalog import get_catalog
from agent import ConversationAgent
from main import ChatRequest, Message, chat

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TraceEvaluator:
    """Evaluates agent performance against conversation traces."""
    
    def __init__(self, traces_dir: str = "data/traces"):
        self.traces_dir = Path(traces_dir)
        self.catalog = get_catalog()
    
    def load_traces(self) -> List[Dict[str, Any]]:
        """Load all conversation traces from directory."""
        traces = []
        if not self.traces_dir.exists():
            logger.warning(f"Traces directory not found: {self.traces_dir}")
            return traces
        
        for trace_file in self.traces_dir.glob("*.json"):
            try:
                with open(trace_file, 'r') as f:
                    trace = json.load(f)
                    traces.append(trace)
            except Exception as e:
                logger.error(f"Failed to load trace {trace_file}: {e}")
        
        return traces
    
    def evaluate_trace(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single trace."""
        result = {
            "trace_id": trace.get("id", "unknown"),
            "persona": trace.get("persona", ""),
            "expected_assessments": trace.get("expected_assessments", []),
            "conversation_turns": [],
            "final_recommendations": [],
            "metrics": {}
        }
        
        # Simulate the conversation
        messages = []
        turn_num = 0
        
        for i, turn in enumerate(trace.get("conversation", [])):
            turn_num += 1
            
            # User turn
            user_message = turn.get("user", "")
            messages.append(Message(role="user", content=user_message))
            
            # Create agent
            agent = ConversationAgent()
            
            # Reconstruct context
            for msg in messages:
                if msg.role == "user":
                    agent._extract_context(msg.content)
            
            # Get agent response
            reply, recommendations, end_conversation = agent.process_user_message(
                user_message, self.catalog
            )
            
            messages.append(Message(role="assistant", content=reply))
            
            turn_result = {
                "turn": turn_num,
                "user": user_message,
                "agent_reply": reply,
                "recommendations_count": len(recommendations),
                "end_conversation": end_conversation
            }
            
            result["conversation_turns"].append(turn_result)
            
            if recommendations:
                result["final_recommendations"] = recommendations
            
            # Check turn limit
            if len(messages) >= 8:
                break
        
        # Calculate metrics
        result["metrics"] = self._calculate_metrics(
            result["final_recommendations"],
            result["expected_assessments"]
        )
        
        return result
    
    def _calculate_metrics(self, recommendations: List[Dict], 
                          expected: List[str]) -> Dict[str, Any]:
        """Calculate recall and other metrics."""
        if not expected:
            return {"recall_10": 1.0, "precision": 1.0, "f1": 1.0}
        
        rec_names = {rec.get("name", "") for rec in recommendations}
        expected_set = set(expected)
        
        # Recall@10
        correct = len(rec_names.intersection(expected_set))
        recall = correct / len(expected_set) if expected_set else 1.0
        
        # Precision
        precision = correct / len(rec_names) if rec_names else 0.0
        
        # F1
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        return {
            "recall_10": recall,
            "precision": precision,
            "f1": f1,
            "correct_recommendations": correct,
            "expected_count": len(expected_set),
            "recommended_count": len(rec_names)
        }
    
    def run_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all traces."""
        traces = self.load_traces()
        logger.info(f"Loaded {len(traces)} traces")
        
        results = []
        for trace in traces:
            result = self.evaluate_trace(trace)
            results.append(result)
            logger.info(f"Evaluated {result['trace_id']}: "
                       f"recall={result['metrics'].get('recall_10', 0):.2f}")
        
        # Aggregate metrics
        avg_recall = (sum(r['metrics'].get('recall_10', 0) for r in results) / len(results) 
                     if results else 0.0)
        
        return {
            "total_traces": len(results),
            "results": results,
            "average_recall_10": avg_recall
        }


def test_agent_directly():
    """Test agent with a simple conversation."""
    logger.info("Testing agent with sample conversation...")
    
    catalog = get_catalog()
    agent = ConversationAgent()
    
    # Sample conversation
    user_inputs = [
        "I'm hiring a Java developer",
        "Mid-level, around 4 years experience",
        "They work with stakeholders and need communication skills"
    ]
    
    for user_input in user_inputs:
        reply, recommendations, end_conv = agent.process_user_message(user_input, catalog)
        logger.info(f"User: {user_input}")
        logger.info(f"Agent: {reply}")
        if recommendations:
            logger.info(f"Recommendations: {len(recommendations)} items")
        logger.info("---")


if __name__ == "__main__":
    # Run direct test
    test_agent_directly()
    
    # Run trace evaluation
    evaluator = TraceEvaluator()
    eval_results = evaluator.run_evaluation()
    
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Total traces: {eval_results['total_traces']}")
    print(f"Average Recall@10: {eval_results['average_recall_10']:.2f}")
    print("="*60)
