'use client';

interface CulturalSafetyPanelProps {
  culturalSafety: {
    flags: string[];
    suggestions: string[];
  };
}

export default function CulturalSafetyPanel({ culturalSafety }: CulturalSafetyPanelProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Cultural Safety Check</h3>
      
      {culturalSafety.flags.length > 0 ? (
        <div className="mb-4">
          <h4 className="font-semibold text-red-700 mb-2">Flags</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-red-600">
            {culturalSafety.flags.map((flag, index) => (
              <li key={index}>{flag}</li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded">
          <p className="text-sm text-green-700">✓ No cultural safety issues detected</p>
        </div>
      )}

      {culturalSafety.suggestions.length > 0 && (
        <div>
          <h4 className="font-semibold text-blue-700 mb-2">Suggestions</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-blue-600">
            {culturalSafety.suggestions.map((suggestion, index) => (
              <li key={index}>{suggestion}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}



