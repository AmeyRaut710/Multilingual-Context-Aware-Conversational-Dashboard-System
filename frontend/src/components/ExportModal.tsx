import React from 'react';
import { X, FileArchive, Globe, FileText, Download, CheckCircle2, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  sessionId: string;
  projectName: string;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  projectName,
}) => {
  if (!isOpen) return null;

  const downloadFile = (url: string, filename: string) => {
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  const safeName = projectName.toLowerCase().replace(/\s+/g, '_');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-5 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center">
              <Download className="w-5 h-5 mr-2 text-brand-600" /> Export Dashboard
            </h2>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Choose your desired export format for {projectName}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Export Options Grid */}
        <div className="p-6 space-y-4 text-xs">
          
          {/* 1. ZIP Project Export */}
          <div className="p-4 border border-brand-200 dark:border-brand-900 bg-brand-50/40 dark:bg-brand-950/20 rounded-xl flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-brand-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-brand-600/20">
                <FileArchive className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    Full Project ZIP Archive
                  </h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-brand-100 dark:bg-brand-900 text-brand-700 dark:text-brand-300">
                    Restorable
                  </span>
                </div>
                <p className="text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                  Contains original dataset, full chart configs, KPIs, active filters, and metadata.
                  Upload this ZIP later to restore your dashboard without uploading the dataset again.
                </p>
              </div>
            </div>
            <button
              onClick={() => downloadFile(api.getZipExportUrl(sessionId), `${safeName}_project.zip`)}
              className="px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white font-semibold transition-colors shrink-0 shadow-sm flex items-center space-x-1.5"
            >
              <Download className="w-4 h-4" />
              <span>Download ZIP</span>
            </button>
          </div>

          {/* 2. Standalone Interactive HTML */}
          <div className="p-4 border border-emerald-200 dark:border-emerald-900 bg-emerald-50/40 dark:bg-emerald-950/20 rounded-xl flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-emerald-600/20">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    Standalone Interactive HTML
                  </h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-700 dark:text-emerald-300">
                    Offline Ready
                  </span>
                </div>
                <p className="text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                  Self-contained HTML file embedding Plotly.js and client-side data filters.
                  Opens directly in Chrome, Edge, or Firefox. Filter dropdowns update charts offline without a backend!
                </p>
              </div>
            </div>
            <button
              onClick={() => downloadFile(api.getHtmlExportUrl(sessionId), `${safeName}_interactive.html`)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold transition-colors shrink-0 shadow-sm flex items-center space-x-1.5"
            >
              <Download className="w-4 h-4" />
              <span>Download HTML</span>
            </button>
          </div>

          {/* 3. Static PDF Report */}
          <div className="p-4 border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 rounded-xl flex items-start justify-between gap-4">
            <div className="flex items-start space-x-3.5">
              <div className="w-10 h-10 rounded-xl bg-slate-700 text-white flex items-center justify-center shrink-0">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">
                    Static PDF Report
                  </h4>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                    Document
                  </span>
                </div>
                <p className="text-slate-600 dark:text-slate-400 mt-1 leading-relaxed">
                  Clean printable summary report containing dataset statistics, KPI summary table, visualization configurations, and applied filters.
                </p>
              </div>
            </div>
            <button
              onClick={() => downloadFile(api.getPdfExportUrl(sessionId), `${safeName}_report.pdf`)}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-600 text-white font-semibold transition-colors shrink-0 shadow-sm flex items-center space-x-1.5"
            >
              <Download className="w-4 h-4" />
              <span>Download PDF</span>
            </button>
          </div>

        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 dark:bg-slate-800/50 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
          <div className="flex items-center space-x-1">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>Files are generated on-the-fly from temporary session memory.</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg border border-slate-200 dark:border-slate-700 font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};
