'use client';

interface CurriculumDashboardProps {
  curriculum: {
    outcomes: any[];
    codes: string[];
    prerequisites: string[];
  };
}

export default function CurriculumDashboard({ curriculum }: CurriculumDashboardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Curriculum Alignment</h3>
      
      {curriculum.codes.length > 0 ? (
        <div className="space-y-4">
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">Curriculum Codes</h4>
            <div className="flex flex-wrap gap-2">
              {curriculum.codes.map((code, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                >
                  {code}
                </span>
              ))}
            </div>
          </div>

          {curriculum.outcomes.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Learning Outcomes</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                {curriculum.outcomes.map((outcome, index) => (
                  <li key={index}>
                    <span className="font-medium">{outcome.code}:</span>{' '}
                    {outcome.description || 'No description available'}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {curriculum.prerequisites.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Prerequisites</h4>
              <ul className="list-disc list-inside text-sm text-gray-700">
                {curriculum.prerequisites.map((prereq, index) => (
                  <li key={index}>{prereq}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ) : (
        <p className="text-gray-500 text-sm">No curriculum data available</p>
      )}
    </div>
  );
}



