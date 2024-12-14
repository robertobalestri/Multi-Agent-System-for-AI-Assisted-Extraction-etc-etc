# arc_progression_service.py

from typing import List, Optional
from src.narrative_storage_management.narrative_models import ArcProgression, NarrativeArc
from src.narrative_storage_management.repositories import ArcProgressionRepository
from src.narrative_storage_management.character_service import CharacterService
import logging
from sqlalchemy import func, select

logger = logging.getLogger(__name__)

class ArcProgressionService:
    """Service to manage arc progressions."""

    def __init__(
        self,
        progression_repository: ArcProgressionRepository,
        character_service: CharacterService
    ):
        self.progression_repository = progression_repository
        self.character_service = character_service
        self.session = progression_repository.session

    def add_or_update_progression(
        self,
        arc: NarrativeArc,
        progression: ArcProgression,
        series: str,
        season: str,
        episode: str
    ) -> ArcProgression:
        """Add or update a progression for an arc in a specific episode."""
        try:
            existing_progression = self.progression_repository.get_single(
                arc.id, series, season, episode
            )

            if existing_progression:
                # Update existing progression
                existing_progression.content = progression.content
                existing_progression.interfering_characters = progression.interfering_characters
                self.progression_repository.add_or_update(existing_progression)
                logger.info(f"Updated progression for arc '{arc.title}' in S{season}E{episode}")
                return existing_progression
            else:
                # Create new progression
                progression.main_arc_id = arc.id
                progression.series = series
                progression.season = season
                progression.episode = episode
                
                # Get next ordinal position within a transaction
                with self.session.begin_nested():
                    # Recalculate all positions based on season/episode order
                    all_progressions = sorted(
                        arc.progressions,
                        key=lambda p: (
                            int(p.season.replace('S', '')), 
                            int(p.episode.replace('E', ''))
                        )
                    )
                    
                    # Find where to insert the new progression
                    new_season_num = int(season.replace('S', ''))
                    new_episode_num = int(episode.replace('E', ''))
                    insert_position = 0
                    
                    for i, prog in enumerate(all_progressions):
                        curr_season_num = int(prog.season.replace('S', ''))
                        curr_episode_num = int(prog.episode.replace('E', ''))
                        
                        if (new_season_num < curr_season_num or 
                            (new_season_num == curr_season_num and new_episode_num < curr_episode_num)):
                            insert_position = i
                            break
                        insert_position = i + 1

                    # Update positions for all affected progressions
                    for i, prog in enumerate(all_progressions[insert_position:], start=insert_position + 1):
                        prog.ordinal_position = i + 1
                        self.progression_repository.add_or_update(prog)

                    # Set position for new progression
                    progression.ordinal_position = insert_position + 1
                    arc.progressions.append(progression)
                    self.progression_repository.add_or_update(progression)
                    
                    logger.info(f"Added new progression for arc '{arc.title}' in S{season}E{episode} with position {progression.ordinal_position}")
                    return progression

        except Exception as e:
            logger.error(f"Error in add_or_update_progression: {e}")
            raise

    def resequence_ordinal_positions(self, arc_id: str):
        """Resequence ordinal positions to ensure they are consecutive and ordered by season/episode."""
        try:
            progressions = self.progression_repository.get_by_arc_id(arc_id)
            
            # Sort progressions by season and episode
            sorted_progressions = sorted(
                progressions,
                key=lambda p: (
                    int(p.season.replace('S', '')), 
                    int(p.episode.replace('E', ''))
                )
            )

            # Update positions
            for i, prog in enumerate(sorted_progressions, 1):
                if prog.ordinal_position != i:
                    prog.ordinal_position = i
                    self.progression_repository.add_or_update(prog)

            logger.info(f"Resequenced {len(progressions)} progressions for arc {arc_id}")

        except Exception as e:
            logger.error(f"Error resequencing progressions: {e}")
            raise

    def get_arc_progression_count(self, arc_id: str) -> int:
        """Get the total number of progressions for an arc."""
        return self.session.exec(
            select(func.count(ArcProgression.id))
            .where(ArcProgression.main_arc_id == arc_id)
        ).scalar() or 0

    def get_progression_by_id(self, progression_id: str) -> Optional[ArcProgression]:
        """Get a progression by its ID."""
        return self.progression_repository.get_by_id(progression_id)
