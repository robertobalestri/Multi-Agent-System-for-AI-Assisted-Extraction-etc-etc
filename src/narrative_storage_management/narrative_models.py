# narrative_models.py

from __future__ import annotations
from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship
import uuid
from sqlalchemy import UniqueConstraint, func

from src.utils.logger_utils import setup_logging
logger = setup_logging(__name__)

class ArcMainCharacterLink(SQLModel, table=True):
    """Junction table for main characters in narrative arcs."""
    __tablename__ = "arc_main_characters"

    arc_id: str = Field(foreign_key="narrativearc.id", primary_key=True)
    character_id: str = Field(foreign_key="character.entity_name", primary_key=True)

class ProgressionInterferingCharacterLink(SQLModel, table=True):
    """Junction table for interfering characters in arc progressions."""
    __tablename__ = "progression_interfering_characters"

    progression_id: str = Field(foreign_key="arcprogression.id", primary_key=True)
    character_id: str = Field(foreign_key="character.entity_name", primary_key=True)

class CharacterAppellation(SQLModel, table=True):
    """Model representing a character's appellation."""
    __tablename__ = "character_appellation"

    appellation: str = Field(primary_key=True)
    character_id: str = Field(foreign_key="character.entity_name")
    character: Optional["Character"] = Relationship(back_populates="appellations",sa_relationship=relationship(
        "Character",
        back_populates="appellations",
        lazy="selectin"
    ))

class Character(SQLModel, table=True):
    """Model representing a character in the series."""
    __tablename__ = "character"

    entity_name: str = Field(primary_key=True)
    best_appellation: str
    series: str = Field(index=True)

    # Relationships
    appellations: List["CharacterAppellation"] = Relationship(
        back_populates="character",
        sa_relationship=relationship(
            "CharacterAppellation",
            back_populates="character",
            cascade="all, delete-orphan"
        )
    )

    main_narrative_arcs: List["NarrativeArc"] = Relationship(
        back_populates="main_characters",
        sa_relationship=relationship(
            "NarrativeArc",
            secondary="arc_main_characters",
            back_populates="main_characters",
            lazy="selectin"
        )
    )

    interfering_progressions: List["ArcProgression"] = Relationship(
        back_populates="interfering_characters",
        sa_relationship=relationship(
            "ArcProgression",
            secondary="progression_interfering_characters",
            back_populates="interfering_characters",
            lazy="selectin"
        )
    )

class NarrativeArc(SQLModel, table=True):
    """Model representing a narrative arc."""
    __tablename__ = "narrativearc"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str
    arc_type: str
    description: str
    series: str

    # Relationships
    main_characters: List["Character"] = Relationship(
        back_populates="main_narrative_arcs",
        sa_relationship=relationship(
            "Character",
            secondary="arc_main_characters",
            back_populates="main_narrative_arcs",
            lazy="selectin"
        )
    )

    progressions: List["ArcProgression"] = Relationship(
        back_populates="narrative_arc",
        sa_relationship=relationship(
            "ArcProgression",
            back_populates="narrative_arc",
            cascade="all, delete-orphan",
            lazy="selectin"
        )
    )

class ArcProgression(SQLModel, table=True):
    """Model representing a progression within a narrative arc."""
    __tablename__ = "arcprogression"

    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    main_arc_id: str = Field(foreign_key="narrativearc.id")
    content: str
    series: str
    season: str
    episode: str
    ordinal_position: int = Field(default=1, nullable=False)

    # Relationships
    interfering_characters: List["Character"] = Relationship(
        back_populates="interfering_progressions",
        sa_relationship=relationship(
            "Character",
            secondary="progression_interfering_characters",
            back_populates="interfering_progressions",
            lazy="selectin"
        )
    )

    narrative_arc: Optional["NarrativeArc"] = Relationship(
        back_populates="progressions",
        sa_relationship=relationship(
            "NarrativeArc",
            back_populates="progressions",
            lazy="selectin"
        )
    )
