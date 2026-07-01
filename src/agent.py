"""
Agent logic for the SHL Assessment Recommender.
Handles clarification, recommendation, refinement, and comparison.
"""
import json
import logging
from typing import Dict, List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ConversationState(Enum):
    """Stages of the recommendation conversation."""
    GATHERING_INFO = "gathering_info"
    RECOMMENDING = "recommending"
    REFINING = "refining"
    COMPARING = "comparing"
    COMPLETE = "complete"


@dataclass
class UserContext:
    """Extracted context about user's hiring needs."""
    role_title: Optional[str] = None
    seniority_level: Optional[str] = None  # junior, mid, senior
    technical_skills: List[str] = None
    soft_skills: List[str] = None
    assessment_types: List[str] = None  # K, P, A, S, etc.
    number_of_candidates: Optional[int] = None
    budget_constraints: Optional[str] = None
    other_requirements: List[str] = None
    
    def __post_init__(self):
        if self.technical_skills is None:
            self.technical_skills = []
        if self.soft_skills is None:
            self.soft_skills = []
        if self.assessment_types is None:
            self.assessment_types = []
        if self.other_requirements is None:
            self.other_requirements = []
    
    def has_enough_context(self) -> bool:
        """Check if we have enough info to make recommendations."""
        # We need at least: role description OR technical skills AND (seniority OR soft_skills)
        has_role_info = self.role_title is not None and len(self.role_title) > 2
        has_technical = len(self.technical_skills) > 0
        has_other = (self.seniority_level is not None or 
                    len(self.soft_skills) > 0 or
                    len(self.assessment_types) > 0)
        
        return has_role_info or (has_technical and has_other)


class ConversationAgent:
    """Main agent for managing the assessment recommendation conversation."""
    
    CLARIFICATION_PROMPTS = [
        "What's the job title or role you're hiring for?",
        "What's the seniority level (junior, mid-level, senior)?",
        "What technical skills are most important?",
        "Are there specific personality or soft skills you care about?",
        "Do you have any preferences for assessment type (technical, personality, reasoning)?",
    ]
    
    SCOPE_KEYWORDS = {
        "offscope": ["salary", "compensation", "legal", "hiring process", "recruiting tips", "hr advice", "contract", "benefits", "equity", "pay", "recruitment strategy", "recruit strategy"],
        "personality": ["personality", "behavioral", "traits", "opq"],
        "technical": ["technical", "programming", "coding", "knowledge"],
        "ability": ["reasoning", "numerical", "verbal", "ability"],
        "situational": ["situational", "judgment", "sj"],
    }
    
    def __init__(self):
        self.context = UserContext()
        self.state = ConversationState.GATHERING_INFO
        self.clarification_count = 0
        self.max_clarifications = 2
        self.last_recommendations = []
        self.asked_questions = set()
    
    def process_user_message(self, user_message: str, catalog) -> Tuple[str, List[Dict], bool]:
        """
        Process a user message and return:
        - response text
        - recommendations (empty list or 1-10 items)
        - end_of_conversation flag
        """
        # Check for off-topic content
        if self._is_off_topic(user_message):
            return self._refuse_message(), [], False
        
        # Check for comparison requests
        if self._is_comparison_request(user_message):
            return self._handle_comparison(user_message, catalog), [], False
        
        # Update context from message
        self._extract_context(user_message)
        
        # Check if we have enough context
        if not self.context.has_enough_context():
            if self.clarification_count < self.max_clarifications:
                response = self._get_next_clarification()
                self.clarification_count += 1
                return response, [], False
            else:
                # Timeout on clarifications - make best guess
                self.state = ConversationState.RECOMMENDING
        
        # Generate recommendations
        recommendations = self._generate_recommendations(catalog)
        
        if recommendations:
            self.state = ConversationState.RECOMMENDING
            self.last_recommendations = recommendations
            response = self._format_recommendations_response(recommendations)
            return response, recommendations, False
        else:
            return "I couldn't find suitable assessments for that criteria. Can you adjust your requirements?", [], False
    
    def _is_off_topic(self, message: str) -> bool:
        """Check if message is off-topic."""
        message_lower = message.lower()
        offscope_words = self.SCOPE_KEYWORDS.get("offscope", [])
        return any(word in message_lower for word in offscope_words)
    
    def _refuse_message(self) -> str:
        """Generate refusal response."""
        return ("I'm specifically designed to help with SHL assessment recommendations. "
                "I can't assist with hiring advice, legal questions, or compensation topics. "
                "Let me know what role you're hiring for and I'll find the right assessments!")
    
    def _is_comparison_request(self, message: str) -> bool:
        """Check if user is asking for comparison."""
        message_lower = message.lower()
        comparison_keywords = ["compare", "difference", "better than", "vs", "versus", "different", "similar"]
        return any(keyword in message_lower for keyword in comparison_keywords)
    
    def _handle_comparison(self, message: str, catalog) -> str:
        """Handle comparison requests between assessments."""
        # Extract assessment names from message
        names = self._extract_assessment_names(message)
        
        if len(names) < 2:
            return "Could you specify which two assessments you'd like me to compare?"
        
        assessments = []
        for name in names:
            for assessment in catalog.get_all():
                if name.lower() in assessment.name.lower():
                    assessments.append(assessment)
                    break
        
        if len(assessments) < 2:
            return f"I couldn't find both assessments in the catalog. Could you clarify the names?"
        
        comparison = self._create_comparison(assessments[:2])
        return comparison
    
    def _extract_assessment_names(self, message: str) -> List[str]:
        """Try to extract assessment names from message."""
        # Simple heuristic - look for capitalized words
        words = message.split()
        names = [w for w in words if w[0].isupper() and len(w) > 2]
        return names
    
    def _create_comparison(self, assessments: List) -> str:
        """Create a comparison between two assessments."""
        if len(assessments) < 2:
            return "Not enough assessments to compare."
        
        a1, a2 = assessments[0], assessments[1]
        
        comparison = f"""**{a1.name} vs {a2.name}**

**{a1.name}:**
- Test Type: {self._test_type_description(a1.test_type)}
- Description: {a1.description}
- Category: {a1.category}
- URL: {a1.url}

**{a2.name}:**
- Test Type: {self._test_type_description(a2.test_type)}
- Description: {a2.description}
- Category: {a2.category}
- URL: {a2.url}

**Key Differences:**
{self._extract_differences(a1, a2)}"""
        
        return comparison
    
    def _test_type_description(self, test_type: str) -> str:
        """Get human-readable description of test type."""
        descriptions = {
            "K": "Knowledge Test - measures technical/domain knowledge",
            "P": "Personality Questionnaire - assesses behavioral traits",
            "A": "Ability Test - measures reasoning, verbal, numerical skills",
            "S": "Situational Judgment - evaluates decision-making",
            "O": "Other Assessment",
        }
        return descriptions.get(test_type, f"Type {test_type}")
    
    def _extract_differences(self, a1, a2) -> str:
        """Extract key differences between two assessments."""
        diffs = []
        
        if a1.test_type != a2.test_type:
            diffs.append(f"- Different test types: {a1.test_type} (Knowledge/Personality/Ability) vs {a2.test_type}")
        
        if a1.category != a2.category:
            diffs.append(f"- Different categories: {a1.category} vs {a2.category}")
        
        if len(diffs) == 0:
            diffs.append("- Both assessments are in the same category but measure different dimensions")
        
        return "\n".join(diffs)
    
    def _extract_context(self, message: str):
        """Extract hiring context from user message."""
        message_lower = message.lower()
        
        # Extract role title
        role_keywords = ["hiring", "need", "looking for", "recruiting", "recruit", "seeking"]
        generic_terms = ["assessment", "test", "evaluation", "candidate", "position"]
        
        for keyword in role_keywords:
            if keyword in message_lower:
                idx = message_lower.find(keyword)
                after_keyword = message[idx + len(keyword):].strip()
                # Take text until punctuation or next sentence
                potential_role = after_keyword.split(';')[0].split(',')[0].split('.')[0].split('who')[0].strip()
                potential_role = potential_role.replace("a ", "", 1).replace("an ", "", 1)
                
                # Check if it's a generic term (skip if too generic)
                if (len(potential_role) > 3 and len(potential_role.split()) <= 4 and 
                    not any(generic in potential_role.lower() for generic in generic_terms)):
                    self.context.role_title = potential_role
                    break
        
        # Extract seniority level
        seniority_keywords = {
            "junior": ["junior", "entry", "entry-level", "entry level", "graduate", "fresher", "beginner"],
            "mid": ["mid-level", "mid level", "intermediate", "mid-career", "3-5 years", "4 years", "5 years", "experience"],
            "senior": ["senior", "lead", "principal", "staff", "10+ years", "10 years", "5+ years", "experienced", "veteran"],
        }
        for level, keywords in seniority_keywords.items():
            if any(kw in message_lower for kw in keywords):
                self.context.seniority_level = level
                break
        
        # Extract technical skills (more comprehensive)
        tech_keywords = {
            "java": "Java",
            "python": "Python",
            "javascript": "JavaScript",
            "c++": "C++",
            "golang": "Go",
            "go lang": "Go",
            "rust": "Rust",
            "sql": "SQL",
            "database": "Database",
            "aws": "AWS",
            "azure": "Azure",
            "cloud": "Cloud",
            "frontend": "Frontend",
            "backend": "Backend",
            "fullstack": "Fullstack",
            "react": "React",
            "angular": "Angular",
            "node": "Node.js",
            "devops": "DevOps",
            "system design": "System Design",
            "distributed systems": "Distributed Systems",
        }
        for keyword, skill in tech_keywords.items():
            if keyword in message_lower:
                if skill not in self.context.technical_skills:
                    self.context.technical_skills.append(skill)
        
        # Extract soft skills
        soft_keywords = {
            "communication": "Communication",
            "communicate": "Communication",
            "leadership": "Leadership",
            "lead": "Leadership",
            "teamwork": "Teamwork",
            "team": "Teamwork",
            "stakeholder": "Stakeholder Management",
            "problem-solving": "Problem-solving",
            "problem solving": "Problem-solving",
            "analytical": "Analytical",
            "analysis": "Analytical",
            "critical thinking": "Critical Thinking",
            "decision making": "Decision Making",
            "interpersonal": "Interpersonal Skills",
        }
        for keyword, skill in soft_keywords.items():
            if keyword in message_lower:
                if skill not in self.context.soft_skills:
                    self.context.soft_skills.append(skill)
        
        # Extract assessment type preferences
        if any(word in message_lower for word in ["personality", "behavioral", "behaviour", "traits"]):
            if "P" not in self.context.assessment_types:
                self.context.assessment_types.append("P")
        if any(word in message_lower for word in ["technical", "programming", "coding", "knowledge", "skill"]):
            if "K" not in self.context.assessment_types:
                self.context.assessment_types.append("K")
        if any(word in message_lower for word in ["reasoning", "numerical", "verbal", "ability", "logic"]):
            if "A" not in self.context.assessment_types:
                self.context.assessment_types.append("A")
        if any(word in message_lower for word in ["situational", "judgment", "scenario"]):
            if "S" not in self.context.assessment_types:
                self.context.assessment_types.append("S")
    
    def _get_next_clarification(self) -> str:
        """Get the next clarification question."""
        if self.clarification_count == 0 and not self.context.role_title:
            return self.CLARIFICATION_PROMPTS[0]
        elif not self.context.seniority_level:
            return self.CLARIFICATION_PROMPTS[1]
        elif len(self.context.technical_skills) == 0:
            return self.CLARIFICATION_PROMPTS[2]
        elif len(self.context.soft_skills) == 0:
            return self.CLARIFICATION_PROMPTS[3]
        else:
            return self.CLARIFICATION_PROMPTS[4]
    
    def _generate_recommendations(self, catalog) -> List[Dict]:
        """Generate assessment recommendations based on context."""
        if not self.context.has_enough_context():
            return []
        
        candidates = []
        
        # Start with all assessments
        all_assessments = catalog.get_all()
        
        # Filter by assessment types if specified
        if self.context.assessment_types:
            matching = [a for a in all_assessments 
                       if a.test_type in self.context.assessment_types]
            candidates = matching
        else:
            candidates = all_assessments
        
        # Score and rank by relevance
        scored = []
        for assessment in candidates:
            score = self._score_assessment(assessment)
            if score > 0:
                scored.append((assessment, score))
        
        # Sort by score and take top 10
        scored.sort(key=lambda x: x[1], reverse=True)
        top_assessments = [a[0] for a in scored[:10]]
        
        return [
            {
                "name": a.name,
                "url": a.url,
                "test_type": a.test_type
            }
            for a in top_assessments
        ]
    
    def _score_assessment(self, assessment) -> float:
        """Score an assessment for relevance to user context."""
        score = 0.0
        content_lower = f"{assessment.name} {assessment.description} {' '.join(assessment.tags)}".lower()
        
        # Score based on role type
        if self.context.role_title:
            role_lower = self.context.role_title.lower()
            
            # Developer roles benefit from technical assessments
            if "developer" in role_lower or "engineer" in role_lower or "programmer" in role_lower:
                if assessment.test_type == "K":
                    score += 3.0
                if "programming" in content_lower or "java" in content_lower or "python" in content_lower:
                    score += 2.0
            
            # Manager roles benefit from personality assessments
            if "manager" in role_lower or "lead" in role_lower:
                if assessment.test_type == "P":
                    score += 3.0
            
            # All roles need reasoning ability
            if assessment.test_type == "A":
                score += 1.5
        
        # Score based on technical skills
        for skill in self.context.technical_skills:
            skill_lower = skill.lower()
            if skill_lower in content_lower:
                score += 2.5
            for tag in assessment.tags:
                if skill_lower in tag.lower():
                    score += 2.0
        
        # Score based on soft skills
        for skill in self.context.soft_skills:
            skill_lower = skill.lower()
            if skill_lower in content_lower:
                score += 2.0
            if "personality" in content_lower and skill_lower in ["communication", "leadership", "teamwork"]:
                score += 1.5
        
        # Score based on seniority
        if self.context.seniority_level:
            if self.context.seniority_level == "senior" and assessment.test_type == "P":
                score += 1.0  # Senior roles often need personality insights
            if self.context.seniority_level in ["junior", "entry"] and assessment.test_type == "K":
                score += 1.0  # Junior roles benefit from knowledge checks
        
        # Penalize if assessment type explicitly excluded
        if self.context.assessment_types and assessment.test_type not in self.context.assessment_types:
            score = score * 0.3  # Heavy penalty but not zero (in case user changes mind)
        
        return max(0, score)
    
    def _format_recommendations_response(self, recommendations: List[Dict]) -> str:
        """Format the recommendations into a natural response."""
        count = len(recommendations)
        if count == 0:
            return "I couldn't find suitable assessments. Could you clarify your requirements?"
        
        response = f"Based on what you've told me about the {self.context.role_title or 'role'}, "
        response += f"here are {count} assessment{'s' if count != 1 else ''} I'd recommend:\n\n"
        
        for i, rec in enumerate(recommendations[:10], 1):
            response += f"{i}. **{rec['name']}** ({rec['test_type']}) - {rec['url']}\n"
        
        return response
