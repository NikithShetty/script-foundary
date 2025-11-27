'use client';

interface MisconceptionPanelProps {
  misconceptions: {
    addressed: any[];
    warnings: string[];
  };
}

// Helper to get correction text from various field names
function getCorrection(mc: any): string {
  return mc.correction || mc.correct_understanding || mc.correct_concept || null;
}

export default function MisconceptionPanel({ misconceptions }: MisconceptionPanelProps) {
  const hasValidData = misconceptions.addressed.length > 0 || misconceptions.warnings.length > 0;

  if (!hasValidData) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Misconceptions Addressed</h3>
        <p className="text-gray-500 text-sm">No misconceptions identified for this topic</p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Misconceptions Addressed</h3>

      {misconceptions.warnings.length > 0 && (
        <div className="space-y-3 mb-4">
          {misconceptions.warnings.map((warning, index) => (
            <div
              key={index}
              className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded"
            >
              <p className="text-sm text-gray-700">{warning}</p>
            </div>
          ))}
        </div>
      )}

      {misconceptions.addressed.length > 0 && (
        <div className={misconceptions.warnings.length > 0 ? "mt-4" : ""}>
          <h4 className="font-semibold text-gray-700 mb-2">Identified Misconceptions</h4>
          <ul className="space-y-3">
            {misconceptions.addressed.map((mc, index) => {
              const correction = getCorrection(mc);
              return (
                <li key={index} className="text-sm text-gray-700 border-l-2 border-blue-200 pl-3">
                  <div className="mb-1">
                    <span className="font-medium text-gray-800">Misconception:</span>{' '}
                    <span className="text-gray-700">{mc.misconception}</span>
                  </div>
                  {correction && (
                    <div>
                      <span className="font-medium text-gray-800">Correction:</span>{' '}
                      <span className="text-gray-700">{correction}</span>
                    </div>
                  )}
                  {mc.why_common && (
                    <div className="text-xs text-gray-500 mt-1 italic">
                      Why common: {mc.why_common}
                    </div>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
}



