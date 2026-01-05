from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class Substory(BaseModel):
    id: str
    title: str
    headline: str
    brief: str
    graphPath: Optional[str] = None
    section_query: Optional[str] = None

class Chapter(BaseModel):
    id: str
    title: str
    headline: str
    brief: str
    substories: List[Substory]
    total_nodes: Optional[int] = 0

class Story(BaseModel):
    id: str
    title: str
    headline: str
    brief: str
    path: str
    chapters: List[Chapter]

class Node(BaseModel):
    id: str
    name: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    highlight: Optional[bool] = None
    type: Optional[str] = None

    class Config:
        extra = "allow"

class Link(BaseModel):
    id: str
    sourceId: str
    targetId: str
    title: Optional[str] = None
    label: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    curvature: Optional[float] = None
    curveRotation: Optional[float] = None

    class Config:
        extra = "allow"

class GraphData(BaseModel):
    nodes: List[Node]
    links: List[Link]

class StoriesResponse(BaseModel):
    stories: List[Story]
