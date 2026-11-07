import React from 'react';
import { ChartConfig } from '../types/dashboard';
import { ChartCard } from './ChartCard';
import { BarChart3, Sparkles } from 'lucide-react';

interface ChartGridProps {
  charts: ChartConfig[];
  selectedChartId?: string;
  darkMode: boolean;
  onSelectChart: (chartId: string) => void;
  onDeleteChart: (chartId: string) => void;
  onUpdateChartType: (chartId: string, newType: string) => void;
  onToggleWidth: (chartId: string) => void;
  onSuggestedCommand: (cmd: string) => void;
}

export const ChartGrid: React.FC<ChartGridProps> = ({
  charts,
  selectedChartId,
  darkMode,
  onSelectChart,
  onDeleteChart,
  onUpdateChartType,
  onToggleWidth,
  onSuggestedCommand,
}) => {
  if (charts.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-2xl p-12 text-center shadow-sm">
        <div className="w-14 h-14 mx-auto rounded-2xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center mb-4">
          <BarChart3 className="w-7 h-7" />
        </div>
        <h3 className="text-base font-bold text-slate-800 dark:text-slate-200">
          No Visualizations Yet
        </h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 max-w-md mx-auto mt-1 mb-6">
          Start generating charts using natural language voice or text commands in English, Hindi, or Marathi.
        </p>
        <div className="flex flex-wrap justify-center gap-2 max-w-lg mx-auto">
          <button
            onClick={() => onSuggestedCommand('Create a bar chart of sales by region')}
            className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 border border-slate-200 dark:border-slate-700 flex items-center"
          >
            <Sparkles className="w-3 h-3 mr-1 text-brand-500" /> "Create a bar chart of sales by region"
          </button>
          <button
            onClick={() => onSuggestedCommand('Monthly sales ka bar chart banao')}
            className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 border border-slate-200 dark:border-slate-700 flex items-center"
          >
            <Sparkles className="w-3 h-3 mr-1 text-amber-500" /> "Monthly sales ka bar chart banao"
          </button>
          <button
            onClick={() => onSuggestedCommand('Monthly sales cha line chart tayar kara')}
            className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 border border-slate-200 dark:border-slate-700 flex items-center"
          >
            <Sparkles className="w-3 h-3 mr-1 text-emerald-500" /> "Monthly sales cha line chart tayar kara"
          </button>
          <button
            onClick={() => onSuggestedCommand('Top 5 products by profit dikhao')}
            className="text-xs px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 border border-slate-200 dark:border-slate-700 flex items-center"
          >
            <Sparkles className="w-3 h-3 mr-1 text-indigo-500" /> "Top 5 products by profit dikhao"
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      {charts.map((chart) => (
        <ChartCard
          key={chart.id}
          chart={chart}
          isSelected={chart.id === selectedChartId}
          darkMode={darkMode}
          onSelect={onSelectChart}
          onDelete={onDeleteChart}
          onUpdateType={onUpdateChartType}
          onToggleWidth={onToggleWidth}
        />
      ))}
    </div>
  );
};
