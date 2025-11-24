'use client';

interface AccessibilityPanelProps {
  accessibility: {
    alt_texts: string[];
    captions: string[];
    metadata: any;
  };
}

export default function AccessibilityPanel({ accessibility }: AccessibilityPanelProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Accessibility Features</h3>
      
      <div className="space-y-4">
        {accessibility.alt_texts.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">
              ALT Texts ({accessibility.alt_texts.length})
            </h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              {accessibility.alt_texts.map((alt, index) => (
                <li key={index}>{alt}</li>
              ))}
            </ul>
          </div>
        )}

        {accessibility.captions.length > 0 && (
          <div>
            <h4 className="font-semibold text-gray-700 mb-2">
              Captions ({accessibility.captions.length})
            </h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              {accessibility.captions.map((caption, index) => (
                <li key={index}>{caption}</li>
              ))}
            </ul>
          </div>
        )}

        {accessibility.metadata?.has_accessibility_features && (
          <div className="p-3 bg-green-50 border border-green-200 rounded">
            <p className="text-sm text-green-700">
              ✓ Accessibility features generated successfully
            </p>
            {accessibility.metadata.dyslexia_friendly_script && (
              <p className="text-xs text-green-600 mt-1">
                Dyslexia-friendly formatting available
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}



