from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Event(BaseModel):
    actor: str
    action: str
    target: Optional[str] = None  # Target can be None for some milestone events
    roleType: str
    start: str
    end: Optional[str] = None
    context: str
    milestone: bool = False

class CaseMetadata(BaseModel):
    name: str
    id: Optional[str] = None
    type: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None

class ActorHighlight(BaseModel):
    """Flexible highlighting directive from Claude's legal analysis"""
    name: str  # Actor name
    color: str  # Hex color (Claude decides based on legal significance)
    reason: str  # Legal reason for highlighting (e.g., "Unqualified replacement", "Potential insider", "Key whistleblower")

class VisualizationConfig(BaseModel):
    """Claude's legal analysis determining visualization structure"""
    # What to show
    focus_actors: Optional[List[str]] = None  # Specific actors to focus on based on user request
    key_milestone_events: List[str] = []  # Which milestone actions matter legally (Claude decides)

    # How to highlight (Claude determines colors and reasons)
    actor_highlights: List[ActorHighlight] = []  # Actors to highlight with custom colors and legal reasoning

    # Structure and analysis
    sort_strategy: str = "chronological"  # How to order actors: "chronological", "by_role", "by_legal_significance"
    title_override: Optional[str] = None  # Custom title if Claude determines standard title insufficient
    footer_analysis: str = ""  # Claude's legal pattern analysis

    # Metadata about Claude's reasoning
    document_type: str = "general"  # Claude's classification: "fraud_investigation", "employment_dispute", "ma_deal", etc.
    visualization_rationale: str = ""  # Why Claude chose this visualization structure

class TimelineData(BaseModel):
    case: CaseMetadata
    events: List[Event]
    visualization_config: Optional[VisualizationConfig] = None

class ProgressUpdate(BaseModel):
    type: str  # "progress" | "thinking" | "complete" | "error"
    message: str
    data: Optional[dict] = None
