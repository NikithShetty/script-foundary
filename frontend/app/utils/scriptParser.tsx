import React from 'react';

export interface ParsedScriptElement {
  type: 'title' | 'learning-objective' | 'scene' | 'heading' | 'section-label' | 'paragraph' | 'list' | 'empty';
  content: string;
  level?: number; // For headings (1-6)
  label?: string; // For section labels like "Visual:", "Narration:"
  items?: string[]; // For lists
}

/**
 * Parse script text into structured elements for better display
 */
export function parseScript(script: string): ParsedScriptElement[] {
  if (!script) return [];

  const lines = script.split('\n');
  const elements: ParsedScriptElement[] = [];
  const knownLabels = [
    'Visual', 'Narration', 'Text Overlay', 'Text overlay',
    'Accessibility', 'Accessibility cue', 'Character', 'Voice',
    'Problem setup', 'Step-by-step', 'Visual metaphor', 'Visual description',
    'Text overlay', 'Accessibility cue'
  ];

  let currentList: string[] = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();

    // Empty lines - flush any current list
    if (!line) {
      if (currentList.length > 0) {
        elements.push({ type: 'list', content: '', items: [...currentList] });
        currentList = [];
      }
      elements.push({ type: 'empty', content: '' });
      continue;
    }

    // Title detection (EDUCATIONAL SCRIPT:, Title:, Topic:, etc.)
    const titleMatch = line.match(/^(EDUCATIONAL\s+SCRIPT|Title|Topic|SCRIPT\s+TITLE):\s*(.+)$/i);
    if (titleMatch) {
      if (currentList.length > 0) {
        elements.push({ type: 'list', content: '', items: [...currentList] });
        currentList = [];
      }
      elements.push({
        type: 'title',
        content: titleMatch[2]?.trim() || line,
      });
      continue;
    }

    // Learning Objective detection
    const learningObjectiveMatch = line.match(/^(Learning\s+Objective|Learning\s+Goal|Objective):\s*(.+)$/i);
    if (learningObjectiveMatch) {
      if (currentList.length > 0) {
        elements.push({ type: 'list', content: '', items: [...currentList] });
        currentList = [];
      }
      elements.push({
        type: 'learning-objective',
        content: learningObjectiveMatch[2]?.trim() || line,
      });
      continue;
    }

    // Scene headers - handle both bracketed and non-bracketed formats
    // Examples: "[Scene 10: Summary and Review]", "SCENE 1:", "Scene 2: Title", "[Scene 2]"
    const bracketedSceneMatch = line.match(/^\[(Scene\s+\d+[:\-]?\s*.*?)\]$/i);
    if (bracketedSceneMatch) {
      if (currentList.length > 0) {
        elements.push({ type: 'list', content: '', items: [...currentList] });
        currentList = [];
      }
      elements.push({
        type: 'scene',
        content: bracketedSceneMatch[1].trim(), // Extract content without brackets
      });
      continue;
    }

    // Non-bracketed scene headers (SCENE 1:, Scene 1:, etc.)
    const sceneMatch = line.match(/^(SCENE|Scene)\s+\d+[:\-]?\s*(.+)?$/i);
    if (sceneMatch) {
      if (currentList.length > 0) {
        elements.push({ type: 'list', content: '', items: [...currentList] });
        currentList = [];
      }
      elements.push({
        type: 'scene',
        content: line,
      });
      continue;
    }

    // Markdown headings (##, ###, ####, etc.)
    const headingMatch = line.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      if (currentList.length > 0) {
        elements.push({ type: 'list', content: '', items: [...currentList] });
        currentList = [];
      }
      const level = headingMatch[1].length;
      const content = headingMatch[2].trim();
      elements.push({
        type: 'heading',
        content,
        level,
      });
      continue;
    }

    // Section labels in brackets [Visual description], [Narration], etc.
    // Only match if it's NOT a scene (scenes are handled above)
    const bracketLabelMatch = line.match(/^\[([A-Za-z\s]+)\]\s*(.+)?$/i);
    if (bracketLabelMatch) {
      const label = bracketLabelMatch[1].trim();

      // Skip if it looks like a scene
      if (!/^Scene\s+\d+/i.test(label)) {
        if (currentList.length > 0) {
          elements.push({ type: 'list', content: '', items: [...currentList] });
          currentList = [];
        }
        const content = bracketLabelMatch[2]?.trim() || '';

        // Check if it matches any known label (case-insensitive, partial match)
        const matchedLabel = knownLabels.find(known =>
          label.toLowerCase().includes(known.toLowerCase()) ||
          known.toLowerCase().includes(label.toLowerCase())
        );

        if (matchedLabel) {
          elements.push({
            type: 'section-label',
            content: content || label,
            label: matchedLabel,
          });
          continue;
        }
      }
    }

    // Section labels with colon (Visual:, Narration:, Text Overlay:, etc.)
    const colonLabelMatch = line.match(/^([A-Z][A-Za-z\s]{2,30}):\s*(.+)?$/);
    if (colonLabelMatch) {
      const label = colonLabelMatch[1].trim();
      const content = colonLabelMatch[2]?.trim() || '';

      // Check if it matches any known label (case-insensitive, partial match)
      const matchedLabel = knownLabels.find(known =>
        label.toLowerCase().includes(known.toLowerCase()) ||
        known.toLowerCase().includes(label.toLowerCase())
      );

      if (matchedLabel) {
        if (currentList.length > 0) {
          elements.push({ type: 'list', content: '', items: [...currentList] });
          currentList = [];
        }
        elements.push({
          type: 'section-label',
          content: content || label,
          label: matchedLabel,
        });
        continue;
      }
    }

    // List items (bullet points or numbered)
    const listItemMatch = line.match(/^[-*•]\s+(.+)$/) || line.match(/^\d+[.)]\s+(.+)$/);
    if (listItemMatch) {
      currentList.push(listItemMatch[1] || line.replace(/^[-*•]\s+/, '').replace(/^\d+[.)]\s+/, ''));
      continue;
    }

    // Flush list if we hit a non-list item
    if (currentList.length > 0) {
      elements.push({ type: 'list', content: '', items: [...currentList] });
      currentList = [];
    }

    // Regular paragraphs
    elements.push({
      type: 'paragraph',
      content: line,
    });
  }

  // Flush any remaining list items
  if (currentList.length > 0) {
    elements.push({ type: 'list', content: '', items: [...currentList] });
  }

  return elements;
}

/**
 * Render parsed script elements with appropriate styling
 */
export function renderParsedScript(elements: ParsedScriptElement[]): React.ReactNode {
  return elements.map((element, index) => {
    switch (element.type) {
      case 'title':
        return (
          <div
            key={index}
            className="mt-4 mb-6 pb-3 border-b-2 border-purple-400"
          >
            <h3 className="text-2xl font-bold text-purple-700 uppercase tracking-wide">
              {element.content}
            </h3>
          </div>
        );

      case 'learning-objective':
        return (
          <div
            key={index}
            className="my-4 pl-4 border-l-4 border-green-400 bg-green-50/30 py-3 rounded-r"
          >
            <span className="font-semibold text-green-700 text-sm uppercase tracking-wide block mb-1">
              Learning Objective:
            </span>
            <p className="text-gray-800 text-base leading-relaxed font-medium">
              {element.content}
            </p>
          </div>
        );

      case 'scene':
        return (
          <div
            key={index}
            className="mt-6 mb-4 pb-2 border-b-2 border-blue-400"
          >
            <h4 className="text-lg font-bold text-blue-700 uppercase tracking-wide">
              {element.content}
            </h4>
          </div>
        );

      case 'heading':
        const HeadingTag = `h${Math.min(element.level || 2, 6)}` as keyof React.JSX.IntrinsicElements;
        const headingClasses = {
          1: 'text-2xl font-bold text-gray-900 mt-6 mb-3',
          2: 'text-xl font-bold text-gray-800 mt-5 mb-3',
          3: 'text-lg font-semibold text-gray-800 mt-4 mb-2',
          4: 'text-base font-semibold text-gray-700 mt-3 mb-2',
          5: 'text-sm font-semibold text-gray-700 mt-2 mb-1',
          6: 'text-sm font-medium text-gray-600 mt-2 mb-1',
        };
        return (
          <HeadingTag
            key={index}
            className={headingClasses[element.level as keyof typeof headingClasses] || headingClasses[3]}
          >
            {element.content}
          </HeadingTag>
        );

      case 'section-label':
        return (
          <div key={index} className="my-3 pl-4 border-l-4 border-indigo-300 bg-indigo-50/30 py-2 rounded-r">
            <span className="font-semibold text-indigo-700 text-sm uppercase tracking-wide">
              {element.label}:
            </span>
            {element.content && element.content !== element.label && (
              <p className="mt-1 text-gray-700 text-sm leading-relaxed">
                {element.content}
              </p>
            )}
          </div>
        );

      case 'list':
        return (
          <ul key={index} className="ml-6 mb-3 list-disc space-y-1">
            {element.items?.map((item, itemIndex) => (
              <li key={itemIndex} className="text-gray-700 text-sm leading-relaxed">
                {item}
              </li>
            ))}
          </ul>
        );

      case 'paragraph':
        return (
          <p key={index} className="mb-2 text-gray-700 text-sm leading-relaxed">
            {element.content}
          </p>
        );

      case 'empty':
        return <div key={index} className="h-2" />;

      default:
        return (
          <p key={index} className="mb-2 text-gray-700 text-sm">
            {element.content}
          </p>
        );
    }
  });
}

