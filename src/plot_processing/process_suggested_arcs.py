# narrative_storage_main.py

from src.narrative_storage_management.repositories import (
    DatabaseSessionManager,
    NarrativeArcRepository,
    ArcProgressionRepository,
    CharacterRepository
)
from src.narrative_storage_management.character_service import CharacterService
from src.narrative_storage_management.narrative_arc_service import NarrativeArcService
from src.narrative_storage_management.llm_service import LLMService
from src.narrative_storage_management.vector_store_service import VectorStoreService
import logging
import json
from src.narrative_storage_management.narrative_models import NarrativeArc, ArcProgression
from typing import List
import uuid

from src.utils.logger_utils import setup_logging
logger = setup_logging(__name__)

def process_suggested_arcs(suggested_arcs_path: str, series: str, season: str, episode: str):
    # Initialize services
    db_manager = DatabaseSessionManager()
    llm_service = LLMService()
    vector_store_service = VectorStoreService()

    with db_manager.session_scope() as session:
        # Initialize repositories and services
        arc_repository = NarrativeArcRepository(session)
        progression_repository = ArcProgressionRepository(session)
        character_repository = CharacterRepository(session)
        character_service = CharacterService(character_repository)
        narrative_arc_service = NarrativeArcService(
            arc_repository=arc_repository,
            progression_repository=progression_repository,
            character_service=character_service,
            llm_service=llm_service,
            vector_store_service=vector_store_service,
            session=session
        )

        # Process arcs from JSON file
        with open(suggested_arcs_path, 'r') as f:
            suggested_arcs_data = json.load(f)

        added_arcs = []
        for arc_data in suggested_arcs_data:
            added_arc = narrative_arc_service.add_arc(
                arc_data=arc_data,
                series=series,
                season=season,
                episode=episode
            )
            added_arcs.append(added_arc)
        return added_arcs

if __name__ == "__main__":
    process_suggested_arcs('suggested_arcs.json', 'SeriesName', '1', '1')
