import React from 'react';
import { 
  Sun, Moon, Download, Trash2, Database, Layers, 
  Sparkles, CheckCircle2, Table as TableIcon 
} from 'lucide-react';
import { DashboardState } from '../types/dashboard';

interface NavbarProps {
  state: DashboardState;
  darkMode: boolean;
  onToggleTheme: () => void;
  onOpenDatasetInfo: () => void;
  onOpenCompleteTable: () => void;
  onOpenExport: () => void;
  onClearWorkspace: () => void;
  onSwitchSheet: (sheetName: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  state,
  darkMode,
  onToggleTheme,
  onOpenDatasetInfo,
  onOpenCompleteTable,
  onOpenExport,
  onClearWorkspace,
  onSwitchSheet,
}) => {
  const meta = state.dataset_meta;

  return (
    <header className="sticky top-0 z-30 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 transition-colors shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand & Project Name */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-base font-bold text-slate-900 dark:text-white leading-tight">
                {state.project_name || 'Untitled Dashboard'}
              </h1>
              <span className="flex items-center text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/50 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                <CheckCircle2 className="w-3 h-3 mr-1" /> Active
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Multilingual Conversational BI System
            </p>
          </div>
        </div>

        {/* Middle: Dataset Info, View Complete Data & Sheet Selector */}
        {meta && (
          <div className="hidden md:flex items-center space-x-2.5">
            <button
              onClick={onOpenDatasetInfo}
              className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-xs font-medium text-slate-700 dark:text-slate-300 transition-colors border border-slate-200 dark:border-slate-700"
              title="Click to view dataset metadata & schema stats"
            >
              <Database className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
              <span>{meta.filename}</span>
              <span className="text-slate-400 dark:text-slate-500">|</span>
              <span className="font-semibold">{meta.total_rows.toLocaleString()} rows</span>
            </button>

            {/* Clearly Visible View Complete Data Button */}
            <button
              onClick={onOpenCompleteTable}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-950/70 hover:bg-indigo-100 dark:hover:bg-indigo-900/60 text-brand-700 dark:text-brand-300 font-bold text-xs border border-brand-200 dark:border-brand-800 transition-colors shadow-sm"
              title="View all rows and all columns in full-screen table view with search, pagination & sorting"
            >
              <TableIcon className="w-3.5 h-3.5 text-brand-600 dark:text-brand-400" />
              <span>View Complete Data</span>
            </button>

            {meta.sheet_names && meta.sheet_names.length > 1 && (
              <div className="flex items-center space-x-1.5 bg-slate-100 dark:bg-slate-800 px-2.5 py-1 rounded-lg border border-slate-200 dark:border-slate-700">
                <Layers className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-xs text-slate-500">Sheet:</span>
                <select
                  value={meta.active_sheet || meta.sheet_names[0]}
                  onChange={(e) => onSwitchSheet(e.target.value)}
                  className="bg-transparent text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none cursor-pointer"
                >
                  {meta.sheet_names.map((name) => (
                    <option key={name} value={name} className="dark:bg-slate-900">
                      {name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        {/* Right Actions */}
        <div className="flex items-center space-x-2">
          {/* Theme Toggle */}
          <button
            onClick={onToggleTheme}
            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-slate-600" />}
          </button>

          {/* Export Modal Button */}
          <button
            onClick={onOpenExport}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-700 text-white text-xs font-medium shadow-sm shadow-brand-600/30 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export</span>
          </button>

          {/* Clear Workspace */}
          <button
            onClick={onClearWorkspace}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 text-xs font-medium transition-colors"
            title="Reset workspace and clear temporary data"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Clear</span>
          </button>
        </div>

      </div>
    </header>
  );
};

