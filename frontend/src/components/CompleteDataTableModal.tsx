import React, { useState, useEffect, useCallback } from 'react';
import { 
  X, Search, ArrowUpDown, ArrowUp, ArrowDown, Filter, 
  RotateCcw, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, 
  Table as TableIcon, Hash, Calendar, Tag, Layers, Loader2, Download
} from 'lucide-react';
import { api } from '../services/api';
import { DataTableResponse, ColumnMeta } from '../types/dashboard';

interface CompleteDataTableModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  filename?: string;
  activeSheet?: string;
}

export const CompleteDataTableModal: React.FC<CompleteDataTableModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  filename = 'Dataset',
  activeSheet,
}) => {
  const [data, setData] = useState<DataTableResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Table state
  const [page, setPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(100);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [appliedSearch, setAppliedSearch] = useState<string>('');
  const [sortBy, setSortBy] = useState<string | undefined>(undefined);
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>({});
  const [showColumnFilters, setShowColumnFilters] = useState<boolean>(false);
  const [jumpPageInput, setJumpPageInput] = useState<string>('');

  // Fetch paginated table data from backend
  const fetchData = useCallback(async (
    targetPage: number,
    targetPageSize: number,
    search?: string,
    sortCol?: string,
    sortDir?: 'asc' | 'desc',
    colFilters?: Record<string, string>
  ) => {
    if (!sessionId) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.fetchCompleteDataTable({
        session_id: sessionId,
        page: targetPage,
        page_size: targetPageSize,
        search: search || undefined,
        sort_by: sortCol,
        sort_order: sortDir,
        column_filters: colFilters && Object.keys(colFilters).length > 0 ? colFilters : undefined,
      });
      setData(res);
      setPage(res.current_page);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch dataset table rows.');
    } finally {
      setIsLoading(false);
    }
  }, [sessionId]);

  // Initial load when modal opens or sessionId changes
  useEffect(() => {
    if (isOpen) {
      fetchData(page, pageSize, appliedSearch, sortBy, sortOrder, columnFilters);
    }
  }, [isOpen, page, pageSize, appliedSearch, sortBy, sortOrder, columnFilters, fetchData]);

  // Handle escape key to close
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  // Sorting handler
  const handleSort = (colName: string) => {
    let nextOrder: 'asc' | 'desc' = 'asc';
    if (sortBy === colName) {
      nextOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    }
    setSortBy(colName);
    setSortOrder(nextOrder);
    setPage(1);
  };

  // Search submit
  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setAppliedSearch(searchTerm.trim());
    setPage(1);
  };

  // Clear search
  const handleClearSearch = () => {
    setSearchTerm('');
    setAppliedSearch('');
    setPage(1);
  };

  // Column filter change
  const handleColumnFilterChange = (colName: string, val: string) => {
    const updated = { ...columnFilters };
    if (!val.trim()) {
      delete updated[colName];
    } else {
      updated[colName] = val;
    }
    setColumnFilters(updated);
    setPage(1);
  };

  // Reset all sorting & filters
  const handleResetAll = () => {
    setSearchTerm('');
    setAppliedSearch('');
    setSortBy(undefined);
    setSortOrder('asc');
    setColumnFilters({});
    setPage(1);
  };

  // Page Jump
  const handleJumpPage = (e: React.FormEvent) => {
    e.preventDefault();
    const p = parseInt(jumpPageInput, 10);
    if (data && !isNaN(p) && p >= 1 && p <= data.total_pages) {
      setPage(p);
      setJumpPageInput('');
    }
  };

  // Helper to get column metadata type
  const getColMeta = (colName: string): ColumnMeta | undefined => {
    return data?.columns_meta?.find((c) => c.name === colName);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-slate-900/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-[98vw] h-[95vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* TOP BAR: Header & Stats */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/40">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-brand-600 text-white flex items-center justify-center shadow-md shadow-brand-600/20">
              <TableIcon className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-slate-900 dark:text-white">
                  Complete Dataset Table
                </h2>
                <span className="text-xs px-2 py-0.5 rounded-md bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-300 font-semibold border border-brand-200 dark:border-brand-800">
                  {filename}
                </span>
                {activeSheet && (
                  <span className="text-xs px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-medium flex items-center">
                    <Layers className="w-3 h-3 mr-1 text-slate-400" />
                    {activeSheet}
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2 mt-0.5 text-xs text-slate-500 dark:text-slate-400">
                <span>
                  Total Rows: <b className="text-slate-900 dark:text-white">{data?.total_rows.toLocaleString() || '...'}</b>
                </span>
                <span>•</span>
                <span>
                  Total Columns: <b className="text-slate-900 dark:text-white">{data?.total_columns || '...'}</b>
                </span>
                {data && data.filtered_rows !== data.total_rows && (
                  <>
                    <span>•</span>
                    <span className="text-brand-600 dark:text-brand-400 font-semibold">
                      Matching Filter: {data.filtered_rows.toLocaleString()} rows
                    </span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              title="Close Table (Esc)"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* CONTROLS TOOLBAR: Search, Page Size, Column Filter Toggle, Reset */}
        <div className="px-6 py-3 border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-wrap items-center justify-between gap-3 text-xs">
          
          {/* Left: Global Search Form */}
          <form onSubmit={handleSearchSubmit} className="flex items-center space-x-2 flex-1 max-w-md">
            <div className="relative w-full">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search across all columns (press Enter)..."
                className="w-full pl-9 pr-8 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
              />
              {searchTerm && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  className="absolute right-2.5 top-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              )}
            </div>
            <button
              type="submit"
              className="px-3.5 py-2 bg-brand-600 hover:bg-brand-700 text-white font-semibold rounded-xl transition-colors shadow-sm shrink-0"
            >
              Search
            </button>
          </form>

          {/* Right Controls: Page Size, Column Filters Toggle, Reset */}
          <div className="flex items-center space-x-3">
            {/* Page Size Selector */}
            <div className="flex items-center space-x-1.5">
              <span className="font-semibold text-slate-500 dark:text-slate-400">Rows per page:</span>
              <select
                value={pageSize}
                onChange={(e) => {
                  setPageSize(Number(e.target.value));
                  setPage(1);
                }}
                className="bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-slate-200 font-bold rounded-lg px-2.5 py-1.5 focus:outline-none cursor-pointer"
              >
                <option value={25}>25</option>
                <option value={50}>50</option>
                <option value={100}>100</option>
                <option value={250}>250</option>
              </select>
            </div>

            {/* Column Filters Toggle */}
            <button
              type="button"
              onClick={() => setShowColumnFilters(!showColumnFilters)}
              className={`px-3 py-1.5 rounded-lg border font-semibold flex items-center space-x-1 transition-colors ${
                showColumnFilters || Object.keys(columnFilters).length > 0
                  ? 'bg-brand-50 dark:bg-brand-950/60 border-brand-300 dark:border-brand-800 text-brand-600 dark:text-brand-300'
                  : 'bg-slate-100 dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200'
              }`}
            >
              <Filter className="w-3.5 h-3.5" />
              <span>Column Filters {Object.keys(columnFilters).length > 0 ? `(${Object.keys(columnFilters).length})` : ''}</span>
            </button>

            {/* Reset All Filters & Sorting */}
            {(appliedSearch || sortBy || Object.keys(columnFilters).length > 0) && (
              <button
                type="button"
                onClick={handleResetAll}
                className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-semibold flex items-center space-x-1 transition-colors"
                title="Reset search, sorting and column filters"
              >
                <RotateCcw className="w-3 h-3 text-slate-500" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>

        {/* ERROR NOTIFICATION */}
        {error && (
          <div className="mx-6 my-2 p-3 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-800 rounded-xl text-rose-600 text-xs">
            {error}
          </div>
        )}

        {/* MAIN DATA TABLE (Scrollable area) */}
        <div className="flex-1 overflow-auto relative">
          {isLoading && (
            <div className="absolute inset-0 z-20 bg-white/60 dark:bg-slate-900/60 backdrop-blur-[2px] flex items-center justify-center">
              <div className="flex items-center space-x-2 text-xs font-semibold text-brand-600 dark:text-brand-400 bg-white dark:bg-slate-800 px-4 py-2.5 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Fetching table rows from dataset...</span>
              </div>
            </div>
          )}

          <table className="w-full border-collapse text-left text-xs">
            {/* Table Header */}
            <thead className="sticky top-0 z-10 bg-slate-100 dark:bg-slate-800 shadow-sm border-b border-slate-200 dark:border-slate-700">
              <tr>
                {/* Row Number Column */}
                <th className="px-3 py-3 w-16 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-center border-r border-slate-200 dark:border-slate-700">
                  #
                </th>
                {data?.columns.map((col) => {
                  const meta = getColMeta(col);
                  const isSorted = sortBy === col;
                  return (
                    <th
                      key={col}
                      onClick={() => handleSort(col)}
                      className={`px-3.5 py-3 text-[11px] font-bold text-slate-800 dark:text-slate-200 whitespace-nowrap cursor-pointer select-none hover:bg-slate-200/70 dark:hover:bg-slate-700/60 transition-colors border-r border-slate-200 dark:border-slate-700 ${
                        isSorted ? 'bg-brand-50/70 dark:bg-brand-950/40 text-brand-600 dark:text-brand-300' : ''
                      }`}
                      title={`Click to sort by ${col}`}
                    >
                      <div className="flex items-center justify-between space-x-2">
                        <div className="flex items-center space-x-1.5">
                          {meta?.dtype === 'numeric' && <Hash className="w-3 h-3 text-brand-500" />}
                          {meta?.dtype === 'datetime' && <Calendar className="w-3 h-3 text-emerald-500" />}
                          {meta?.dtype === 'categorical' && <Tag className="w-3 h-3 text-amber-500" />}
                          <span>{col}</span>
                        </div>
                        <div className="text-slate-400">
                          {isSorted ? (
                            sortOrder === 'asc' ? (
                              <ArrowUp className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
                            ) : (
                              <ArrowDown className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
                            )
                          ) : (
                            <ArrowUpDown className="w-3 h-3 opacity-40 hover:opacity-100" />
                          )}
                        </div>
                      </div>
                    </th>
                  );
                })}
              </tr>

              {/* Optional Individual Column Filters Row */}
              {showColumnFilters && (
                <tr className="bg-slate-50 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-700">
                  <td className="p-1 border-r border-slate-200 dark:border-slate-700 text-center text-slate-400 text-[10px]">
                    Filter
                  </td>
                  {data?.columns.map((col) => (
                    <td key={`filter_${col}`} className="p-1 border-r border-slate-200 dark:border-slate-700">
                      <input
                        type="text"
                        value={columnFilters[col] || ''}
                        onChange={(e) => handleColumnFilterChange(col, e.target.value)}
                        placeholder={`Filter ${col}...`}
                        className="w-full px-2 py-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded text-[11px] text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-500"
                      />
                    </td>
                  ))}
                </tr>
              )}
            </thead>

            {/* Table Body */}
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
              {data && data.rows.length > 0 ? (
                data.rows.map((row, idx) => {
                  const absoluteIndex = (data.current_page - 1) * data.page_size + idx + 1;
                  return (
                    <tr
                      key={idx}
                      className="hover:bg-slate-50 dark:hover:bg-slate-800/40 transition-colors"
                    >
                      <td className="px-3 py-2 text-slate-400 text-center border-r border-slate-100 dark:border-slate-800 font-sans select-none">
                        {absoluteIndex}
                      </td>
                      {data.columns.map((col) => {
                        const val = row[col];
                        const isNull = val === null || val === undefined || val === '';
                        return (
                          <td
                            key={col}
                            className="px-3.5 py-2 text-slate-800 dark:text-slate-200 whitespace-nowrap border-r border-slate-100 dark:border-slate-800"
                          >
                            {isNull ? (
                              <span className="italic text-slate-400 dark:text-slate-500 text-[10px] px-1 py-0.5 rounded bg-slate-100 dark:bg-slate-800/80">
                                null
                              </span>
                            ) : (
                              String(val)
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td
                    colSpan={(data?.columns.length || 0) + 1}
                    className="py-12 text-center text-slate-400 font-sans text-sm"
                  >
                    No matching records found in dataset.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* BOTTOM PAGINATION BAR */}
        <div className="px-6 py-3 border-t border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 flex flex-wrap items-center justify-between gap-3 text-xs">
          
          {/* Left: Record Range Summary */}
          <div className="text-slate-500 dark:text-slate-400 font-medium">
            Showing <b className="text-slate-900 dark:text-white">{data?.start_row || 0}</b> to{' '}
            <b className="text-slate-900 dark:text-white">{data?.end_row || 0}</b> of{' '}
            <b className="text-slate-900 dark:text-white">{data?.filtered_rows.toLocaleString() || 0}</b> rows
            {data && data.filtered_rows !== data.total_rows && (
              <span> (filtered from {data.total_rows.toLocaleString()} total)</span>
            )}
          </div>

          {/* Center / Right: Pagination Controls */}
          <div className="flex items-center space-x-1.5">
            {/* First Page */}
            <button
              onClick={() => setPage(1)}
              disabled={page <= 1 || isLoading}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              title="First Page"
            >
              <ChevronsLeft className="w-4 h-4" />
            </button>

            {/* Previous Page */}
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || isLoading}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              title="Previous Page"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>

            {/* Current Page Indicator */}
            <span className="px-3 py-1 font-bold text-slate-900 dark:text-white bg-slate-200/70 dark:bg-slate-700 rounded-lg text-xs">
              Page {data?.current_page || 1} of {data?.total_pages || 1}
            </span>

            {/* Next Page */}
            <button
              onClick={() => setPage((p) => Math.min(data?.total_pages || 1, p + 1))}
              disabled={data ? page >= data.total_pages || isLoading : true}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              title="Next Page"
            >
              <ChevronRight className="w-4 h-4" />
            </button>

            {/* Last Page */}
            <button
              onClick={() => setPage(data?.total_pages || 1)}
              disabled={data ? page >= data.total_pages || isLoading : true}
              className="p-1.5 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              title="Last Page"
            >
              <ChevronsRight className="w-4 h-4" />
            </button>

            {/* Jump to Page Form */}
            {data && data.total_pages > 1 && (
              <form onSubmit={handleJumpPage} className="flex items-center space-x-1 pl-2 border-l border-slate-200 dark:border-slate-700">
                <span className="text-[11px] text-slate-400">Go to:</span>
                <input
                  type="number"
                  min={1}
                  max={data.total_pages}
                  value={jumpPageInput}
                  onChange={(e) => setJumpPageInput(e.target.value)}
                  placeholder="#"
                  className="w-12 px-1.5 py-1 text-center bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded text-xs text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-brand-500"
                />
              </form>
            )}

            {/* Close Button */}
            <button
              onClick={onClose}
              className="ml-3 px-4 py-1.5 bg-slate-900 dark:bg-white text-white dark:text-slate-900 font-bold rounded-xl hover:opacity-90 transition-opacity"
            >
              Close
            </button>
          </div>

        </div>

      </div>
    </div>
  );
};

