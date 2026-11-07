import React, { useState, useRef, useEffect } from 'react';
import { FilterItem, ColumnMeta } from '../types/dashboard';
import { Filter, X, RotateCcw, ChevronDown, Check, Search, Trash2 } from 'lucide-react';

interface FilterBarProps {
  filters: FilterItem[];
  availableColumns: ColumnMeta[];
  onApplyFilter: (column: string, value: any) => void;
  onClearFilter: (column?: string) => void;
  onRemoveSlicer?: (column: string) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  availableColumns,
  onApplyFilter,
  onClearFilter,
  onRemoveSlicer,
}) => {
  const [openDropdownCol, setOpenDropdownCol] = useState<string | null>(null);
  const [searchTerms, setSearchTerms] = useState<Record<string, string>>({});
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setOpenDropdownCol(null);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter columns that aren't yet added as slicers
  const activeColNames = new Set(filters.map((f) => f.column));
  const candidateCols = availableColumns.filter(
    (c) => (c.dtype === 'categorical' || c.dtype === 'boolean') && !activeColNames.has(c.name)
  );

  // Check how many filters currently have active constraints
  const getSelectedArray = (flt: FilterItem): string[] => {
    if (!flt.current_value) return [];
    if (Array.isArray(flt.current_value)) return flt.current_value.map(String);
    if (flt.current_value === 'All' || flt.current_value === 'all' || flt.current_value === '') return [];
    return [String(flt.current_value)];
  };

  const activeFiltersCount = filters.filter((flt) => getSelectedArray(flt).length > 0).length;

  const handleToggleOption = (flt: FilterItem, option: string) => {
    const current = getSelectedArray(flt);
    let updated: string[];
    if (current.includes(option)) {
      updated = current.filter((item) => item !== option);
    } else {
      updated = [...current, option];
    }
    onApplyFilter(flt.column, updated.length > 0 ? updated : []);
  };

  const handleRemoveSingleTag = (flt: FilterItem, option: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const current = getSelectedArray(flt);
    const updated = current.filter((item) => item !== option);
    onApplyFilter(flt.column, updated.length > 0 ? updated : []);
  };

  const handleSelectAll = (flt: FilterItem) => {
    onApplyFilter(flt.column, [...flt.options]);
  };

  const handleClearSingleFilter = (flt: FilterItem, e?: React.MouseEvent) => {
    if (e) e.stopPropagation();
    onClearFilter(flt.column);
  };

  return (
    <div
      ref={dropdownRef}
      className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-3.5 shadow-sm space-y-3"
    >
      {/* Top Header Row */}
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex items-center space-x-2">
          <div className="w-7 h-7 rounded-lg bg-brand-50 dark:bg-brand-950/60 text-brand-600 dark:text-brand-400 flex items-center justify-center">
            <Filter className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-800 dark:text-slate-200">
                Dashboard Slicers & Filters
              </span>
              {activeFiltersCount > 0 && (
                <span className="px-1.5 py-0.5 rounded-full bg-brand-600 text-white text-[10px] font-bold">
                  {activeFiltersCount} active
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Interactive multi-select filters applying across all charts, KPIs and data views.
            </p>
          </div>
        </div>

        {/* Global Controls: Reset All and Add Slicer */}
        <div className="flex items-center space-x-2">
          {activeFiltersCount > 0 && (
            <button
              onClick={() => onClearFilter()}
              className="inline-flex items-center space-x-1 px-2.5 py-1 text-xs font-medium text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 rounded-lg transition-colors shadow-2xs"
              title="Clear all active selections"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Clear All Filters</span>
            </button>
          )}

          {candidateCols.length > 0 && (
            <div className="relative inline-block">
              <select
                onChange={(e) => {
                  if (e.target.value) {
                    onApplyFilter(e.target.value, []);
                    e.target.value = '';
                  }
                }}
                defaultValue=""
                className="text-xs font-medium text-brand-600 dark:text-brand-400 bg-brand-50/70 dark:bg-brand-950/40 hover:bg-brand-100 dark:hover:bg-brand-900/60 border border-brand-200 dark:border-brand-800 rounded-lg px-2.5 py-1 focus:outline-none cursor-pointer"
              >
                <option value="" disabled>
                  + Add Slicer...
                </option>
                {candidateCols.map((c) => (
                  <option key={c.name} value={c.name} className="dark:bg-slate-900 text-slate-900 dark:text-slate-100">
                    {c.name} ({c.unique_count} values)
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Slicers Grid / List */}
      {filters.length === 0 ? (
        <div className="text-xs text-slate-500 dark:text-slate-400 italic py-1 px-1">
          No active slicers. Say &quot;Add the slicer of Region and State&quot; or click &quot;+ Add Slicer&quot; above.
        </div>
      ) : (
        <div className="flex flex-wrap items-center gap-2.5 pt-1">
          {filters.map((flt) => {
            const selected = getSelectedArray(flt);
            const isOpen = openDropdownCol === flt.column;
            const searchTerm = (searchTerms[flt.column] || '').toLowerCase();
            const filteredOptions = flt.options.filter((opt) =>
              String(opt).toLowerCase().includes(searchTerm)
            );
            const isAllSelected = flt.options.length > 0 && selected.length === flt.options.length;

            return (
              <div key={flt.id || flt.column} className="relative">
                {/* Slicer Pill / Trigger */}
                <div
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border text-xs transition-all ${
                    selected.length > 0
                      ? 'bg-brand-50/80 dark:bg-brand-950/40 border-brand-300 dark:border-brand-700 text-brand-900 dark:text-brand-100 shadow-2xs'
                      : 'bg-slate-50 dark:bg-slate-800/80 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-600'
                  }`}
                >
                  {/* Column Label */}
                  <span className="font-semibold text-slate-500 dark:text-slate-400">
                    {flt.column}:
                  </span>

                  {/* Active Selection Summary */}
                  <button
                    type="button"
                    onClick={() => setOpenDropdownCol(isOpen ? null : flt.column)}
                    className="flex items-center space-x-1 font-medium hover:underline focus:outline-none"
                  >
                    {selected.length === 0 ? (
                      <span className="text-slate-600 dark:text-slate-300">All ({flt.options.length})</span>
                    ) : selected.length === 1 ? (
                      <span className="font-bold text-brand-700 dark:text-brand-300">{selected[0]}</span>
                    ) : (
                      <span className="font-bold text-brand-700 dark:text-brand-300">
                        {selected.length} selected
                      </span>
                    )}
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  </button>

                  {/* Quick Individual Clear Badge */}
                  {selected.length > 0 && (
                    <button
                      type="button"
                      onClick={(e) => handleClearSingleFilter(flt, e)}
                      className="p-0.5 rounded hover:bg-brand-200/60 dark:hover:bg-brand-900/60 text-brand-600 dark:text-brand-400 ml-0.5"
                      title={`Clear ${flt.column} filter`}
                    >
                      <X className="w-3 h-3" />
                    </button>
                  )}

                  {/* Remove Slicer Button */}
                  {onRemoveSlicer && (
                    <button
                      type="button"
                      onClick={() => onRemoveSlicer(flt.column)}
                      className="p-0.5 rounded text-slate-300 dark:text-slate-600 hover:text-rose-500 dark:hover:text-rose-400 transition-colors ml-1"
                      title={`Remove ${flt.column} slicer from dashboard`}
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  )}
                </div>

                {/* Selected Tags Chips (when 2 to 4 items selected) */}
                {selected.length > 0 && selected.length <= 3 && (
                  <div className="flex flex-wrap items-center gap-1 mt-1 pl-1">
                    {selected.map((item) => (
                      <span
                        key={item}
                        className="inline-flex items-center space-x-1 px-1.5 py-0.5 bg-brand-100 dark:bg-brand-900/60 text-brand-800 dark:text-brand-200 rounded text-[10px] font-medium"
                      >
                        <span className="truncate max-w-[100px]">{item}</span>
                        <button
                          type="button"
                          onClick={(e) => handleRemoveSingleTag(flt, item, e)}
                          className="hover:text-rose-600"
                        >
                          <X className="w-2.5 h-2.5" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {/* Dropdown Popover */}
                {isOpen && (
                  <div className="absolute left-0 mt-1.5 w-64 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-xl z-50 p-2.5 animate-fadeIn space-y-2">
                    {/* Search inside options */}
                    <div className="relative">
                      <Search className="w-3.5 h-3.5 absolute left-2 top-2 text-slate-400" />
                      <input
                        type="text"
                        placeholder={`Search ${flt.column}...`}
                        value={searchTerms[flt.column] || ''}
                        onChange={(e) =>
                          setSearchTerms((prev) => ({ ...prev, [flt.column]: e.target.value }))
                        }
                        className="w-full text-xs pl-7 pr-2 py-1.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-800 dark:text-slate-200 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
                      />
                    </div>

                    {/* Quick selection actions */}
                    <div className="flex items-center justify-between text-[11px] px-1 py-0.5 border-b border-slate-100 dark:border-slate-800">
                      <button
                        type="button"
                        onClick={() => handleSelectAll(flt)}
                        className="text-brand-600 dark:text-brand-400 hover:underline font-semibold"
                      >
                        {isAllSelected ? 'All Selected' : 'Select All'}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleClearSingleFilter(flt)}
                        className="text-slate-500 dark:text-slate-400 hover:text-rose-500 font-semibold"
                      >
                        Clear Selection
                      </button>
                    </div>

                    {/* Options Checkbox List */}
                    <div className="max-h-52 overflow-y-auto space-y-1 pr-1 custom-scrollbar text-xs">
                      {filteredOptions.length === 0 ? (
                        <div className="text-center py-4 text-xs text-slate-400 italic">
                          No matching options
                        </div>
                      ) : (
                        filteredOptions.map((opt) => {
                          const isChecked = selected.includes(String(opt));
                          return (
                            <label
                              key={String(opt)}
                              className="flex items-center space-x-2 px-2 py-1.5 rounded-md hover:bg-slate-50 dark:hover:bg-slate-800 cursor-pointer transition-colors"
                            >
                              <input
                                type="checkbox"
                                checked={isChecked}
                                onChange={() => handleToggleOption(flt, String(opt))}
                                className="w-3.5 h-3.5 rounded border-slate-300 dark:border-slate-600 text-brand-600 focus:ring-brand-500"
                              />
                              <span
                                className={`truncate text-xs ${
                                  isChecked
                                    ? 'font-bold text-slate-900 dark:text-slate-100'
                                    : 'font-normal text-slate-700 dark:text-slate-300'
                                }`}
                              >
                                {opt}
                              </span>
                            </label>
                          );
                        })
                      )}
                    </div>

                    {/* Footer with Done button */}
                    <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex justify-between items-center text-[11px]">
                      <span className="text-slate-400">
                        {selected.length} of {flt.options.length} selected
                      </span>
                      <button
                        type="button"
                        onClick={() => setOpenDropdownCol(null)}
                        className="px-2.5 py-1 bg-brand-600 text-white rounded-md font-semibold text-xs hover:bg-brand-700 transition-colors shadow-2xs"
                      >
                        Done
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
