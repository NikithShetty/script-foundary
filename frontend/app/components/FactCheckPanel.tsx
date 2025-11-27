'use client';

interface FactCheckPanelProps {
  factChecking: {
    results: any[];
    confidence_score: number | null;
    citations: string[];
    warnings?: string[];
  };
}

export default function FactCheckPanel({ factChecking }: FactCheckPanelProps) {
  // Convert probability (0.0-1.0) to percentage (0-100)
  const confidenceScore = (factChecking.confidence_score ?? 0) * 100;
  const confidenceColor =
    confidenceScore >= 80
      ? 'bg-green-100 text-green-800'
      : confidenceScore >= 60
        ? 'bg-yellow-100 text-yellow-800'
        : 'bg-red-100 text-red-800';

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Fact-Checking Results</h3>

      {factChecking.warnings && factChecking.warnings.length > 0 && (
        <div className="mb-4 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Warnings</h4>
          <ul className="list-disc list-inside text-sm text-yellow-700 space-y-1">
            {factChecking.warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Confidence Score</span>
          <span className={`px-3 py-1 rounded-full text-sm font-semibold ${confidenceColor}`}>
            {confidenceScore.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full ${confidenceScore >= 80
              ? 'bg-green-500'
              : confidenceScore >= 60
                ? 'bg-yellow-500'
                : 'bg-red-500'
              }`}
            style={{ width: `${confidenceScore}%` }}
          />
        </div>
      </div>

      {factChecking.results.length > 0 && (
        <div className="space-y-3 mb-4">
          <h4 className="font-semibold text-gray-700">Verified Claims</h4>
          {factChecking.results.map((result, index) => (
            <div
              key={index}
              className={`p-3 rounded border-l-4 ${result.verified
                ? 'bg-green-50 border-green-400'
                : 'bg-red-50 border-red-400'
                }`}
            >
              <p className="text-sm text-gray-700 mb-1">
                <span className="font-medium">Claim:</span> {result.claim}
              </p>
              <p className="text-xs text-gray-600">
                {result.verified ? '✓ Verified' : '✗ Not verified'} - {result.notes}
              </p>
            </div>
          ))}
        </div>
      )}

      {factChecking.citations.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-700 mb-2">Sources</h4>
          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
            {factChecking.citations.map((citation, index) => (
              <li key={index}>
                <a
                  href={citation}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {citation}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}



