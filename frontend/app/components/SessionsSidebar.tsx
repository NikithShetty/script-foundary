'use client';

import { useState, useEffect } from 'react';
import { listSessions, SessionSummary } from '@/lib/api';

interface SessionsSidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  onSelectSession: (sessionId: string) => void;
  currentSessionId?: string | null;
}

export default function SessionsSidebar({
  isOpen,
  onToggle,
  onSelectSession,
  currentSessionId,
}: SessionsSidebarProps) {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadSessions();
    }
  }, [isOpen]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await listSessions();
      setSessions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load sessions');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString?: string | null) => {
    if (!dateString) return 'Unknown';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return 'Unknown';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'generating':
      case 'fact_checking':
        return 'bg-blue-100 text-blue-800';
      case 'collecting_info':
        return 'bg-yellow-100 text-yellow-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <>
      {/* Toggle Button - Only show when sidebar is closed */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed left-4 top-4 z-50 p-2 bg-blue-600 text-white rounded-md shadow-lg hover:bg-blue-700 transition-colors"
          aria-label="Show sessions"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      )}

      {/* Sidebar */}
      <div
        className={`fixed left-0 top-0 h-full bg-white shadow-xl z-40 transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
        style={{ width: '320px' }}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-gray-200 relative">
            <button
              onClick={onToggle}
              className="absolute right-4 top-4 p-1 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
              aria-label="Hide sessions"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
            <h2 className="text-xl font-bold text-gray-900 pr-8">Previous Sessions</h2>
            <p className="text-sm text-gray-600 mt-1">
              Click on a session to view it
            </p>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : error ? (
              <div className="text-red-600 text-sm py-4">{error}</div>
            ) : sessions.length === 0 ? (
              <div className="text-gray-500 text-sm py-8 text-center">
                No previous sessions found
              </div>
            ) : (
              <div className="space-y-3">
                {sessions.map((session) => (
                  <button
                    key={session.session_id}
                    onClick={() => onSelectSession(session.session_id)}
                    className={`w-full text-left p-3 rounded-lg border-2 transition-all hover:shadow-md ${
                      currentSessionId === session.session_id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-gray-900 truncate">
                          {session.topic || 'Untitled Session'}
                        </h3>
                        {session.subject && (
                          <p className="text-xs text-gray-500 mt-1">
                            {session.subject}
                            {session.year_level && ` • Year ${session.year_level}`}
                          </p>
                        )}
                      </div>
                      <span
                        className={`ml-2 px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(
                          session.status
                        )}`}
                      >
                        {session.status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mt-2">
                      Updated: {formatDate(session.updated_at)}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <button
              onClick={loadSessions}
              className="w-full px-4 py-2 text-sm font-medium text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100 transition-colors"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Overlay with blur effect */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-white/30 backdrop-blur-sm z-30"
          onClick={onToggle}
        />
      )}
    </>
  );
}

