

from pydantic import BaseModel, UUID4, Field
from uuid import uuid4, UUID
from typing import Optional
from enum import StrEnum, auto
import ruamel.yaml

yaml = ruamel.yaml.YAML()
yaml.indent(mapping=2, sequence=4, offset=2)
class BaseThing(BaseModel):
    id: str = Field(default_factory=lambda : str(uuid4()))
    name: str
    url: str | None = ""

class Relationship(StrEnum):
    EXPLAINS = auto()
    RELATES_TO = auto()
    TEACHES = auto()

class Resource(BaseThing):
    url: str


class Relates(BaseModel):
    r_from: str
    r_to: str
    rel_type: Relationship


# class Website(Resource): pass
# class Book(Resource): pass
# class Video(Resource): pass
# class Image(Resource): pass

class  RulePrincipleConcept(BaseThing):
    description: str | None = ""

class  Subject(BaseThing):
    description: str | None = ""

class SubjectUniverse(BaseModel):
    name: str
    rules_principles_concepts: list[RulePrincipleConcept]
    subjects_topics: list[Subject]

class StudyMaterial(BaseModel):
    topic_fields: list[SubjectUniverse]
    resources: list[Resource]
    relates: list[Relates] = []
