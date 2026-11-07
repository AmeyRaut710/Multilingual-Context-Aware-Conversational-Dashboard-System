import React, { useState } from 'react';
import { 
  Sparkles, Upload, FileSpreadsheet, FileArchive, ArrowRight, 
  CheckCircle2, Shield, Languages, Mic, BarChart2, AlertCircle 
} from 'lucide-react';
import { api } from '../services/api';
import { DashboardState } from '../types/dashboard';

interface WelcomePageProps {
  onProjectLoaded: (sessionId: string, state: DashboardState) => void;
  darkMode: boolean;
}

export const WelcomePage: React.FC<WelcomePageProps> = ({ onProjectLoaded, darkMode }) => {
  const [activeTab, setActiveTab] = useState<'new' | 'restore'>('new');
  const [projectName, setProjectName] = useState('Retail Sales Analytics');
  const [file, setFile] = useState<File | null>(null);
  const [zipFile, setZipFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleCreateNew = async () => {
    if (!file) {
      setErrorMessage('Please select a CSV or Excel dataset file.');
      return;
    }
    setErrorMessage(null);
    setIsLoading(true);
    try {
      // 1. Create project
      const proj = await api.createProject(projectName.trim() || 'Untitled Dashboard');
      // 2. Upload dataset
      const dsRes = await api.uploadDataset(proj.session_id, file);
      onProjectLoaded(proj.session_id, dsRes.state);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to initialize project with dataset.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoadSample = async (sampleType: 'csv' | 'xlsx') => {
    setErrorMessage(null);
    setIsLoading(true);
    try {
      const proj = await api.createProject(
        sampleType === 'csv' ? 'Superstore Sales Analytics' : 'Retail Multi-Sheet Analytics'
      );

      // Fetch the sample file from sample_datasets or static endpoint
      const filename = sampleType === 'csv' ? 'superstore_sales.csv' : 'retail_sales_multisheet.xlsx';
      
      // Let's create dummy blob or fetch from sample datasets via standard fetch
      // In Vite dev, we can fetch from backend static or read via sample data
      const sampleBlobRes = await fetch(`/api/health`);
      
      // To load the sample directly, we can read the file via an input or let user drag and drop
      // Or we can post a special sample dataset trigger!
      // Let's load the sample file from public or fetch it:
      const res = await fetch(`/sample_datasets/${filename}`);
      let sampleBlob: Blob;
      if (res.ok) {
        sampleBlob = await res.blob();
      } else {
        // Fallback: create mock sales CSV on the fly
        const mockCsv = `Order_ID,Order_Date,Region,State,Category,Sub_Category,Product_Name,Sales,Quantity,Discount,Profit
ORD-2023-1001,2023-01-15,West,Maharashtra,Electronics,Phones,Smart Phone Pro,18500,2,0.05,2400
ORD-2023-1002,2023-02-10,South,Karnataka,Furniture,Chairs,Ergonomic Chair,8500,3,0.1,1200
ORD-2023-1003,2023-03-05,North,Delhi,Electronics,Laptops,Gaming Laptop,45000,1,0.0,7800
ORD-2023-1004,2023-04-12,West,Maharashtra,Clothing,Shirts,Cotton Shirt,1200,4,0.15,350
ORD-2023-1005,2023-05-20,East,West Bengal,Office Supplies,Binders,Premium Binder,850,5,0.0,210
ORD-2023-1006,2023-06-18,Central,Madhya Pradesh,Electronics,Accessories,Wireless Mouse,1400,2,0.05,450
ORD-2024-1007,2024-01-22,South,Tamil Nadu,Furniture,Tables,Dining Table,16000,1,0.1,3100
ORD-2024-1008,2024-02-14,North,Punjab,Electronics,Phones,Smart Phone Plus,22000,2,0.05,3900`;
        sampleBlob = new Blob([mockCsv], { type: 'text/csv' });
      }

      const sampleFile = new File([sampleBlob], filename, {
        type: sampleType === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      });

      const dsRes = await api.uploadDataset(proj.session_id, sampleFile);
      onProjectLoaded(proj.session_id, dsRes.state);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load sample dataset.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleRestoreZip = async () => {
    if (!zipFile) {
      setErrorMessage('Please select a project ZIP file to restore.');
      return;
    }
    setErrorMessage(null);
    setIsLoading(true);
    try {
      const res = await api.uploadProjectZip(zipFile);
      onProjectLoaded(res.session_id, res.state);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to restore project from ZIP.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-between py-12 px-4 sm:px-6 lg:px-8 bg-slate-50 dark:bg-slate-950 transition-colors">
      <div className="max-w-4xl mx-auto w-full">
        
        {/* Header Hero */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-50 dark:bg-brand-950/60 border border-brand-200 dark:border-brand-800 text-brand-700 dark:text-brand-300 text-xs font-semibold mb-4">
            <Sparkles className="w-3.5 h-3.5 text-brand-600" />
            <span>Multilingual Context-Aware Analytics System</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Conversational Dashboard Intelligence
          </h1>
          <p className="mt-3 text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            Create, modify, and explore interactive business dashboards using natural speech and text commands in English, Hindi, Marathi, and mixed languages.
          </p>

          {/* Highlights Badges */}
          <div className="flex flex-wrap items-center justify-center gap-3 mt-5 text-xs text-slate-600 dark:text-slate-400">
            <span className="flex items-center space-x-1 bg-white dark:bg-slate-900 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800 shadow-sm">
              <Languages className="w-3.5 h-3.5 text-brand-600" />
              <span>English • हिन्दी • मराठी</span>
            </span>
            <span className="flex items-center space-x-1 bg-white dark:bg-slate-900 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800 shadow-sm">
              <Mic className="w-3.5 h-3.5 text-emerald-600" />
              <span>Voice & Text Input</span>
            </span>
            <span className="flex items-center space-x-1 bg-white dark:bg-slate-900 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-800 shadow-sm">
              <Shield className="w-3.5 h-3.5 text-amber-600" />
              <span>Privacy First • No Permanent DB</span>
            </span>
          </div>
        </div>

        {/* Main Card with Tabs */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl shadow-xl overflow-hidden">
          
          {/* Tab Selector */}
          <div className="grid grid-cols-2 border-b border-slate-200 dark:border-slate-800 text-sm font-bold">
            <button
              onClick={() => { setActiveTab('new'); setErrorMessage(null); }}
              className={`py-4 px-6 flex items-center justify-center space-x-2 transition-colors ${
                activeTab === 'new'
                  ? 'border-b-2 border-brand-600 text-brand-600 dark:text-brand-400 bg-brand-50/20 dark:bg-brand-950/10'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              <FileSpreadsheet className="w-4 h-4" />
              <span>Option 1: New Project</span>
            </button>

            <button
              onClick={() => { setActiveTab('restore'); setErrorMessage(null); }}
              className={`py-4 px-6 flex items-center justify-center space-x-2 transition-colors ${
                activeTab === 'restore'
                  ? 'border-b-2 border-brand-600 text-brand-600 dark:text-brand-400 bg-brand-50/20 dark:bg-brand-950/10'
                  : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'
              }`}
            >
              <FileArchive className="w-4 h-4" />
              <span>Option 2: Upload Existing Project</span>
            </button>
          </div>

          <div className="p-6 sm:p-8">
            {/* Error Message Alert */}
            {errorMessage && (
              <div className="mb-6 p-3.5 bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900 rounded-xl text-rose-600 dark:text-rose-400 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMessage}</span>
              </div>
            )}

            {/* TAB 1: NEW PROJECT */}
            {activeTab === 'new' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                    Project Name
                  </label>
                  <input
                    type="text"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="Enter project name..."
                    className="w-full bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/30"
                  />
                </div>

                {/* Dropzone for Dataset */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                    Upload Dataset (.CSV or .XLSX)
                  </label>
                  <div
                    onClick={() => document.getElementById('datasetInput')?.click()}
                    className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand-500 dark:hover:border-brand-500 rounded-2xl p-8 text-center cursor-pointer transition-colors bg-slate-50/60 dark:bg-slate-800/40"
                  >
                    <input
                      id="datasetInput"
                      type="file"
                      accept=".csv, .xlsx, .xls"
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setFile(e.target.files[0]);
                        }
                      }}
                    />
                    <div className="w-12 h-12 mx-auto rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 flex items-center justify-center mb-3">
                      <Upload className="w-6 h-6" />
                    </div>
                    {file ? (
                      <div>
                        <p className="text-sm font-bold text-slate-900 dark:text-white">
                          {file.name}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {(file.size / 1024).toFixed(1)} KB • Click to choose a different file
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                          Click to upload or drag & drop CSV or Excel
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          Supports multiple Excel worksheets, numeric metrics, and date columns
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Quick Sample Dataset Buttons */}
                <div className="pt-2 border-t border-slate-100 dark:border-slate-800">
                  <span className="text-xs text-slate-400 font-medium block mb-2">
                    Or quickly start with pre-generated benchmark data:
                  </span>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => handleLoadSample('csv')}
                      disabled={isLoading}
                      className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 text-xs font-semibold border border-slate-200 dark:border-slate-700 transition-colors flex items-center space-x-1.5"
                    >
                      <FileSpreadsheet className="w-3.5 h-3.5 text-brand-600" />
                      <span>Load Superstore Sales (.CSV)</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleLoadSample('xlsx')}
                      disabled={isLoading}
                      className="px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950 text-slate-700 dark:text-slate-300 hover:text-brand-600 text-xs font-semibold border border-slate-200 dark:border-slate-700 transition-colors flex items-center space-x-1.5"
                    >
                      <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Load Multi-Sheet Retail (.XLSX)</span>
                    </button>
                  </div>
                </div>

                {/* Submit Button */}
                <button
                  type="button"
                  onClick={handleCreateNew}
                  disabled={isLoading || !file}
                  className="w-full py-3 px-6 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm shadow-md shadow-brand-600/30 transition-all flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <span>Initializing Workspace...</span>
                  ) : (
                    <>
                      <span>Open Dashboard Workspace</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            )}

            {/* TAB 2: RESTORE ZIP */}
            {activeTab === 'restore' && (
              <div className="space-y-6">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                    Upload Project Archive (.ZIP)
                  </label>
                  <div
                    onClick={() => document.getElementById('zipInput')?.click()}
                    className="border-2 border-dashed border-slate-300 dark:border-slate-700 hover:border-brand-500 dark:hover:border-brand-500 rounded-2xl p-8 text-center cursor-pointer transition-colors bg-slate-50/60 dark:bg-slate-800/40"
                  >
                    <input
                      id="zipInput"
                      type="file"
                      accept=".zip"
                      className="hidden"
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setZipFile(e.target.files[0]);
                        }
                      }}
                    />
                    <div className="w-12 h-12 mx-auto rounded-xl bg-brand-50 dark:bg-brand-950/60 text-brand-600 flex items-center justify-center mb-3">
                      <FileArchive className="w-6 h-6" />
                    </div>
                    {zipFile ? (
                      <div>
                        <p className="text-sm font-bold text-slate-900 dark:text-white">
                          {zipFile.name}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">
                          {(zipFile.size / 1024).toFixed(1)} KB • Ready to restore
                        </p>
                      </div>
                    ) : (
                      <div>
                        <p className="text-sm font-bold text-slate-800 dark:text-slate-200">
                          Click to upload previously exported project ZIP
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                          Extracts dataset, restores all charts, KPIs, filters, and conversation history
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl text-xs text-slate-600 dark:text-slate-400 leading-relaxed border border-slate-200 dark:border-slate-700">
                  <div className="font-bold text-slate-800 dark:text-slate-200 mb-1 flex items-center">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 mr-1.5" /> Zero Re-upload Required
                  </div>
                  When restoring a project ZIP, your original dataset and all generated visualizations are completely restored automatically.
                </div>

                <button
                  type="button"
                  onClick={handleRestoreZip}
                  disabled={isLoading || !zipFile}
                  className="w-full py-3 px-6 rounded-xl bg-brand-600 hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-sm shadow-md shadow-brand-600/30 transition-all flex items-center justify-center space-x-2"
                >
                  {isLoading ? (
                    <span>Restoring Dashboard...</span>
                  ) : (
                    <>
                      <span>Restore Dashboard & Resume</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </div>
            )}

          </div>
        </div>

      </div>

      {/* Footer */}
      <footer className="mt-12 text-center text-xs text-slate-400 dark:text-slate-600">
        B.Tech Computer Science Engineering Final Year Major Project • Multilingual Conversational Dashboard System
      </footer>
    </div>
  );
};

