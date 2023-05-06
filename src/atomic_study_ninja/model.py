

from pydantic import BaseModel
from typing import Optional

class BaseThing(BaseModel): pass


class Resource(BaseThing):
    id: str
    title: Optional[str]
    url: str
    references: Optional[list[BaseThing]]

class Website(Resource): pass
class Book(Resource): pass
class Video(Resource): pass
class Image(Resource): pass

class  RulePrincipleConcept(BaseThing):
    name: str
    summary: str
    relates_to: Optional[list[BaseThing]]

class TopicField(BaseModel):
    name: str
    rules_principles_concepts: list[RulePrincipleConcept]

class StudyMaterial(BaseModel):
    topic_fields: list[TopicField]
    resources: list[Resource]
