import React from 'react';
import { KPIConfig } from '../types/dashboard';
import { TrendingUp, Trash2, Hash, DollarSign, Calculator } from 'lucide-react';

interface KPISectionProps {
  kpis: KPIConfig[];
  onDeleteKPI: (kpiId: string) => void;
  onQuickKPI: (metric: string, agg: string) => void;
  availableMetrics: string[];
}

export const KPISection: React.FC<KPISectionProps> = ({
  kpis,
  onDeleteKPI,
  onQuickKPI,
  availableMetrics,
}) => {
  if (kpis.length === 0) {
    return (
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 flex items-center">
              <TrendingUp className="w-4 h-4 mr-1.5 text-brand-600" /> Key Performance Indicators
            </h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">
              No KPI cards generated yet. Use voice/text commands or click below:
            </p>
          </div>
          {availableMetrics.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {availableMetrics.slice(0, 3).map((m) => (
                <button
                  key={m}
                  onClick={() => onQuickKPI(m, 'sum')}
                  className="px-2.5 py-1 text-xs font-medium rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 border border-slate-200 dark:border-slate-700 transition-colors"
                >
                  + Total {m}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {kpis.map((kpi) => {
        const isCurrency = kpi.prefix === '₹' || kpi.metric_col.toLowerCase().includes('sales') || kpi.metric_col.toLowerCase().includes('profit') || kpi.metric_col.toLowerCase().includes('revenue');
        return (
          <div
            key={kpi.id}
            className="group relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 shadow-sm hover:shadow-md transition-all border-l-4 border-l-brand-600"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400 truncate max-w-[80%]">
                {kpi.title}
              </span>
              <button
                onClick={() => onDeleteKPI(kpi.id)}
                className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-rose-500 rounded transition-opacity"
                title="Delete KPI"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>

            <div className="mt-2 flex items-baseline justify-between">
              <div className="text-2xl sm:text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {kpi.prefix}
                {kpi.formatted_value}
                {kpi.suffix}
              </div>
              <span className="inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 uppercase">
                {kpi.agg}
              </span>
            </div>

            <div className="mt-2 flex items-center text-xs text-slate-400 dark:text-slate-500">
              {isCurrency ? (
                <DollarSign className="w-3.5 h-3.5 mr-1 text-emerald-500" />
              ) : (
                <Hash className="w-3.5 h-3.5 mr-1 text-brand-500" />
              )}
              <span className="truncate">Metric: {kpi.metric_col}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
