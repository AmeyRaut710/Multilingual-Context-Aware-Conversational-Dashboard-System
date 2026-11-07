import React from 'react';
import { FilterItem, ColumnMeta } from '../types/dashboard';
import { Filter, X, RotateCcw, Plus } from 'lucide-react';

interface FilterBarProps {
  filters: FilterItem[];
  availableColumns: ColumnMeta[];
  onApplyFilter: (column: string, value: any) => void;
  onClearFilter: (column?: string) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  availableColumns,
  onApplyFilter,
  onClearFilter,
}) => {
  // Available categorical columns that aren't yet active in filters
  const categoricalCols = availableColumns.filter(
    (c) => c.dtype === 'categorical' && c.unique_count <= 40
  );

  const activeCount = filters.filter((f) => f.current_value && f.current_value !== 'All').length;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 shadow-sm flex flex-wrap items-center justify-between gap-3">
      
      {/* Left: Filter Controls */}
      <div className="flex flex-wrap items-center gap-2.5">
        <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-700 dark:text-slate-300 pr-2 border-r border-slate-200 dark:border-slate-800">
          <Filter className="w-3.5 h-3.5 text-brand-600" />
          <span>Filters</span>
          {activeCount > 0 && (
            <span className="w-5 h-5 rounded-full bg-brand-600 text-white text-[10px] flex items-center justify-center font-bold">
              {activeCount}
            </span>
          )}
        </div>

        {/* Active Filters */}
        {filters.map((flt) => (
          <div
            key={flt.id}
            className="flex items-center space-x-1.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg px-2.5 py-1 text-xs"
          >
            <span className="font-semibold text-slate-500 dark:text-slate-400">
              {flt.column}:
            </span>
            <select
              value={flt.current_value || ''}
              onChange={(e) => onApplyFilter(flt.column, e.target.value)}
              className="bg-transparent font-medium text-slate-900 dark:text-slate-100 focus:outline-none cursor-pointer max-w-[140px] truncate"
            >
              <option value="" className="dark:bg-slate-900">All</option>
              {flt.options.map((opt) => (
                <option key={opt} value={opt} className="dark:bg-slate-900">
                  {opt}
                </option>
              ))}
            </select>
            {flt.current_value && flt.current_value !== 'All' && (
              <button
                onClick={() => onApplyFilter(flt.column, '')}
                className="text-slate-400 hover:text-rose-500 transition-colors ml-1"
                title="Clear this filter"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        ))}

        {/* Add Filter Quick Dropdown */}
        {categoricalCols.length > 0 && (
          <div className="relative inline-block">
            <select
              onChange={(e) => {
                if (e.target.value) {
                  onApplyFilter(e.target.value, '');
                  e.target.value = '';
                }
              }}
              defaultValue=""
              className="text-xs font-medium text-brand-600 dark:text-brand-400 bg-brand-50/60 dark:bg-brand-950/40 hover:bg-brand-100 dark:hover:bg-brand-900/60 border border-brand-200 dark:border-brand-800 rounded-lg px-2.5 py-1.5 focus:outline-none cursor-pointer"
            >
              <option value="" disabled>+ Add Filter Column...</option>
              {categoricalCols.map((c) => (
                <option key={c.name} value={c.name} className="dark:bg-slate-900 text-slate-900 dark:text-slate-100">
                  {c.name} ({c.unique_count} options)
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Right: Reset All Filters Button */}
      {activeCount > 0 && (
        <button
          onClick={() => onClearFilter()}
          className="flex items-center space-x-1 text-xs font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 px-2 py-1 rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Reset Filters</span>
        </button>
      )}

    </div>
  );
};
