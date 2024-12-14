from pydantic import BaseModel
from typing import List, Dict
from json import JSONEncoder

class EntityLink(BaseModel):
    entity_name: str  # Updated from character to entity_name
    best_appellation: str
    appellations: List[str]
    entity_type: str = "PERSON"  # Default to PERSON, but can be ORG, GPE, etc.
    
class EntityLinkEncoder(JSONEncoder):
    """
    Custom JSON encoder for EntityLink objects.

    Methods:
        default(obj): Override the default method to serialize EntityLink objects.
    """
    def default(self, obj):
        if isinstance(obj, EntityLink):
            return {
                "entity_name": obj.entity_name,  # Updated from character to entity_name
                "appellations": obj.appellations,
                "entity_type": obj.entity_type
            }
        return super().default(obj)
    
    
class ProcessedText(BaseModel):
    """
    Pydantic model for processed text data.

    Attributes:
        synopsis (str): A brief summary of the text.
        entities (List[EntityLink]): List of entities extracted from the text.
        semantic_segments (List[str]): Segments of the text categorized by meaning.
        relationship_structure (List[Dict]): Structure representing relationships between entities.
    """
    synopsis: str
    entities: List[EntityLink]
    semantic_segments: List[str]
    relationship_structure: List[Dict]