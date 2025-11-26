'use client';

import { useState } from 'react';
import { ScriptOutput as ScriptOutputType } from '@/lib/api';
import { parseScript, renderParsedScript } from '@/app/utils/scriptParser';

interface ScriptOutputProps {
  output: ScriptOutputType;
}

export default function ScriptOutput({ output }: ScriptOutputProps) {
  const parsedScript = output.script ? parseScript(output.script) : [];
  const [copied, setCopied] = useState(false);

  const handleCopyScript = async () => {
    if (!output.script) return;

    try {
      await navigator.clipboard.writeText(output.script);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy script:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Educational Script: {output.topic}
        </h2>
        <div className="text-sm text-gray-600 mb-4">
          Level: Year {output.year_level} | Curriculum Codes: {output.curriculum.codes.join(', ') || 'N/A'}
        </div>

        <div className="prose max-w-none">
          <h3 className="text-lg font-semibold mb-2 text-gray-900">Learning Objective</h3>
          <p className="text-gray-900 mb-6">{output.learning_objective}</p>

          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Script</h3>
            {output.script && (
              <button
                onClick={handleCopyScript}
                className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 hover:border-gray-400 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                title="Copy script to clipboard"
              >
                {copied ? (
                  <>
                    <svg
                      className="w-4 h-4 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-green-600">Copied!</span>
                  </>
                ) : (
                  <>
                    <svg
                      className="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      />
                    </svg>
                    <span>Copy Script</span>
                  </>
                )}
              </button>
            )}
          </div>
          <div className="bg-gray-50 p-6 rounded-md border border-gray-200">
            {parsedScript.length > 0 ? (
              <div className="space-y-1">
                {renderParsedScript(parsedScript)}
              </div>
            ) : (
              <p className="text-gray-500 italic">No script generated</p>
            )}
          </div>
        </div>
      </div>

      {output.errors && output.errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-md">
          <h4 className="font-semibold text-red-800 mb-2">Errors</h4>
          <ul className="list-disc list-inside text-sm text-red-700">
            {output.errors.map((error, index) => (
              <li key={index}>{error}</li>
            ))}
          </ul>
        </div>
      )}

      {output.warnings && output.warnings.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-md">
          <h4 className="font-semibold text-yellow-800 mb-2">Warnings</h4>
          <ul className="list-disc list-inside text-sm text-yellow-700">
            {output.warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}



