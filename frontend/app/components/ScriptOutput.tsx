'use client';

import { ScriptOutput as ScriptOutputType } from '@/lib/api';

interface ScriptOutputProps {
  output: ScriptOutputType;
}

export default function ScriptOutput({ output }: ScriptOutputProps) {
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
          <h3 className="text-lg font-semibold mb-2">Learning Objective</h3>
          <p className="text-gray-700 mb-6">{output.learning_objective}</p>

          <h3 className="text-lg font-semibold mb-2">Script</h3>
          <div className="bg-gray-50 p-4 rounded-md whitespace-pre-wrap text-sm">
            {output.script || 'No script generated'}
          </div>
        </div>
      </div>

      {output.scenes && output.scenes.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Scenes</h3>
          <div className="space-y-4">
            {output.scenes.map((scene, index) => (
              <div key={index} className="border-l-4 border-blue-500 pl-4">
                <h4 className="font-semibold text-gray-800">{scene.title}</h4>
                <div className="mt-2 space-y-2 text-sm">
                  {scene.visual_description && (
                    <div>
                      <span className="font-medium text-gray-600">Visual: </span>
                      <span className="text-gray-700">{scene.visual_description}</span>
                    </div>
                  )}
                  {scene.narration && (
                    <div>
                      <span className="font-medium text-gray-600">Narration: </span>
                      <span className="text-gray-700">{scene.narration}</span>
                    </div>
                  )}
                  {scene.text_overlay && (
                    <div>
                      <span className="font-medium text-gray-600">Text Overlay: </span>
                      <span className="text-gray-700">{scene.text_overlay}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

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



