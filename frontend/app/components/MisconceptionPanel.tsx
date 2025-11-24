'use client';

interface MisconceptionPanelProps {
  misconceptions: {
    addressed: any[];
    warnings: string[];
  };
}

export default function MisconceptionPanel({ misconceptions }: MisconceptionPanelProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Misconceptions Addressed</h3>
      
      {misconceptions.warnings.length > 0 ? (
        <div className="space-y-3">
          {misconceptions.warnings.map((warning, index) => (
            <div
              key={index}
              className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded"
            >
              <p className="text-sm text-gray-700">{warning}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">No misconceptions identified for this topic</p>
      )}

      {misconceptions.addressed.length > 0 && (
        <div className="mt-4">
          <h4 className="font-semibold text-gray-700 mb-2">Misconceptions Database</h4>
          <ul className="space-y-2">
            {misconceptions.addressed.map((mc, index) => (
              <li key={index} className="text-sm text-gray-700">
                <span className="font-medium">Misconception:</span> {mc.misconception || 'N/A'}
                <br />
                <span className="font-medium">Correction:</span> {mc.correction || 'N/A'}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}



