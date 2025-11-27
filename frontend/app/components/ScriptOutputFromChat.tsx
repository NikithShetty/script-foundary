'use client';

import { ScriptResponse, ScriptOutput as ScriptOutputType } from '@/lib/api';
import ScriptOutput from './ScriptOutput';
import CurriculumDashboard from './CurriculumDashboard';
import MisconceptionPanel from './MisconceptionPanel';
import FactCheckPanel from './FactCheckPanel';
import CulturalSafetyPanel from './CulturalSafetyPanel';
import AccessibilityPanel from './AccessibilityPanel';

interface ScriptOutputFromChatProps {
  scriptResponse: ScriptResponse;
}

export default function ScriptOutputFromChat({ scriptResponse }: ScriptOutputFromChatProps) {
  // Convert ScriptResponse to ScriptOutput format for compatibility
  const output: ScriptOutputType = {
    topic: scriptResponse.topic,
    year_level: scriptResponse.year_level,
    learning_objective: scriptResponse.learning_objective,
    script: scriptResponse.script,
    scenes: scriptResponse.scenes,
    curriculum: {
      outcomes: scriptResponse.curriculum.outcomes || [],
      codes: scriptResponse.curriculum.codes || [],
      prerequisites: [],
    },
    misconceptions: {
      addressed: (scriptResponse.misconceptions?.misconceptions || []).map((mc: any) => ({
        misconception: mc.misconception,
        correction: mc.correction || mc.correct_understanding,
        why_common: mc.why_common,
        correct_understanding: mc.correct_understanding,
      })),
      warnings: [],
    },
    fact_checking: {
      results: scriptResponse.fact_checking?.results?.claims || [],
      confidence_score: scriptResponse.fact_checking?.confidence_score || null,
      citations: scriptResponse.fact_checking?.results?.claims?.flatMap((c: any) => c.sources || []) || [],
      warnings: scriptResponse.fact_checking?.warnings || [],
    },
    cultural_safety: {
      flags: scriptResponse.cultural_safety?.flags || [],
      suggestions: [],
    },
    accessibility: {
      alt_texts: [],
      captions: [],
      metadata: scriptResponse.accessibility?.metadata || {},
    },
    errors: [],
    warnings: [
      ...(scriptResponse.fact_checking?.warnings || []),
    ],
    metadata: {},
  };

  return (
    <div className="space-y-6">
      <ScriptOutput output={output} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <CurriculumDashboard curriculum={output.curriculum} />
        <MisconceptionPanel misconceptions={output.misconceptions} />
        <FactCheckPanel factChecking={output.fact_checking} />
        <CulturalSafetyPanel culturalSafety={output.cultural_safety} />
        <AccessibilityPanel accessibility={output.accessibility} />
      </div>
    </div>
  );
}

