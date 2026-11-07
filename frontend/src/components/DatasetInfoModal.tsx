import React, { useState } from 'react';
import { DatasetMeta } from '../types/dashboard';
import { X, Database, FileSpreadsheet, AlertTriangle, Layers, Hash, Calendar, Tag } from 'lucide-react';

interface DatasetInfoModalProps {
  isOpen: boolean;
  onClose: () => void;
  metadata?: DatasetMeta;
  onSwitchSheet: (sheetName: string) => void;
}

export const DatasetInfoModal: React.FC<DatasetInfoModalProps> = ({
  isOpen,
  onClose,
  metadata,
  onSwitchSheet,
}) => {
  const [activeTab, setActiveTab] = useState<'preview' | 'schema' | 'stats'>('preview');

  if (!isOpen || !metadata) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 flex items-center justify-center">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center">
                {metadata.filename}
                <span className="ml-2 text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 uppercase">
                  {metadata.file_type}
                </span>
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {metadata.total_rows.toLocaleString()} total rows • {metadata.total_columns} columns • {metadata.duplicate_count} duplicate rows
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Worksheet Selector if XLSX */}
        {metadata.sheet_names && metadata.sheet_names.length > 1 && (
          <div className="px-5 py-2.5 bg-slate-50 dark:bg-slate-800/40 border-b border-slate-200 dark:border-slate-800 flex items-center space-x-2 text-xs">
            <Layers className="w-4 h-4 text-brand-600" />
            <span className="font-semibold text-slate-600 dark:text-slate-300">Select Worksheet:</span>
            <div className="flex gap-1.5 overflow-x-auto">
              {metadata.sheet_names.map((s) => (
                <button
                  key={s}
                  onClick={() => onSwitchSheet(s)}
                  className={`px-3 py-1 rounded-lg font-medium transition-colors ${
                    metadata.active_sheet === s
                      ? 'bg-brand-600 text-white shadow-sm'
                      : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100'
                  }`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 px-5 text-xs font-semibold">
          <button
            onClick={() => setActiveTab('preview')}
            className={`py-3 mr-4 border-b-2 transition-colors ${
              activeTab === 'preview'
                ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            Data Preview (First 15 Rows)
          </button>
          <button
            onClick={() => setActiveTab('schema')}
            className={`py-3 mr-4 border-b-2 transition-colors ${
              activeTab === 'schema'
                ? 'border-brand-600 text-brand-600 dark:text-brand-400'
                : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
            }`}
          >
            Columns & Data Types ({metadata.columns.length})
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-auto p-5 text-xs">
          {activeTab === 'preview' && (
            <div className="border border-slate-200 dark:border-slate-800 rounded-xl overflow-x-auto">
              <table className="w-full border-collapse text-left">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/80 border-b border-slate-200 dark:border-slate-800">
                    <th className="p-2.5 font-bold text-slate-500 text-[10px] uppercase">#</th>
                    {metadata.columns.map((col) => (
                      <th key={col.name} className="p-2.5 font-bold text-slate-700 dark:text-slate-300 whitespace-nowrap">
                        {col.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-800 font-mono text-[11px]">
                  {metadata.preview_rows.map((row, idx) => (
                    <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-800/40">
                      <td className="p-2.5 text-slate-400">{idx + 1}</td>
                      {metadata.columns.map((col) => (
                        <td key={col.name} className="p-2.5 text-slate-800 dark:text-slate-200 whitespace-nowrap">
                          {row[col.name] !== null && row[col.name] !== undefined ? String(row[col.name]) : <span className="text-slate-300 dark:text-slate-600 italic">null</span>}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {activeTab === 'schema' && (
            <div className="space-y-3">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {metadata.columns.map((col) => (
                  <div
                    key={col.name}
                    className="p-3.5 bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 rounded-xl"
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center space-x-1.5 font-bold text-slate-900 dark:text-white">
                        {col.dtype === 'numeric' && <Hash className="w-3.5 h-3.5 text-brand-500" />}
                        {col.dtype === 'datetime' && <Calendar className="w-3.5 h-3.5 text-emerald-500" />}
                        {col.dtype === 'categorical' && <Tag className="w-3.5 h-3.5 text-amber-500" />}
                        <span>{col.name}</span>
                      </div>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-400 uppercase border border-slate-200 dark:border-slate-700">
                        {col.dtype}
                      </span>
                    </div>

                    <div className="grid grid-cols-3 gap-2 text-[11px] text-slate-500 dark:text-slate-400 mb-2">
                      <div>Unique: <span className="font-semibold text-slate-700 dark:text-slate-300">{col.unique_count}</span></div>
                      <div>Nulls: <span className="font-semibold text-slate-700 dark:text-slate-300">{col.null_count}</span></div>
                      {col.mean_val !== null && <div>Mean: <span className="font-semibold text-slate-700 dark:text-slate-300">{col.mean_val}</span></div>}
                    </div>

                    {col.sample_values && col.sample_values.length > 0 && (
                      <div className="text-[10px] text-slate-400 truncate">
                        Samples: {col.sample_values.slice(0, 4).join(', ')}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-semibold hover:opacity-90 transition-opacity"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
