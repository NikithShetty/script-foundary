/** API client for backend communication */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ScriptInput {
  topic: string;
  year_level: number;
  learning_objective: string;
  subject?: string;
  enable_curriculum_aligner?: boolean;
  enable_misconception_checker?: boolean;
  enable_script_generator?: boolean;
  enable_fact_checker?: boolean;
  enable_cultural_safety?: boolean;
  enable_accessibility?: boolean;
}

export interface Scene {
  scene_number: number;
  title: string;
  visual_description: string;
  narration: string;
  text_overlay?: string;
  accessibility_cue?: string;
  duration_estimate?: number;
}

export interface ScriptOutput {
  topic: string;
  year_level: number;
  learning_objective: string;
  script: string;
  scenes: Scene[];
  curriculum: {
    outcomes: any[];
    codes: string[];
    prerequisites: string[];
  };
  misconceptions: {
    addressed: any[];
    warnings: string[];
  };
  fact_checking: {
    results: any[];
    confidence_score: number | null;
    citations: string[];
  };
  cultural_safety: {
    flags: string[];
    suggestions: string[];
  };
  accessibility: {
    alt_texts: string[];
    captions: string[];
    metadata: any;
  };
  errors: string[];
  warnings: string[];
  metadata: any;
}

export async function generateScript(input: ScriptInput): Promise<ScriptOutput> {
  const response = await fetch(`${API_URL}/api/v1/scripts/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to generate script');
  }

  return response.json();
}

export async function searchCurriculum(topic: string, yearLevel: number, subject?: string) {
  const params = new URLSearchParams({
    topic,
    year_level: yearLevel.toString(),
  });
  if (subject) {
    params.append('subject', subject);
  }

  const response = await fetch(`${API_URL}/api/v1/curriculum/search?${params}`);
  if (!response.ok) {
    throw new Error('Failed to search curriculum');
  }
  return response.json();
}

export async function getMisconceptions(topic: string) {
  const response = await fetch(`${API_URL}/api/v1/misconceptions/${encodeURIComponent(topic)}`);
  if (!response.ok) {
    throw new Error('Failed to get misconceptions');
  }
  return response.json();
}

export async function factCheckText(text: string) {
  const response = await fetch(`${API_URL}/api/v1/fact-check`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    throw new Error('Failed to fact-check text');
  }
  return response.json();
}

// ============================================================================
// Chat Session API
// ============================================================================

export interface ChatRequest {
  message: string;
}

export interface AgentAction {
  agent: string;
  action: string;
  status: string;
}

export interface ChatResponse {
  message_id: string;
  role: 'assistant';
  content: string;
  session_id: string;
  collected_data: {
    topic?: string | null;
    year_level?: number | null;
    learning_objective?: string | null;
    subject?: string | null;
  };
  status: string;
  missing_fields: string[];
  ready_to_generate: boolean;
  agent_actions: AgentAction[];
}

export interface SessionStatus {
  session_id: string;
  status: string;
  collected_data: {
    topic?: string | null;
    year_level?: number | null;
    learning_objective?: string | null;
    subject?: string | null;
  };
  missing_fields: string[];
  conversation_history: Array<{
    role: string;
    content: string;
  }>;
  generation_progress?: {
    current_step: string;
    current_agent: string;
    progress: number;
  } | null;
  created_at?: string;
  updated_at?: string;
}

export interface ScriptResponse {
  session_id: string;
  topic: string;
  year_level: number;
  learning_objective: string;
  script: string;
  scenes: Scene[];
  curriculum: {
    outcomes: any[];
    codes: string[];
  };
  fact_checking: {
    confidence_score: number;
    results: any;
  };
  misconceptions?: {
    misconceptions?: any[];
  };
  cultural_safety?: {
    flags?: string[];
  };
  accessibility?: {
    metadata?: any;
  };
}

export interface GenerationStatus {
  status: string;
  progress: number;
  current_step: string;
  current_agent: string;
  estimated_time_remaining?: number | null;
  errors: string[];
  warnings: string[];
}

export interface SessionSummary {
  session_id: string;
  topic?: string | null;
  year_level?: number | null;
  subject?: string | null;
  status: string;
  created_at?: string | null;
  updated_at?: string | null;
}

/**
 * Create a new conversation session.
 */
export async function createSession(): Promise<SessionStatus> {
  const response = await fetch(`${API_URL}/api/v1/chat/sessions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create session');
  }

  return response.json();
}

/**
 * Send a message to the orchestrator and process through workflow.
 */
export async function sendMessage(
  sessionId: string,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/api/v1/chat/sessions/${sessionId}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to send message');
  }

  return response.json();
}

/**
 * Get current session status and collected data.
 */
export async function getSession(sessionId: string): Promise<SessionStatus> {
  const response = await fetch(`${API_URL}/api/v1/chat/sessions/${sessionId}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get session');
  }

  return response.json();
}

/**
 * Retrieve generated script when status is "completed".
 */
export async function getScript(sessionId: string): Promise<ScriptResponse> {
  const response = await fetch(`${API_URL}/api/v1/chat/sessions/${sessionId}/script`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get script');
  }

  return response.json();
}

/**
 * Poll for generation status (for long-running operations).
 */
export async function getGenerationStatus(sessionId: string): Promise<GenerationStatus> {
  const response = await fetch(
    `${API_URL}/api/v1/chat/sessions/${sessionId}/generation/status`
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get generation status');
  }

  return response.json();
}

/**
 * List all previous sessions.
 */
export async function listSessions(): Promise<SessionSummary[]> {
  const response = await fetch(`${API_URL}/api/v1/chat/sessions`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to list sessions');
  }

  return response.json();
}



