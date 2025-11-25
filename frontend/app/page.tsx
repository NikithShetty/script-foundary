'use client';

import { useState } from 'react';
import ChatInterface from './components/ChatInterface';
import ScriptOutputFromChat from './components/ScriptOutputFromChat';
import SessionsSidebar from './components/SessionsSidebar';
import { ScriptResponse } from '@/lib/api';

export default function Home() {
  const [script, setScript] = useState<ScriptResponse | null>(null);
  const [viewMode, setViewMode] = useState<'chat' | 'script'>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);

  const handleScriptReady = (scriptResponse: ScriptResponse) => {
    setScript(scriptResponse);
    setViewMode('script');
  };

  const handleSelectSession = (sessionId: string) => {
    setSelectedSessionId(sessionId);
    setCurrentSessionId(sessionId);
    setSidebarOpen(false);
    // Reset script when switching sessions
    setScript(null);
    setViewMode('chat');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sessions Sidebar */}
      <SessionsSidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onSelectSession={handleSelectSession}
        currentSessionId={currentSessionId}
      />

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Script Foundary
          </h1>
          <p className="text-gray-600">
            Chat with AI to collaboratively create evidence-based educational scripts with curriculum alignment,
            misconception checking, and accessibility features
          </p>
        </header>

        {/* View Mode Toggle */}
        {script && (
          <div className="mb-4 flex gap-2">
            <button
              onClick={() => setViewMode('chat')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${viewMode === 'chat'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
            >
              Chat
            </button>
            <button
              onClick={() => setViewMode('script')}
              className={`px-4 py-2 rounded-md font-medium transition-colors ${viewMode === 'script'
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
            >
              Generated Script
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chat Interface - Always visible on left */}
          <div className={`lg:col-span-1 ${viewMode === 'script' ? 'hidden lg:block' : ''}`}>
            <div className="lg:sticky lg:top-4" style={{ height: viewMode === 'chat' ? 'calc(100vh - 8rem)' : 'auto' }}>
              <ChatInterface 
                onScriptReady={handleScriptReady} 
                initialSessionId={selectedSessionId}
              />
            </div>
          </div>

          {/* Script Output - Right side */}
          <div className={`lg:col-span-2 ${viewMode === 'chat' ? 'hidden lg:block' : ''}`}>
            {script ? (
              <ScriptOutputFromChat scriptResponse={script} />
            ) : (
              <div className="bg-white p-12 rounded-lg shadow-md text-center">
                <p className="text-gray-500">
                  Start a conversation to create an educational script. The AI will guide you through
                  gathering information and generating your script.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
