# character_service.py

from sqlite3 import IntegrityError
from typing import List, Optional, Union
from src.narrative_storage_management.narrative_models import Character, CharacterAppellation, NarrativeArc, ArcProgression
from src.narrative_storage_management.repositories import CharacterRepository
from src.plot_processing.plot_processing_models import EntityLink
import logging

from src.utils.logger_utils import setup_logging
logger = setup_logging(__name__)

class CharacterService:
    """Service to manage character-related operations."""

    def __init__(self, character_repository: CharacterRepository):
        self.character_repository = character_repository

    def add_or_update_character(self, entity: EntityLink, series: str) -> Optional[Union[Character, List[Character]]]:
        """Add a new character or update an existing one based on the EntityLink."""
        # Skip invalid entity names
        if len(entity.entity_name.strip()) <= 1:
            logger.warning(f"Skipping invalid entity name: '{entity.entity_name}'")
            return None

        try:
            # Ensure entity_name is normalized
            normalized_entity_name = self._normalize_name(entity.entity_name)
            entity.entity_name = normalized_entity_name

            # Normalize and validate appellations
            validated_appellations = set()
            for appellation in entity.appellations:
                if appellation and len(appellation.strip()) > 1:
                    validated_appellations.add(appellation.strip())
            
            # Ensure best_appellation is valid and included
            if entity.best_appellation and len(entity.best_appellation.strip()) > 1:
                validated_appellations.add(entity.best_appellation.strip())
            elif validated_appellations:
                # If no valid best_appellation, use the first valid appellation
                entity.best_appellation = next(iter(validated_appellations))
            else:
                logger.warning(f"No valid appellations found for entity: {entity.entity_name}")
                return None

            # First try to find existing character by normalized entity_name
            existing_character = self.character_repository.get_by_entity_name(normalized_entity_name, series)
            
            # If not found by entity_name, try to find by any appellation
            if not existing_character:
                for appellation in validated_appellations:
                    existing_character = self.character_repository.get_character_by_appellation(
                        appellation, 
                        series
                    )
                    if existing_character:
                        break

            if existing_character:
                # Update existing character
                # Clear existing appellations to avoid duplicates
                existing_character.appellations.clear()
                
                # Update best appellation
                existing_character.best_appellation = entity.best_appellation

                # Add all validated appellations
                for appellation in validated_appellations:
                    # Check if appellation is used by another character
                    other_character = self.character_repository.get_character_by_appellation(appellation, series)
                    if other_character and other_character.entity_name != existing_character.entity_name:
                        logger.warning(
                            f"Appellation '{appellation}' is already used by character "
                            f"'{other_character.entity_name}', skipping."
                        )
                        continue
                    
                    new_appellation = CharacterAppellation(
                        appellation=appellation,
                        character_id=existing_character.entity_name
                    )
                    existing_character.appellations.append(new_appellation)

                self.character_repository.update(existing_character)
                logger.info(
                    f"Updated existing character: {existing_character.entity_name} "
                    f"with appellations: {[app.appellation for app in existing_character.appellations]}"
                )
                return existing_character
            else:
                # Create new character
                new_character = Character(
                    entity_name=normalized_entity_name,
                    best_appellation=entity.best_appellation,
                    series=series
                )

                # Add all validated appellations
                for appellation in validated_appellations:
                    # Check if appellation is already used
                    existing_char = self.character_repository.get_character_by_appellation(appellation, series)
                    if existing_char:
                        logger.warning(
                            f"Appellation '{appellation}' is already used by character "
                            f"'{existing_char.entity_name}', skipping."
                        )
                        continue

                    new_appellation = CharacterAppellation(
                        appellation=appellation,
                        character_id=new_character.entity_name
                    )
                    new_character.appellations.append(new_appellation)

                if not new_character.appellations:
                    logger.warning(f"No valid appellations for character: {entity.entity_name}")
                    return None

                self.character_repository.add(new_character)
                logger.info(
                    f"Added new character: {new_character.entity_name} "
                    f"with appellations: {[app.appellation for app in new_character.appellations]}"
                )
                return new_character

        except IntegrityError as e:
            logger.error(f"Database integrity error when processing character {entity.entity_name}: {e}")
            self.character_repository.session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error when processing character {entity.entity_name}: {e}")
            self.character_repository.session.rollback()
            raise

    def get_characters_by_appellations(self, appellations: List[str], series: str) -> List[Character]:
        """Get characters by matching their appellations."""
        # Clean and split any semicolon-separated appellations
        cleaned_appellations = []
        for appellation in appellations:
            if isinstance(appellation, str):  # Ensure we're working with a string
                # Split by semicolon and clean each part
                if ';' in appellation:
                    cleaned_appellations.extend([
                        name.strip() 
                        for name in appellation.split(';') 
                        if name.strip()
                    ])
                else:
                    cleaned_appellations.append(appellation.strip())

        # Get characters by appellations
        characters = self.character_repository.get_by_appellations(cleaned_appellations, series)
        
        if not characters:
            logger.warning(f"No characters found for appellations: {cleaned_appellations}")
        else:
            logger.info(f"Found {len(characters)} characters for appellations: {cleaned_appellations}")
        
        return characters

    def link_characters_to_arc(self, characters: List[Character], arc: Optional[NarrativeArc]):
        if not arc:
            return  # Handle linking within add_arc

        existing_ids = {c.entity_name for c in arc.main_characters}
        new_characters = [c for c in characters if c.entity_name not in existing_ids]
        if new_characters:
            arc.main_characters.extend(new_characters)
            for character in new_characters:
                if arc not in character.main_narrative_arcs:
                    character.main_narrative_arcs.append(arc)
            logger.info(f"Linked {len(new_characters)} characters to arc '{arc.title}'")

    def link_characters_to_progression(self, characters: List[Character], progression: ArcProgression):
        existing_ids = {c.entity_name for c in progression.interfering_characters}
        new_characters = [c for c in characters if c.entity_name not in existing_ids]
        if new_characters:
            progression.interfering_characters.extend(new_characters)
            for character in new_characters:
                if progression not in character.interfering_progressions:
                    character.interfering_progressions.append(progression)
            logger.info(f"Linked {len(new_characters)} characters to progression in S{progression.season}E{progression.episode}")

    def delete_character(self, entity_name: str, series: str) -> bool:
        """
        Delete a character and update all related arcs and progressions.
        Returns True if successful, False otherwise.
        """
        try:
            character = self.character_repository.get_by_entity_name(entity_name, series)
            if not character:
                return False

            # Remove character from main characters in arcs
            for arc in character.main_narrative_arcs:
                arc.main_characters.remove(character)

            # Remove character from interfering characters in progressions
            for progression in character.interfering_progressions:
                progression.interfering_characters.remove(character)

            # Delete the character
            self.character_repository.delete(character)
            return True

        except Exception as e:
            logger.error(f"Error deleting character {entity_name}: {e}")
            raise

    def merge_characters(
        self,
        character1_id: str,
        character2_id: str,
        series: str,
        keep_character: str = 'character1'
    ) -> bool:
        """
        Merge two characters, keeping the data from the specified character.
        
        Args:
            character1_id: Entity name of the first character
            character2_id: Entity name of the second character
            series: Series identifier
            keep_character: Which character to keep ('character1' or 'character2')
        
        Returns:
            bool: True if merge was successful, False otherwise
        """
        # Get both characters
        char1 = self.character_repository.get_by_entity_name(character1_id, series)
        char2 = self.character_repository.get_by_entity_name(character2_id, series)

        if not char1 or not char2:
            return False

        # Determine which character to keep based on keep_character parameter
        kept_char = char1 if keep_character == 'character1' else char2
        merged_char = char2 if keep_character == 'character1' else char1

        # Merge appellations
        merged_appellations = set([app.appellation for app in kept_char.appellations])
        merged_appellations.update([app.appellation for app in merged_char.appellations])

        # Update the kept character with merged appellations
        kept_char.appellations = [
            CharacterAppellation(
                appellation=app,
                character_id=kept_char.entity_name
            )
            for app in merged_appellations
        ]

        # Update any references from narrative arcs
        for arc in merged_char.main_narrative_arcs:
            if kept_char not in arc.main_characters:
                arc.main_characters.append(kept_char)

        # Update any references from progressions
        for prog in merged_char.interfering_progressions:
            if kept_char not in prog.interfering_characters:
                prog.interfering_characters.append(kept_char)

        # Delete the other character
        self.character_repository.delete(merged_char)

        return True

    def _normalize_name(self, name: str) -> str:
        """Helper method to normalize character names."""
        return name.lower().replace(' ', '_')
