"""
SHL Catalog management module.
Handles catalog data structure, retrieval, and caching.
"""
import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

CATALOG_CACHE_PATH = "data/catalog_cache.json"
# Use the SHL products listing page (works better than the old productcatalog path)
SHL_CATALOG_URL = "https://www.shl.com/solutions/products/"


@dataclass
class Assessment:
    """Represents a single SHL assessment."""
    name: str
    url: str
    test_type: str  # K=Knowledge, P=Personality, A=Ability, etc.
    description: str
    category: str
    tags: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "url": self.url,
            "test_type": self.test_type,
            "description": self.description,
            "category": self.category,
            "tags": self.tags
        }


class SHLCatalog:
    """Manages SHL assessment catalog."""
    
    def __init__(self):
        self.assessments: Dict[str, Assessment] = {}
        self.load_or_scrape()
    
    def load_or_scrape(self):
        """Load from cache or scrape fresh catalog."""
        if os.path.exists(CATALOG_CACHE_PATH):
            self._load_from_cache()
        else:
            self._scrape_catalog()
            self._save_to_cache()
    
    def _load_from_cache(self):
        """Load catalog from JSON cache."""
        try:
            with open(CATALOG_CACHE_PATH, 'r') as f:
                data = json.load(f)
                for name, info in data.items():
                    self.assessments[name] = Assessment(**info)
            logger.info(f"Loaded {len(self.assessments)} assessments from cache")
        except Exception as e:
            logger.error(f"Cache load failed: {e}. Will scrape fresh.")
            self._scrape_catalog()
            self._save_to_cache()
    
    def _scrape_catalog(self):
        """Scrape SHL catalog from website."""
        logger.info("Scraping SHL catalog...")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(SHL_CATALOG_URL, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Parse assessments from the catalog page
            # This is a placeholder - adjust selectors based on actual HTML structure
            assessment_cards = soup.find_all('div', class_=['product-card', 'assessment-item'])
            
            for card in assessment_cards:
                try:
                    name_elem = card.find(['h2', 'h3', 'a'])
                    if not name_elem:
                        continue
                    
                    name = name_elem.get_text(strip=True)
                    url = name_elem.get('href', SHL_CATALOG_URL)
                    
                    # Make URL absolute
                    if url.startswith('/'):
                        url = 'https://www.shl.com' + url
                    
                    desc_elem = card.find('p', class_=['description', 'overview'])
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    # Extract category and tags from content
                    category = self._extract_category(card)
                    tags = self._extract_tags(card)
                    test_type = self._infer_test_type(name, description, tags)
                    
                    assessment = Assessment(
                        name=name,
                        url=url,
                        test_type=test_type,
                        description=description,
                        category=category,
                        tags=tags
                    )
                    self.assessments[name] = assessment
                except Exception as e:
                    logger.warning(f"Failed to parse assessment: {e}")
            
            logger.info(f"Scraped {len(self.assessments)} assessments")
            # If scraping returned no assessments, fall back to the curated default
            if len(self.assessments) == 0:
                logger.warning("Scrape returned 0 assessments; loading default fallback catalog")
                self._load_default_catalog()
                self._save_to_cache()
        except Exception as e:
            logger.error(f"Catalog scrape failed: {e}")
            self._load_default_catalog()
    
    def _load_default_catalog(self):
        """Load a curated default catalog for fallback."""
        # This is a fallback catalog with known SHL assessments
        # Based on actual SHL product line
        defaults = {
            "Java 8 (New)": {
                "name": "Java 8 (New)",
                "url": "https://www.shl.com/solutions/products/java-8/",
                "test_type": "K",
                "description": "Java programming knowledge test covering Java 8 features and best practices",
                "category": "Technical",
                "tags": ["programming", "java", "knowledge", "technical"]
            },
            "OPQ32r": {
                "name": "OPQ32r",
                "url": "https://www.shl.com/solutions/products/opq32r/",
                "test_type": "P",
                "description": "Personality questionnaire measuring occupational personality traits and behavioral preferences",
                "category": "Personality",
                "tags": ["personality", "behavioral", "traits", "occupational"]
            },
            "GSA": {
                "name": "GSA",
                "url": "https://www.shl.com/solutions/products/gsa/",
                "test_type": "A",
                "description": "General Skills Assessment measuring reasoning, verbal, and numerical abilities",
                "category": "Ability",
                "tags": ["reasoning", "verbal", "numerical", "ability"]
            },
            "Verify STAR": {
                "name": "Verify STAR",
                "url": "https://www.shl.com/solutions/products/verify-star/",
                "test_type": "K",
                "description": "Short assessment for technical role evaluation, testing core competencies",
                "category": "Technical",
                "tags": ["programming", "technical", "knowledge", "short"]
            },
            "SJI": {
                "name": "SJI (Situational Judgment Inventory)",
                "url": "https://www.shl.com/solutions/products/sji/",
                "test_type": "S",
                "description": "Situational judgment test evaluating decision-making in work scenarios",
                "category": "Behavioral",
                "tags": ["situational", "judgment", "decision-making", "behavioral"]
            },
            "CEB Ability Assessments": {
                "name": "CEB Ability Assessments",
                "url": "https://www.shl.com/solutions/products/ceb-ability/",
                "test_type": "A",
                "description": "Comprehensive ability assessments for graduate and professional roles",
                "category": "Ability",
                "tags": ["reasoning", "ability", "graduate", "professional"]
            },
            "Python Programming": {
                "name": "Python Programming",
                "url": "https://www.shl.com/solutions/products/python-programming/",
                "test_type": "K",
                "description": "Python programming knowledge test for software development roles",
                "category": "Technical",
                "tags": ["programming", "python", "knowledge", "technical"]
            },
            "Frontend Development": {
                "name": "Frontend Development",
                "url": "https://www.shl.com/solutions/products/frontend-development/",
                "test_type": "K",
                "description": "Frontend web development test covering HTML, CSS, JavaScript, and frameworks",
                "category": "Technical",
                "tags": ["programming", "frontend", "web", "javascript"]
            },
            "Leadership Potential Indicator": {
                "name": "Leadership Potential Indicator",
                "url": "https://www.shl.com/solutions/products/leadership-potential/",
                "test_type": "P",
                "description": "Personality assessment designed to identify leadership potential and capabilities",
                "category": "Personality",
                "tags": ["personality", "leadership", "behavioral"]
            },
            "Customer Service": {
                "name": "Customer Service Assessment",
                "url": "https://www.shl.com/solutions/products/customer-service/",
                "test_type": "A",
                "description": "Assessment for customer service roles, measuring communication and problem-solving",
                "category": "Ability",
                "tags": ["customer-service", "communication", "ability"]
            },
            "Data Scientist": {
                "name": "Data Scientist Assessment",
                "url": "https://www.shl.com/solutions/products/data-scientist/",
                "test_type": "K",
                "description": "Assessment for data science roles covering statistics, programming, and analysis",
                "category": "Technical",
                "tags": ["data-science", "programming", "statistical", "knowledge"]
            },
            "Team Player": {
                "name": "Team Player Assessment",
                "url": "https://www.shl.com/solutions/products/team-player/",
                "test_type": "P",
                "description": "Personality-based assessment measuring teamwork, collaboration, and interpersonal skills",
                "category": "Personality",
                "tags": ["personality", "teamwork", "collaboration", "interpersonal"]
            }
        }
        
        for name, data in defaults.items():
            self.assessments[name] = Assessment(**data)
        logger.info("Loaded default fallback catalog")
    
    def _extract_category(self, card) -> str:
        """Extract category from assessment card."""
        category_elem = card.find('span', class_='category')
        if category_elem:
            return category_elem.get_text(strip=True)
        return "General"
    
    def _extract_tags(self, card) -> List[str]:
        """Extract tags from assessment card."""
        tags = []
        tag_elems = card.find_all('span', class_='tag')
        for elem in tag_elems:
            tags.append(elem.get_text(strip=True).lower())
        return tags
    
    def _infer_test_type(self, name: str, description: str, tags: List[str]) -> str:
        """Infer test type from various fields."""
        content = f"{name} {description}".lower()
        
        if any(word in content for word in ["personality", "behavioral", "trait"]):
            return "P"
        elif any(word in content for word in ["knowledge", "technical", "skill", "programming"]):
            return "K"
        elif any(word in content for word in ["ability", "reasoning", "verbal", "numerical"]):
            return "A"
        elif any(word in content for word in ["situational", "judgment", "sj"]):
            return "S"
        else:
            return "O"  # Other
    
    def _save_to_cache(self):
        """Save catalog to JSON cache."""
        try:
            os.makedirs("data", exist_ok=True)
            data = {name: assessment.to_dict() 
                   for name, assessment in self.assessments.items()}
            with open(CATALOG_CACHE_PATH, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Cached catalog to {CATALOG_CACHE_PATH}")
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get_all(self) -> List[Assessment]:
        """Get all assessments."""
        return list(self.assessments.values())
    
    def search(self, query: str) -> List[Assessment]:
        """Search assessments by name, description, or tags."""
        query_lower = query.lower()
        results = []
        
        for assessment in self.assessments.values():
            if (query_lower in assessment.name.lower() or
                query_lower in assessment.description.lower() or
                any(query_lower in tag for tag in assessment.tags)):
                results.append(assessment)
        
        return results
    
    def get_by_category(self, category: str) -> List[Assessment]:
        """Get assessments by category."""
        return [a for a in self.assessments.values() 
                if a.category.lower() == category.lower()]
    
    def get_by_test_type(self, test_type: str) -> List[Assessment]:
        """Get assessments by test type."""
        return [a for a in self.assessments.values() 
                if a.test_type == test_type]


# Global catalog instance
_catalog: Optional[SHLCatalog] = None


def get_catalog() -> SHLCatalog:
    """Get or initialize the global catalog."""
    global _catalog
    if _catalog is None:
        _catalog = SHLCatalog()
    return _catalog
