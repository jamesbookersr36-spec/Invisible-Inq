from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

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

# Authentication Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    auth_provider: Optional[str] = "local"  # local, google

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None

class GoogleAuthRequest(BaseModel):
    credential: str  # Google ID token

# User Activity Tracking Models
class ActivityType(BaseModel):
    page_view: str = "page_view"
    section_view: str = "section_view"
    graph_interaction: str = "graph_interaction"
    search: str = "search"

class UserActivityCreate(BaseModel):
    user_id: Optional[str] = None  # Optional for anonymous users
    session_id: str
    activity_type: str
    page_url: Optional[str] = None
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    duration_seconds: Optional[int] = None
    metadata: Optional[Dict] = None

class UserActivityResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    session_id: str
    activity_type: str
    page_url: Optional[str] = None
    section_id: Optional[str] = None
    section_title: Optional[str] = None
    duration_seconds: Optional[int] = None
    metadata: Optional[Dict] = None
    timestamp: datetime
    user_email: Optional[str] = None
    user_name: Optional[str] = None

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str
    admin_key: Optional[str] = None  # Optional admin verification key
