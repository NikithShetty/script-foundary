'use client';

import { useState, useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import {
  createSession,
  sendMessage,
  getSession,
  getScript,
  getGenerationStatus,
  ChatResponse,
  SessionStatus,
  ScriptResponse,
} from '@/lib/api';

interface ChatInterfaceProps {
  onScriptReady?: (script: ScriptResponse) => void;
}

export default function ChatInterface({ onScriptReady }: ChatInterfaceProps) {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [status, setStatus] = useState<string>('collecting_info');
  const [collectedData, setCollectedData] = useState<SessionStatus['collected_data']>({});
  const [missingFields, setMissingFields] = useState<string[]>([]);
  const [agentActions, setAgentActions] = useState<Array<{ agent: string; action: string; status: string }>>([]);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize session on mount
  useEffect(() => {
    const initSession = async () => {
      try {
        const session = await createSession();
        setSessionId(session.session_id);
        setStatus(session.status);
        setCollectedData(session.collected_data);
        setMissingFields(session.missing_fields);
        
        // Add welcome message
        setMessages([
          {
            role: 'assistant',
            content: "Hello! I'm here to help you create an educational video script. Let's start by gathering some information. What topic would you like to create a script about?",
          },
        ]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to initialize session');
      }
    };

    initSession();
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Poll for status updates when generating
  useEffect(() => {
    if (!sessionId || !isPolling) return;

    const pollInterval = setInterval(async () => {
      try {
        const genStatus = await getGenerationStatus(sessionId);
        setStatus(genStatus.status);
        setAgentActions([
          {
            agent: genStatus.current_agent,
            action: genStatus.current_step,
            status: genStatus.status,
          },
        ]);

        // Check if script is ready
        if (genStatus.status === 'completed') {
          setIsPolling(false);
          clearInterval(pollInterval);
          try {
            const script = await getScript(sessionId);
            if (onScriptReady) {
              onScriptReady(script);
            }
            setMessages((prev) => [
              ...prev,
              {
                role: 'assistant',
                content: `Great! Your script has been generated and fact-checked with a confidence score of ${(genStatus.progress * 100).toFixed(0)}%. You can view it in the script view.`,
              },
            ]);
            setStatus('completed');
          } catch (err) {
            const errorMsg = err instanceof Error ? err.message : 'Failed to retrieve script';
            setError(errorMsg);
            setMessages((prev) => [
              ...prev,
              {
                role: 'assistant',
                content: `I encountered an error retrieving the script: ${errorMsg}. Please try again.`,
              },
            ]);
          }
        } else if (genStatus.status === 'failed') {
          setIsPolling(false);
          clearInterval(pollInterval);
          const errorMsg = genStatus.errors.length > 0 
            ? genStatus.errors.join(', ') 
            : 'Script generation failed. Please try again.';
          setError(errorMsg);
          setMessages((prev) => [
            ...prev,
            {
              role: 'assistant',
              content: `I'm sorry, but script generation failed: ${errorMsg}. Please try starting a new conversation.`,
            },
          ]);
        }
      } catch (err) {
        console.error('Error polling status:', err);
      }
    }, 2000); // Poll every 2 seconds

    return () => clearInterval(pollInterval);
  }, [sessionId, isPolling, onScriptReady]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setError(null);

    // Add user message to UI
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);

    try {
      const response: ChatResponse = await sendMessage(sessionId, {
        message: userMessage,
      });

      // Add assistant response
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.content },
      ]);

      // Update state
      setStatus(response.status);
      setCollectedData(response.collected_data);
      setMissingFields(response.missing_fields);
      setAgentActions(response.agent_actions);

      // Start polling if generating or in a state that requires polling
      if (['generating', 'fact_checking', 'needs_refinement', 'script_generated'].includes(response.status)) {
        setIsPolling(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col bg-white rounded-lg shadow-md" style={{ height: '100%' }}>
      {/* Header */}
      <div className="p-4 border-b bg-gray-50">
        <h2 className="text-xl font-bold text-gray-900">Chat with AI Assistant</h2>
        <div className="mt-2 flex items-center gap-4 text-sm">
          <span className={`px-2 py-1 rounded ${
            status === 'completed' ? 'bg-green-100 text-green-800' :
            status === 'generating' || status === 'fact_checking' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {status.replace('_', ' ')}
          </span>
          {agentActions.length > 0 && (
            <span className="text-gray-600">
              {agentActions[0].agent} - {agentActions[0].action}
            </span>
          )}
        </div>
      </div>

      {/* Collected Data Summary */}
      {(collectedData.topic || collectedData.year_level || collectedData.learning_objective) && (
        <div className="p-4 border-b bg-blue-50">
          <h3 className="text-sm font-semibold text-gray-700 mb-2">Collected Information:</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {collectedData.topic && (
              <div>
                <span className="font-medium">Topic:</span> {collectedData.topic}
              </div>
            )}
            {collectedData.year_level && (
              <div>
                <span className="font-medium">Year Level:</span> {collectedData.year_level}
              </div>
            )}
            {collectedData.subject && (
              <div>
                <span className="font-medium">Subject:</span> {collectedData.subject}
              </div>
            )}
            {collectedData.learning_objective && (
              <div className="col-span-2">
                <span className="font-medium">Learning Objective:</span> {collectedData.learning_objective}
              </div>
            )}
          </div>
          {missingFields.length > 0 && (
            <div className="mt-2 text-sm text-amber-700">
              <span className="font-medium">Still need:</span> {missingFields.join(', ')}
            </div>
          )}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} role={msg.role} content={msg.content} />
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg px-4 py-2">
              <div className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600"></div>
                <span className="text-sm text-gray-600">Thinking...</span>
              </div>
            </div>
          </div>
        )}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-4 border-t bg-gray-50">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading || !sessionId}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 disabled:bg-gray-100"
          />
          <button
            type="submit"
            disabled={isLoading || !sessionId || !input.trim()}
            className="px-6 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

