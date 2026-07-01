# SHL Assessment Recommender - Design Approach

## Design Philosophy

Built a **stateless, conversation-aware agent** that gracefully handles ambiguous requirements by asking clarifying questions before recommending. The system prioritizes **robustness over cleverness**—handling edge cases (vague queries, off-topic requests, conversational changes) explicitly rather than relying on LLM hallucinations.

---

## Architecture Overview

### 1. Catalog Management (`catalog.py`)

**Design Decision:** Cache-first with web-scrape fallback.
- Scrapes SHL catalog from product pages, extracting name, URL, description, category, and inferred test type
- Caches to JSON to avoid repeated scraping (network resilience, performance)
- Falls back to curated defaults if scraping fails (robustness)
- Provides search, filtering by category/type, and structured access

**Why this works:**
- Eliminates hallucinated URLs—all recommendations come from actual catalog data
- Fast cold-start even on constrained hosts (Render free tier, ~2min startup)
- Graceful degradation: service works even if scraping fails

### 2. Conversation Agent (`agent.py`)

**Design Decision:** Explicit state machine with context accumulation.

The agent progresses through stages:
1. **GATHERING_INFO**: Extract role, seniority, skills, assessment preferences from user input
2. **RECOMMENDING**: Generate shortlist once `has_enough_context()` is true
3. **COMPARING**: Handle side-by-side comparisons without restarting

**Context Extraction (not using LLM for this):**
- Pattern-based extraction of role titles, seniority levels (junior/mid/senior), technical skills (Java, Python, etc.), soft skills (communication, leadership)
- Keyword spotting for assessment type preferences
- Explicit mapping: Java→"technical", communication→"soft_skill"

**Why pattern-based extraction?**
- Deterministic and auditable (not a black box)
- No hallucination risk
- Consistent across conversation history (extract from all messages, not just last turn)
- Avoids per-turn LLM calls for cost/latency

**Recommendation Scoring:**
- Linear scoring: technical/soft skill matches (+2 points), description matches (+1-2), role type matches (+1-2)
- Penalizes mismatched assessment types if user specified preference
- Selects top 10 by score

**Scope Enforcement:**
- Hard blocklist for off-topic keywords ("salary", "legal", "contract")
- Refuses general hiring advice
- Ensures all URLs point to shl.com

### 3. API Layer (`main.py`)

**Design Decision:** Strict schema compliance, stateless by design.

**Why stateless matters:**
- Evaluator simulates multi-turn conversations, each call with full history
- Forces the agent to re-extract context from entire conversation
- Prevents state corruption from concurrent requests
- Easier to deploy on serverless (though using Render/Railway here)

**Response Schema (non-negotiable):**
```json
{
  "reply": "string",
  "recommendations": [{"name": "...", "url": "...", "test_type": "X"}],
  "end_of_conversation": boolean
}
```

**Why this structure:**
- `recommendations` = empty array until we have high confidence
- Only populated with 1-10 items once context is sufficient
- `end_of_conversation` = true when recommending (user will act on shortlist)
- Strictly validates: 8-turn cap, schema, all URLs from catalog

---

## What Didn't Work & Iteration

### 1. Pure LLM-based Extraction
**Initial attempt:** Let an LLM extract role, skills, preferences from each message.
**Problem:** Hallucinated non-existent skills, inconsistent interpretation.
**Solution:** Switch to pattern-based extraction, validated against known keywords.

### 2. Single-Turn Recommendations
**Initial attempt:** Recommend on turn 1 if user gave a role title.
**Problem:** Missed critical context. "Java developer" alone doesn't tell us seniority, which changes recommendations significantly.
**Solution:** Require at least two pieces of context (role + seniority OR role + skills).

### 3. Greedy Recommendation Updates
**Initial attempt:** If user says "add personality tests," wipe recommendations and start over.
**Problem:** Violates the refinement requirement—should update existing shortlist, not reset.
**Solution:** Track context cumulatively; regenerate rankings when constraints change.

---

## Evaluation Approach

### Testing Against Provided Traces
```python
# tests/evaluate.py simulates the evaluator behavior:
# 1. Load trace (persona + facts + expected assessments)
# 2. Feed user messages sequentially
# 3. Check agent responses for:
#    - Schema compliance
#    - Relevance (recall@10)
#    - Turn limit compliance
#    - Hallucinations (URLs not in catalog)
```

### Metrics Tracked
- **Schema compliance**: Every response matches Pydantic model
- **URL validity**: All recommendations are from shl.com
- **Turn efficiency**: Rarely exceeds 4-5 turns to recommendation
- **Recall@10**: Measures fraction of relevant assessments recommended

### Edge Case Testing
- Vague queries ("I need an assessment") → ask clarification, don't recommend
- Off-topic ("What's the market salary?") → refuse explicitly
- Conversational refinement ("Actually, add leadership") → update context, re-rank
- Comparison requests ("OPQ vs GSA?") → draw from catalog descriptions

---

## Stack Rationale

| Component | Choice | Reason |
|-----------|--------|--------|
| Framework | FastAPI | Type-safe, auto-docs, fast cold start |
| LLM | Optional (Anthropic/OpenAI/Groq) | Not strictly needed for agent logic; patterns sufficient. Fallback for future enhancements. |
| Catalog | Web scrape + JSON cache | Avoids database, startup latency. Catalog rarely changes. |
| Deployment | Render/Railway free tier | Quick iteration, built-in GitHub integration, 30s timeout fits 4-5 turn conversations |

---

## Known Limitations & Mitigations

| Limitation | Impact | Mitigation |
|-----------|--------|-----------|
| Pattern-based extraction may miss edge cases | Potential context loss | Fallback to clarification questions; evaluator provides "no preference" responses |
| Catalog scraped at startup | Cold start ~2min | Cache persists; future: async scrape with streaming responses |
| No persistent state | Can't "remember" user across sessions | By design per requirements; evaluator provides full history each call |

---

## Conclusion

This implementation prioritizes **clarity and reliability** over sophistication. The pattern-based agent logic is auditable, the catalog is grounded in actual SHL data, and the API strictly enforces schema/limits. The system gracefully degrades when information is missing (asks questions) rather than hallucinating, making it suitable for production use.
