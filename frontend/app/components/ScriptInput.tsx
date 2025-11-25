'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { ScriptInput as ScriptInputType } from '@/lib/api';

interface ScriptInputProps {
  onSubmit: (data: ScriptInputType) => void;
  isLoading?: boolean;
}

export default function ScriptInput({ onSubmit, isLoading }: ScriptInputProps) {
  const { register, handleSubmit, formState: { errors } } = useForm<ScriptInputType>({
    defaultValues: {
      enable_curriculum_aligner: true,
      enable_misconception_checker: true,
      enable_script_generator: true,
      enable_fact_checker: true,
      enable_cultural_safety: true,
      enable_accessibility: true,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-2xl font-bold text-gray-800">Generate Educational Script</h2>
      
      <div>
        <label htmlFor="topic" className="block text-sm font-medium text-gray-700 mb-2">
          Topic *
        </label>
        <input
          {...register('topic', { required: 'Topic is required' })}
          type="text"
          id="topic"
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          placeholder="e.g., Photosynthesis"
        />
        {errors.topic && (
          <p className="mt-1 text-sm text-red-600">{errors.topic.message}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="year_level" className="block text-sm font-medium text-gray-700 mb-2">
            Year Level *
          </label>
          <select
            {...register('year_level', { required: 'Year level is required' })}
            id="year_level"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((year) => (
              <option key={year} value={year.toString()}>
                Year {year}
              </option>
            ))}
          </select>
          {errors.year_level && (
            <p className="mt-1 text-sm text-red-600">{errors.year_level.message}</p>
          )}
        </div>

        <div>
          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
            Subject
          </label>
          <input
            {...register('subject')}
            type="text"
            id="subject"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
            placeholder="e.g., Science"
          />
        </div>
      </div>

      <div>
        <label htmlFor="learning_objective" className="block text-sm font-medium text-gray-700 mb-2">
          Learning Objective *
        </label>
        <textarea
          {...register('learning_objective', { required: 'Learning objective is required' })}
          id="learning_objective"
          rows={3}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900"
          placeholder="e.g., Students will understand why plants need light and water"
        />
        {errors.learning_objective && (
          <p className="mt-1 text-sm text-red-600">{errors.learning_objective.message}</p>
        )}
      </div>

      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Feature Toggles</h3>
        <div className="grid grid-cols-2 gap-3">
          {[
            { key: 'enable_curriculum_aligner', label: 'Curriculum Aligner' },
            { key: 'enable_misconception_checker', label: 'Misconception Checker' },
            { key: 'enable_script_generator', label: 'Script Generator' },
            { key: 'enable_fact_checker', label: 'Fact Checker' },
            { key: 'enable_cultural_safety', label: 'Cultural Safety' },
            { key: 'enable_accessibility', label: 'Accessibility' },
          ].map(({ key, label }) => (
            <label key={key} className="flex items-center space-x-2">
              <input
                {...register(key as keyof ScriptInputType)}
                type="checkbox"
                className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              />
              <span className="text-sm text-gray-700">{label}</span>
            </label>
          ))}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-md font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Generating...' : 'Generate Script'}
      </button>
    </form>
  );
}



