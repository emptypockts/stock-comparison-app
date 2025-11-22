
from langchain.tools import BaseTool
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import Field,BaseModel
from outils import get_today_str
from typing_extensions import Optional, Annotated, List, Sequence, TypedDict
import operator

class AgentInputState(MessagesState):
    """Input state for the full agent - only contains messages from user input."""
    pass

class AgentState(MessagesState):
    """
    Main state for the full multi-agent research system.
    
    Extends MessagesState with additional fields for research coordination.
    Note: Some fields are duplicated across different state classes for proper
    state management between subgraphs and the main workflow.
    """

    # Research brief generated from user conversation history
    research_brief: Optional[str]
    # Messages exchanged with the supervisor agent for coordination
    supervisor_messages: Annotated[Sequence[BaseMessage], add_messages]
    # Raw unprocessed research notes collected during the research phase
    raw_notes: Annotated[list[str], operator.add] = []
    # Processed and structured notes ready for report generation
    notes: Annotated[list[str], operator.add] = []
    # Final formatted research report
    final_report: str

# ===== STRUCTURED OUTPUT SCHEMAS =====

class ClarifyWithUser(BaseModel):
    """Schema for user clarification decision and questions."""
    
    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question.",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
    )

class ResearchQuestion(BaseModel):
    """Schema for structured research brief generation."""
    
    research_brief: str = Field(
        description="A research question that will be used to guide the research.",
    )


#====quant======
class Section(BaseModel):
    name:str=Field(
        description="this section contains a financial summary of highlights and red flags identified in the text."
    )
    key_metrics:List[str]=Field(
        description="contains the metrics or indicators to focus on while analyzing this report"
    )
    reasoning_focus:str=Field(
        description= "specify the type of focus, anomaly detection, highlights or pattern detection"
    )

class Sections(BaseModel):
    sections: List[Section]=Field(
        description="sections of the report."
    )

class State(TypedDict):
    report:str
    sections:list[Section]
    completed_sections:Annotated[
        list,operator.add
    ]
    final_report:str

class QuantState(TypedDict):
    section:Section
    completed_sections:Annotated[list,operator.add]



