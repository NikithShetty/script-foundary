# System Architecture Document

## 1. Overview

### System Purpose
Multi-agent educational script generation system that enables educators to interact with AI agents through a chat interface to collaboratively gather information and generate curriculum-aligned educational video scripts.

### Architecture Pattern
**LangGraph-based workflow orchestration** with custom REST API layer for conversation management.

### Key Components
- **Orchestrator Agent**: Manages conversation flow and coordinates all sub-agents
- **Subject-specific Script Generator Agents**: Specialized agents for Science, Math, English, etc.
- **Fact Checker Agent**: Verifies accuracy of generated scripts
- **Curriculum Agent**: Integrates with CurricuLLM-AU API for curriculum alignment
- **Information Gathering Agents**: Misconception checker, Cultural Safety, Accessibility

---

## 2. System Flow

### High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    REST API Layer                             │
│              POST /chat/sessions/{id}/messages                │
└──────────────────────────┬────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                         │
│                                                               │
│  ┌──────────────┐                                             │
│  │ Conversation │ ◄──┐                                       │
│  │    Node      │    │ (loop if more info needed)            │
│  └──────┬───────┘    │                                       │
│         │             │                                       │
│         ▼             │                                       │
│  ┌─────────────────┐ │                                       │
│  │   Information   │ │                                       │
│  │   Gathering     │─┘                                       │
│  └──────┬──────────┘                                         │
│         │                                                    │
│         ├──► Curriculum Agent (if needed)                     │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────┐                                         │
│  │ Check: Ready?   │───No──► Conversation                   │
│  └──────┬──────────┘                                         │
│         │ Yes                                                │
│         ▼                                                    │
│  ┌─────────────────┐                                         │
│  │   Script        │ ◄──┐                                   │
│  │  Generation     │    │ (refinement loop)                 │
│  └──────┬──────────┘    │                                   │
│         │               │                                   │
│         ▼               │                                   │
│  ┌─────────────────┐   │                                   │
│  │   Fact Check    │───┘                                   │
│  │     Node        │                                        │
│  └─────────────────┘                                        │
│         │                                                    │
│         ├──► Confidence < 80%? ──► Refine                    │
│         │                                                    │
│         └──► Confidence ≥ 80%? ──► Complete                 │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                    Return to Educator
```

### Step-by-Step Flow Description

1. **Educator Provides Initial Input**
   - Educator sends message via REST API: `POST /api/v1/chat/sessions/{id}/messages`
   - Message contains learning objective or topic information
   - Workflow enters at `conversation_node`

2. **Orchestrator Coordinates Conversation**
   - `conversation_node` extracts structured information from natural language
   - Updates `SessionState` with extracted fields (topic, year_level, learning_objective, subject)
   - Determines what information is still missing
   - Generates appropriate follow-up question or confirmation

3. **Information Gathering Phase**
   - `information_gathering_node` checks completeness of required fields
   - If curriculum data needed → routes to `curriculum_agent_node`
   - Curriculum agent calls CurricuLLM-AU API
   - Returns to information gathering to update state

4. **Decision Point: Ready to Generate?**
   - Conditional edge checks if all required fields present:
     - Required: `topic`, `year_level`, `learning_objective`
     - Optional: `subject`, `curriculum_outcomes`
   - If not ready → loop back to `conversation_node`
   - If ready → proceed to `script_generation_node`

5. **Script Generation**
   - `script_generation_node` selects appropriate subject-specific agent
   - Agent generates script using:
     - Collected information
     - Curriculum outcomes
     - Misconceptions
     - FAME framework (Fading, Alternating, Mistakes, Explanation)
   - Script stored in state

6. **Fact Checking**
   - `fact_checking_node` extracts factual claims from script
   - Verifies each claim against Wikipedia/Wikidata
   - Calculates confidence score
   - Determines if refinement needed (threshold: 80%)

7. **Refinement Loop (if needed)**
   - If confidence < 80% and iterations < max (default: 3):
     - Routes back to `script_generation_node`
     - Includes fact-check issues in context
     - Script generator refines script
     - Loop continues until confidence threshold met or max iterations reached

8. **Return Completed Script**
   - When status = "completed", script available via REST API
   - `GET /api/v1/chat/sessions/{id}/script` returns full `ScriptOutput`

---

## 3. Agent Architecture

### Agent Hierarchy

```
Orchestrator Agent (Main Coordinator)
    │
    ├──► Curriculum Agent (Information Service)
    │       └──► CurricuLLM-AU API
    │
    ├──► Information Gathering Agents
    │       ├──► Misconception Agent
    │       ├──► Cultural Safety Agent
    │       └──► Accessibility Agent
    │
    ├──► Subject-Specific Script Generator Agents
    │       ├──► Science Script Agent
    │       ├──► Math Script Agent
    │       ├──► English Script Agent
    │       └──► Default Script Agent (fallback)
    │
    └──► Fact Checker Agent
            └──► Wikipedia/Wikidata APIs
```

### Agent Responsibilities

#### Orchestrator Agent
- **Primary Role**: Conversation management and workflow coordination
- **Responsibilities**:
  - Extract structured data from natural language educator input
  - Determine what information is missing
  - Generate appropriate follow-up questions
  - Coordinate between all sub-agents
  - Make decisions about workflow progression
  - Manage session state transitions

#### Curriculum Agent
- **Primary Role**: Curriculum alignment and information retrieval
- **Responsibilities**:
  - Call CurricuLLM-AU API with topic, year_level, subject
  - Retrieve curriculum outcomes and codes
  - Fetch prerequisite knowledge
  - Can be called by orchestrator or script generator as needed
- **Integration**: Uses existing `app/services/curriculum_api.py`

#### Subject-Specific Script Generator Agents
- **Primary Role**: Generate educational scripts tailored to specific subjects
- **Responsibilities**:
  - Science Agent: Emphasizes experiments, observations, scientific method
  - Math Agent: Focuses on problem-solving, step-by-step solutions
  - English Agent: Emphasizes narrative structure, language skills
  - Default Agent: General-purpose script generation
- **Selection Logic**: Based on `state["subject"]` field

#### Fact Checker Agent
- **Primary Role**: Verify factual accuracy of generated scripts
- **Responsibilities**:
  - Extract factual claims from script text
  - Verify claims against Wikipedia/Wikidata
  - Calculate confidence scores
  - Identify low-confidence claims
  - Provide feedback for refinement
- **Integration**: Uses existing `app/services/fact_check_service.py`

#### Information Gathering Agents (Supporting)
- **Misconception Agent**: Identifies common student misconceptions
- **Cultural Safety Agent**: Checks for cultural sensitivity
- **Accessibility Agent**: Generates accessibility features

---

## 4. LangGraph Workflow Design

### State Definition

```python
# Pseudo code structure
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class SessionState(TypedDict):
    """State shared across all nodes in the workflow."""
    
    # Session identification
    session_id: str
    status: str  # "collecting_info", "generating", "fact_checking", "refining", "completed", "failed"
    
    # Conversation management
    messages: Annotated[List[BaseMessage], add_messages]  # LangGraph message handling
    user_input: Optional[str]  # Latest user message
    
    # Collected information (from educator)
    learning_objective: Optional[str]
    topic: Optional[str]
    year_level: Optional[int]
    subject: Optional[str]  # "Science", "Math", "English", etc.
    
    # Supporting information (from agents)
    curriculum_outcomes: List[Dict[str, Any]]
    curriculum_codes: List[str]
    prerequisites: List[str]
    misconceptions: List[Dict[str, Any]]
    cultural_safety_flags: List[str]
    accessibility_metadata: Dict[str, Any]
    
    # Generated content
    script: Optional[str]
    script_scenes: List[Dict[str, Any]]
    
    # Fact checking results
    fact_check_results: Dict[str, Any]
    confidence_score: Optional[float]  # 0.0 to 1.0
    refinement_iterations: int  # Track refinement count
    
    # Control flow flags
    ready_to_generate: bool
    needs_refinement: bool
    max_refinement_iterations: int  # Default: 3
    
    # Error handling
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
```

### Node Definitions

#### conversation_node
```python
async def conversation_node(state: SessionState) -> SessionState:
    """
    Handle conversation with educator.
    Extracts information and generates responses.
    """
    # Extract user message
    user_message = state["user_input"]
    messages = state["messages"]
    
    # Add user message to conversation history
    messages.append(HumanMessage(content=user_message))
    
    # Use LLM to extract structured information
    extracted_info = await extract_information_from_message(
        message=user_message,
        current_state=state
    )
    
    # Update state with extracted fields
    if extracted_info.get("topic"):
        state["topic"] = extracted_info["topic"]
    if extracted_info.get("year_level"):
        state["year_level"] = extracted_info["year_level"]
    if extracted_info.get("learning_objective"):
        state["learning_objective"] = extracted_info["learning_objective"]
    if extracted_info.get("subject"):
        state["subject"] = extracted_info["subject"]
    
    # Generate appropriate response
    response = await generate_conversation_response(
        state=state,
        missing_fields=identify_missing_fields(state)
    )
    
    # Add assistant response to conversation
    messages.append(AIMessage(content=response))
    state["messages"] = messages
    state["status"] = "collecting_info"
    
    return state
```

#### curriculum_agent_node
```python
async def curriculum_agent_node(state: SessionState) -> SessionState:
    """
    Fetch curriculum information from CurricuLLM-AU API.
    Can be called by orchestrator or script generator.
    """
    topic = state.get("topic")
    year_level = state.get("year_level")
    subject = state.get("subject")
    
    # Validate required fields
    if not topic or not year_level:
        state["warnings"].append("Cannot fetch curriculum: missing topic or year_level")
        return state
    
    # Call curriculum API (existing service)
    outcomes = get_curriculum_outcomes(
        topic=topic,
        year_level=year_level,
        subject=subject
    )
    
    # Update state
    state["curriculum_outcomes"] = outcomes
    state["curriculum_codes"] = [
        outcome.get("code", "") 
        for outcome in outcomes 
        if outcome.get("code")
    ]
    
    # Get prerequisites if available
    prerequisites = get_prerequisites(topic, year_level)
    state["prerequisites"] = prerequisites
    
    return state
```

#### information_gathering_node
```python
async def information_gathering_node(state: SessionState) -> SessionState:
    """
    Orchestrator checks what information is needed and coordinates gathering.
    """
    # Check completeness of required fields
    has_topic = bool(state.get("topic"))
    has_year_level = bool(state.get("year_level"))
    has_learning_objective = bool(state.get("learning_objective"))
    has_curriculum = len(state.get("curriculum_outcomes", [])) > 0
    
    # If we have basic info but no curriculum, mark for curriculum fetch
    if has_topic and has_year_level and not has_curriculum:
        state["status"] = "gathering_curriculum"
        return state
    
    # Check if all required info is present
    required_fields = {
        "topic": has_topic,
        "year_level": has_year_level,
        "learning_objective": has_learning_objective
    }
    
    all_ready = all(required_fields.values())
    state["ready_to_generate"] = all_ready
    
    if all_ready:
        state["status"] = "ready_to_generate"
    else:
        state["status"] = "collecting_info"
    
    return state
```

#### script_generation_node
```python
async def script_generation_node(state: SessionState) -> SessionState:
    """
    Generate script using subject-specific agent.
    Can be called for initial generation or refinement.
    """
    state["status"] = "generating"
    
    # Select appropriate script generator based on subject
    subject = state.get("subject", "").lower()
    script_generator = get_script_generator_for_subject(subject)
    # Returns: ScienceAgent, MathAgent, EnglishAgent, or DefaultAgent
    
    # Build context for script generation
    context = {
        "topic": state["topic"],
        "year_level": state["year_level"],
        "learning_objective": state["learning_objective"],
        "subject": state.get("subject"),
        "curriculum_outcomes": state.get("curriculum_outcomes", []),
        "curriculum_codes": state.get("curriculum_codes", []),
        "misconceptions": state.get("misconceptions", []),
    }
    
    # If this is a refinement, include fact-check feedback
    if state.get("needs_refinement"):
        context["fact_check_issues"] = state.get("fact_check_results", {}).get("issues", [])
        context["low_confidence_claims"] = state.get("fact_check_results", {}).get("low_confidence_claims", [])
        context["refinement_notes"] = "Address the following fact-check issues in the script"
    
    # Generate script using selected agent
    script_result = await script_generator.generate(context)
    
    # Update state
    state["script"] = script_result["script"]
    state["script_scenes"] = script_result.get("scenes", [])
    state["status"] = "script_generated"
    
    return state
```

#### fact_checking_node
```python
async def fact_checking_node(state: SessionState) -> SessionState:
    """
    Verify factual accuracy of generated script.
    """
    state["status"] = "fact_checking"
    
    script = state.get("script", "")
    if not script:
        state["errors"].append("No script available for fact-checking")
        state["status"] = "failed"
        return state
    
    # Extract factual claims from script
    claims = extract_factual_claims(script)
    
    # Check each claim
    results = []
    verified_count = 0
    
    for claim in claims:
        result = check_fact(claim)  # Uses existing fact_check_service
        results.append(result)
        if result.get("verified", False):
            verified_count += 1
    
    # Calculate confidence score
    confidence_score = (verified_count / len(claims)) if claims else 1.0
    
    # Update state with results
    state["fact_check_results"] = {
        "claims": results,
        "confidence_score": confidence_score,
        "total_claims": len(claims),
        "verified_claims": verified_count,
        "issues": [r for r in results if not r.get("verified", False)],
        "low_confidence_claims": [
            r for r in results 
            if r.get("confidence", 0) < 0.5
        ]
    }
    state["confidence_score"] = confidence_score
    
    # Determine if refinement is needed
    confidence_threshold = 0.8  # 80%
    state["needs_refinement"] = confidence_score < confidence_threshold
    
    if state["needs_refinement"]:
        state["refinement_iterations"] = state.get("refinement_iterations", 0) + 1
        state["status"] = "needs_refinement"
    else:
        state["status"] = "completed"
    
    return state
```

### Edge Definitions

#### Workflow Construction
```python
def create_script_generation_workflow():
    """Create the LangGraph workflow for script generation."""
    
    workflow = StateGraph(SessionState)
    
    # Add all nodes
    workflow.add_node("conversation", conversation_node)
    workflow.add_node("curriculum_agent", curriculum_agent_node)
    workflow.add_node("information_gathering", information_gathering_node)
    workflow.add_node("script_generation", script_generation_node)
    workflow.add_node("fact_checking", fact_checking_node)
    
    # Set entry point
    workflow.set_entry_point("conversation")
    
    # Sequential edges
    workflow.add_edge("conversation", "information_gathering")
    workflow.add_edge("curriculum_agent", "information_gathering")
    workflow.add_edge("script_generation", "fact_checking")
    
    # Conditional edge: Information Gathering → Check readiness
    workflow.add_conditional_edges(
        "information_gathering",
        check_if_ready_to_generate,
        {
            "continue_conversation": "conversation",  # Need more info
            "gather_curriculum": "curriculum_agent",  # Need curriculum
            "ready": "script_generation"  # All info ready
        }
    )
    
    # Conditional edge: Fact Checking → Refine or Complete
    workflow.add_conditional_edges(
        "fact_checking",
        check_fact_check_results,
        {
            "refine": "script_generation",  # Needs refinement
            "complete": END  # Script is ready
        }
    )
    
    return workflow.compile()
```

---

## 5. State Management

### State Persistence Strategy

**Storage Options**:
1. **Redis** (Recommended for production): Fast, supports TTL, good for session management
2. **PostgreSQL** (Current database): Persistent storage, supports complex queries
3. **In-memory** (Development): Simple dict storage for testing

**State Lifecycle**:
```
Session Created → State Initialized → State Updated (per node) → State Persisted → Session Completed
```

**State Transitions**:
- `collecting_info` → `gathering_curriculum` → `ready_to_generate` → `generating` → `fact_checking` → `completed`
- `fact_checking` → `needs_refinement` → `generating` (loop)
- Any state → `failed` (on error)

### State Recovery

- On workflow restart, load state from storage
- Resume from last completed node
- Handle partial state gracefully (missing fields)

---

## 6. REST API Design

### Endpoint Specifications

#### POST /api/v1/chat/sessions
**Purpose**: Create a new conversation session

**Request**: Empty body

**Response**:
```json
{
    "session_id": "uuid",
    "status": "collecting_info",
    "created_at": "timestamp"
}
```

**Implementation**:
- Generate unique session_id
- Initialize SessionState with default values
- Store in Redis/PostgreSQL
- Return session_id

---

#### POST /api/v1/chat/sessions/{session_id}/messages
**Purpose**: Send message to orchestrator and process through workflow

**Request**:
```json
{
    "message": "I want to create a script about photosynthesis for year 7"
}
```

**Response**:
```json
{
    "message_id": "uuid",
    "role": "assistant",
    "content": "Great! I'm gathering information...",
    "session_id": "uuid",
    "collected_data": {
        "topic": "photosynthesis",
        "year_level": 7,
        "learning_objective": null,
        "subject": null
    },
    "status": "collecting_info",
    "missing_fields": ["learning_objective"],
    "ready_to_generate": false,
    "agent_actions": [
        {
            "agent": "curriculum_agent",
            "action": "fetching_curriculum",
            "status": "in_progress"
        }
    ]
}
```

**Implementation**:
- Load session state from storage
- Update state with user message
- Invoke LangGraph workflow: `await workflow.ainvoke(state, config)`
- Save updated state
- Extract latest assistant message
- Return response with current state

---

#### GET /api/v1/chat/sessions/{session_id}
**Purpose**: Get current session status and collected data

**Response**:
```json
{
    "session_id": "uuid",
    "status": "generating",
    "collected_data": {
        "topic": "photosynthesis",
        "year_level": 7,
        "learning_objective": "Students understand...",
        "subject": "Science"
    },
    "missing_fields": [],
    "conversation_history": [...],
    "generation_progress": {
        "current_step": "script_generation",
        "current_agent": "science_script_agent",
        "progress": 0.65
    },
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

---

#### GET /api/v1/chat/sessions/{session_id}/script
**Purpose**: Retrieve generated script when status is "completed"

**Response**:
```json
{
    "session_id": "uuid",
    "topic": "photosynthesis",
    "year_level": 7,
    "learning_objective": "...",
    "script": "Full script text...",
    "scenes": [...],
    "curriculum": {
        "outcomes": [...],
        "codes": [...]
    },
    "fact_checking": {
        "confidence_score": 0.85,
        "results": [...]
    },
    "misconceptions": {...},
    "cultural_safety": {...},
    "accessibility": {...}
}
```

**Error Handling**:
- If status != "completed": Return 400 with current status
- If session not found: Return 404

---

#### GET /api/v1/chat/sessions/{session_id}/generation/status
**Purpose**: Poll for generation status (for long-running operations)

**Response**:
```json
{
    "status": "fact_checking",
    "progress": 0.75,
    "current_step": "fact_checking",
    "current_agent": "fact_checker_agent",
    "estimated_time_remaining": 15,
    "errors": [],
    "warnings": []
}
```

---

### Request/Response Models (Pseudo)

```python
# Request Models
class ChatRequest(BaseModel):
    message: str

# Response Models
class ChatResponse(BaseModel):
    message_id: str
    role: Literal["assistant"]
    content: str
    session_id: str
    collected_data: Dict[str, Any]
    status: str
    missing_fields: List[str]
    ready_to_generate: bool
    agent_actions: List[Dict[str, Any]]

class SessionStatus(BaseModel):
    session_id: str
    status: str
    collected_data: Dict[str, Any]
    missing_fields: List[str]
    generation_progress: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
```

---

## 7. Conditional Logic

### check_if_ready_to_generate

```python
def check_if_ready_to_generate(state: SessionState) -> str:
    """
    Determine next step after information gathering.
    Returns: "continue_conversation" | "gather_curriculum" | "ready"
    """
    # Check if we have topic and year_level but no curriculum
    if state.get("topic") and state.get("year_level") and \
       not state.get("curriculum_outcomes"):
        return "gather_curriculum"
    
    # Check if all required fields are present
    required_fields = ["topic", "year_level", "learning_objective"]
    all_present = all(state.get(field) for field in required_fields)
    
    if all_present:
        return "ready"
    
    return "continue_conversation"
```

### check_fact_check_results

```python
def check_fact_check_results(state: SessionState) -> str:
    """
    Determine if script needs refinement based on fact-check results.
    Returns: "refine" | "complete"
    """
    max_iterations = state.get("max_refinement_iterations", 3)
    current_iterations = state.get("refinement_iterations", 0)
    
    # Check if we've exceeded max iterations
    if current_iterations >= max_iterations:
        return "complete"  # Give up after max iterations
    
    # Check if refinement is needed
    needs_refinement = state.get("needs_refinement", False)
    confidence_score = state.get("confidence_score", 1.0)
    
    if needs_refinement and confidence_score < 0.8:
        return "refine"
    
    return "complete"
```

### Refinement Loop Conditions

**Entry Conditions**:
- `confidence_score < 0.8` (80% threshold)
- `refinement_iterations < max_refinement_iterations` (default: 3)

**Exit Conditions**:
- `confidence_score >= 0.8` (threshold met)
- `refinement_iterations >= max_refinement_iterations` (max reached)

### Conversation Loop Conditions

**Entry Conditions**:
- Missing required fields: `topic`, `year_level`, or `learning_objective`
- `ready_to_generate == False`

**Exit Conditions**:
- All required fields present
- `ready_to_generate == True`

---

## 8. Integration Points

### LangGraph Workflow Integration

**Location**: `backend/app/agents/workflow.py`

**Key Functions**:
- `create_script_generation_workflow()`: Builds and compiles workflow
- Workflow instance created once, reused for all sessions
- Thread-based execution: Each session uses unique `thread_id` in config

**Configuration**:
```python
config = {
    "configurable": {
        "thread_id": session_id  # Unique per session
    }
}
```

### FastAPI Endpoint Integration

**Location**: `backend/app/main.py`

**Integration Pattern**:
```python
# Create workflow instance (singleton)
workflow = create_script_generation_workflow()

@app.post("/api/v1/chat/sessions/{session_id}/messages")
async def send_message(session_id: str, request: ChatRequest):
    # Load state
    state = await load_session(session_id)
    
    # Update with user input
    state["user_input"] = request.message
    
    # Invoke workflow
    config = {"configurable": {"thread_id": session_id}}
    result = await workflow.ainvoke(state, config)
    
    # Save state
    await store_session(session_id, result)
    
    # Return response
    return format_response(result)
```

### Database/Redis Session Storage

**Storage Interface**:
```python
async def store_session(session_id: str, state: SessionState):
    """Store session state in Redis/PostgreSQL"""
    # Serialize state to JSON
    # Store with TTL (e.g., 24 hours)
    pass

async def load_session(session_id: str) -> SessionState:
    """Load session state from storage"""
    # Deserialize from JSON
    # Return SessionState dict
    pass
```

**Redis Structure**:
- Key: `session:{session_id}`
- Value: JSON-serialized SessionState
- TTL: 24 hours (configurable)

**PostgreSQL Structure**:
- Table: `chat_sessions`
- Columns: `session_id`, `state_json`, `created_at`, `updated_at`
- Index on `session_id`

### External API Integrations

#### CurricuLLM-AU API
- **Service**: `app/services/curriculum_api.py`
- **Function**: `get_curriculum_outcomes(topic, year_level, subject)`
- **Called by**: `curriculum_agent_node`
- **Error Handling**: Falls back to mock data if API unavailable

#### LLM Services (OpenAI/Anthropic)
- **Service**: `app/services/llm_service.py`
- **Used by**: 
  - `conversation_node` (information extraction, response generation)
  - `script_generation_node` (script generation)
- **Configuration**: From `app/config.py` settings

#### Wikipedia/Wikidata APIs
- **Service**: `app/services/fact_check_service.py`
- **Functions**: `extract_factual_claims()`, `check_fact()`
- **Called by**: `fact_checking_node`
- **Error Handling**: Returns low confidence if API unavailable

---

## 9. Error Handling Strategy

### Node-Level Error Handling

**Pattern**:
```python
async def node_function(state: SessionState) -> SessionState:
    try:
        # Node logic
        result = await perform_action()
        state.update(result)
    except Exception as e:
        # Log error
        logger.error(f"Error in {node_name}: {str(e)}")
        
        # Add to state errors
        state["errors"].append(f"{node_name}: {str(e)}")
        
        # Set status
        state["status"] = "failed"
        
        # Continue workflow (don't crash)
        return state
```

### Workflow-Level Error Recovery

**Strategies**:
1. **Graceful Degradation**: Continue workflow with partial data
2. **Retry Logic**: Retry failed operations (e.g., API calls)
3. **Fallback Values**: Use defaults or mock data when APIs fail
4. **State Validation**: Validate state before critical transitions

**Error States**:
- `failed`: Critical error, workflow stopped
- `warning`: Non-critical issue, workflow continues
- `partial`: Some operations failed, partial results available

### State Recovery Mechanisms

**On Workflow Restart**:
1. Load state from storage
2. Validate state structure
3. Identify last completed node
4. Resume from appropriate point
5. Handle missing/invalid fields gracefully

**Recovery Scenarios**:
- API timeout → Retry with exponential backoff
- Invalid state → Reset to last known good state
- Missing fields → Route back to conversation node

---

## 10. Future Extensibility

### Adding New Agents

**Steps**:
1. Create new agent class in `backend/app/agents/`
2. Implement agent logic
3. Add node function to `backend/app/agents/nodes.py`
4. Register node in workflow: `workflow.add_node("new_agent", new_agent_node)`
5. Add edge to connect to workflow

**Example**:
```python
# New agent: Research Agent
async def research_agent_node(state: SessionState) -> SessionState:
    # Agent logic
    pass

# Add to workflow
workflow.add_node("research", research_agent_node)
workflow.add_edge("information_gathering", "research")
```

### Adding New Subject-Specific Generators

**Steps**:
1. Create new generator class: `HistoryScriptAgent`, `GeographyScriptAgent`, etc.
2. Implement subject-specific prompt generation
3. Register in `get_script_generator_for_subject()` function
4. No workflow changes needed (selection is dynamic)

**Example**:
```python
def get_script_generator_for_subject(subject: str):
    generators = {
        "science": ScienceScriptAgent(),
        "math": MathScriptAgent(),
        "english": EnglishScriptAgent(),
        "history": HistoryScriptAgent(),  # New
        "geography": GeographyScriptAgent(),  # New
    }
    return generators.get(subject.lower(), DefaultScriptAgent())
```

### Extending Workflow with New Nodes

**Pattern**:
1. Define new node function
2. Add to workflow graph
3. Define edges (conditional or sequential)
4. Update state structure if needed

**Example**: Adding a "Review" node before completion
```python
workflow.add_node("review", review_node)
workflow.add_edge("fact_checking", "review")
workflow.add_edge("review", END)
```

### Adding New Conditional Paths

**Pattern**:
1. Create condition function
2. Add conditional edge to workflow
3. Define routing logic

**Example**: Adding quality check before fact-checking
```python
def check_script_quality(state: SessionState) -> str:
    quality_score = calculate_quality(state["script"])
    if quality_score < 0.7:
        return "improve"
    return "fact_check"

workflow.add_conditional_edges(
    "script_generation",
    check_script_quality,
    {
        "improve": "script_generation",  # Loop back
        "fact_check": "fact_checking"
    }
)
```

---

## 11. Dependencies and Requirements

### Python Packages

**Core**:
- `langgraph>=0.2.0`: Workflow orchestration
- `langchain>=0.1.0`: LLM integration and message handling
- `fastapi>=0.100.0`: REST API framework
- `pydantic>=2.0.0`: Data validation

**Existing** (from `requirements.txt`):
- `openai` or `anthropic`: LLM providers
- `requests`: HTTP client for APIs
- `sqlalchemy`: Database ORM
- `redis`: Session storage (optional)

### External Services

- **CurricuLLM-AU API**: Curriculum data
- **OpenAI/Anthropic**: LLM services
- **Wikipedia/Wikidata**: Fact-checking sources
- **Redis** (optional): Session storage
- **PostgreSQL**: Persistent storage

### Configuration

**Environment Variables** (from `app/config.py`):
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`
- `CURRICULLM_API_KEY`
- `DATABASE_URL`
- `REDIS_URL` (optional)

---

## 12. File Structure

### New Files to Create

```
backend/app/
├── agents/
│   ├── __init__.py
│   ├── state.py              # SessionState definition
│   ├── workflow.py           # Workflow creation
│   ├── nodes.py              # Node implementations
│   ├── conditions.py         # Conditional edge functions
│   └── generators/
│       ├── __init__.py
│       ├── base.py          # Base script generator
│       ├── science.py        # Science agent
│       ├── math.py           # Math agent
│       ├── english.py        # English agent
│       └── default.py        # Default agent
├── services/
│   └── session_storage.py    # Session persistence
└── main.py                   # Updated with new endpoints
```

### Existing Files to Modify

- `backend/app/main.py`: Add new REST endpoints
- `backend/app/services/curriculum_api.py`: Already exists, used by curriculum_agent_node
- `backend/app/services/fact_check_service.py`: Already exists, used by fact_checking_node
- `backend/app/services/llm_service.py`: Already exists, used by multiple nodes

---

## 13. Implementation Notes

### Development Approach

1. **Phase 1**: Implement basic workflow with conversation and information gathering
2. **Phase 2**: Add curriculum agent and script generation
3. **Phase 3**: Add fact-checking and refinement loop
4. **Phase 4**: Add subject-specific generators
5. **Phase 5**: Polish error handling and edge cases

### Testing Strategy

- **Unit Tests**: Test individual nodes in isolation
- **Integration Tests**: Test workflow end-to-end
- **API Tests**: Test REST endpoints with mock workflow
- **State Tests**: Test state transitions and persistence

### Performance Considerations

- **Async Operations**: All nodes use async/await
- **Caching**: Cache curriculum data per topic/year_level
- **Rate Limiting**: Implement rate limits for LLM API calls
- **Session Cleanup**: TTL-based cleanup of old sessions

---

## 14. Diagram Reference

### Complete System Architecture

```
┌─────────────┐
│   Frontend  │ (Next.js - Chat Interface)
│  (Next.js)  │
└──────┬──────┘
       │ HTTP/REST
       ▼
┌─────────────────────────────────────────┐
│         FastAPI REST API                 │
│  /chat/sessions, /messages, /script     │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│      LangGraph Workflow                 │
│                                         │
│  Conversation → Info Gathering          │
│       ↓              ↓                   │
│  Curriculum Agent ←─┘                   │
│       ↓                                 │
│  Script Generation                      │
│       ↓                                 │
│  Fact Checking ←─┐                     │
│       ↓          │ (refinement loop)    │
│    Complete      └─────────────────┘   │
└──────┬──────────────────────────────────┘
       │
       ├──► CurricuLLM-AU API
       ├──► OpenAI/Anthropic
       ├──► Wikipedia/Wikidata
       └──► Redis/PostgreSQL (State Storage)
```

---

## 15. Key Design Decisions

1. **LangGraph over CrewAI**: Better state management and conditional flows for this use case
2. **Separate Curriculum Agent**: Reusable, can be called by multiple agents
3. **Subject-Specific Generators**: Better quality through specialization
4. **Refinement Loop**: Iterative improvement until quality threshold met
5. **State Persistence**: Enables resumable workflows and debugging
6. **REST API Layer**: Clean separation between frontend and agent orchestration

---

## 16. References

- Existing codebase structure: `backend/app/`
- Current pipeline modules: `backend/app/pipeline/modules/`
- Current services: `backend/app/services/`
- Current models: `backend/app/models/`
- Project requirements: `Project.md`
- Setup guide: `SETUP.md`

---

*This document serves as the authoritative reference for implementing the multi-agent script generation system. All code implementations should align with the architecture and patterns described herein.*

