import React, { useState } from 'react';
import { DashboardState, CommandResponse } from '../types/dashboard';
import { Navbar } from '../components/Navbar';
import { KPISection } from '../components/KPISection';
import { FilterBar } from '../components/FilterBar';
import { ChartGrid } from '../components/ChartGrid';
import { ChatAssistant } from '../components/ChatAssistant';
import { DatasetInfoModal } from '../components/DatasetInfoModal';
import { ExportModal } from '../components/ExportModal';
import { CompleteDataTableModal } from '../components/CompleteDataTableModal';
import { api } from '../services/api';
import { Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

interface DashboardWorkspaceProps {
  initialState: DashboardState;
  darkMode: boolean;
  onToggleTheme: () => void;
  onBackToWelcome: () => void;
}

export const DashboardWorkspace: React.FC<DashboardWorkspaceProps> = ({
  initialState,
  darkMode,
  onToggleTheme,
  onBackToWelcome,
}) => {
  const [state, setState] = useState<DashboardState>(initialState);
  const [isLoadingCommand, setIsLoadingCommand] = useState(false);
  const [isDatasetInfoOpen, setIsDatasetInfoOpen] = useState(false);
  const [isCompleteTableOpen, setIsCompleteTableOpen] = useState(false);
  const [isExportOpen, setIsExportOpen] = useState(false);
  const [toastMessage, setToastMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

  const showToast = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
    setToastMessage({ text, type });
    setTimeout(() => {
      setToastMessage(null);
    }, 4500);
  };

  // 1. Process Natural Language Command
  const handleSendCommand = async (command: string) => {
    setIsLoadingCommand(true);
    try {
      const res: CommandResponse = await api.processCommand(state.session_id, command);
      
      if (res.updated_state) {
        setState(res.updated_state);
      }

      if (res.success) {
        showToast(
          `[${res.detected_language}] ${res.message}`,
          res.requires_clarification ? 'info' : 'success'
        );
      } else {
        showToast(res.message || 'Operation failed', 'error');
      }
      return res;
    } catch (err: any) {
      showToast(err.message || 'Error processing command', 'error');
    } finally {
      setIsLoadingCommand(false);
    }
  };

  // 2. Resolve Clarification Option Click
  const handleResolveClarification = async (answer: string) => {
    await handleSendCommand(answer);
  };

  // 3. Filter changes
  const handleApplyFilter = async (column: string, value: any) => {
    try {
      const res = await api.applyFilter(state.session_id, column, value);
      setState(res.state);
      showToast(`Filter applied on ${column}`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to apply filter', 'error');
    }
  };

  const handleClearFilter = async (column?: string) => {
    try {
      const res = await api.clearFilter(state.session_id, column);
      setState(res.state);
      showToast('Filters reset', 'info');
    } catch (err: any) {
      showToast(err.message || 'Failed to reset filters', 'error');
    }
  };

  const handleRemoveSlicer = async (column: string) => {
    try {
      const res = await api.removeSlicer(state.session_id, column);
      setState(res.state);
      showToast(`Removed ${column} slicer`, 'info');
    } catch (err: any) {
      showToast(err.message || 'Failed to remove slicer', 'error');
    }
  };

  // 4. Chart Management
  const handleSelectChart = (chartId: string) => {
    setState((prev) => ({
      ...prev,
      selected_chart_id: chartId === prev.selected_chart_id ? undefined : chartId,
    }));
  };

  const handleDeleteChart = async (chartId: string) => {
    try {
      const res = await api.deleteChart(state.session_id, chartId);
      setState(res.state);
      showToast('Chart deleted', 'info');
    } catch (err: any) {
      showToast(err.message || 'Failed to delete chart', 'error');
    }
  };

  const handleUpdateChartType = async (chartId: string, newType: string) => {
    try {
      const res = await api.updateChart(state.session_id, chartId, { chart_type: newType });
      setState(res.state);
      showToast(`Chart updated to ${newType}`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to update chart', 'error');
    }
  };

  const handleToggleWidth = (chartId: string) => {
    setState((prev) => ({
      ...prev,
      charts: prev.charts.map((c) =>
        c.id === chartId ? { ...c, width: c.width === 'full' ? 'half' : 'full' } : c
      ),
    }));
  };

  // 5. KPI Management
  const handleDeleteKPI = async (kpiId: string) => {
    try {
      const res = await api.deleteKPI(state.session_id, kpiId);
      setState(res.state);
      showToast('KPI removed', 'info');
    } catch (err: any) {
      showToast(err.message || 'Failed to delete KPI', 'error');
    }
  };

  const handleQuickKPI = async (metric: string, agg: string) => {
    await handleSendCommand(`Calculate ${agg} of ${metric}`);
  };

  // 6. Worksheet Switch
  const handleSwitchSheet = async (sheetName: string) => {
    try {
      const res = await api.switchSheet(state.session_id, sheetName);
      setState(res.state);
      showToast(`Switched to sheet ${sheetName}`, 'success');
    } catch (err: any) {
      showToast(err.message || 'Failed to switch sheet', 'error');
    }
  };

  // 7. Clear Workspace
  const handleClearWorkspace = async () => {
    if (window.confirm('Are you sure you want to clear this workspace? All temporary charts, KPIs, and uploaded data will be deleted.')) {
      try {
        await api.clearWorkspace(state.session_id);
        onBackToWelcome();
      } catch (err: any) {
        showToast(err.message || 'Failed to clear session', 'error');
      }
    }
  };

  const numericCols = state.dataset_meta?.columns
    .filter((c) => c.dtype === 'numeric')
    .map((c) => c.name) || [];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex flex-col transition-colors pb-24">
      {/* Top Navbar */}
      <Navbar
        state={state}
        darkMode={darkMode}
        onToggleTheme={onToggleTheme}
        onOpenDatasetInfo={() => setIsDatasetInfoOpen(true)}
        onOpenCompleteTable={() => setIsCompleteTableOpen(true)}
        onOpenExport={() => setIsExportOpen(true)}
        onClearWorkspace={handleClearWorkspace}
        onSwitchSheet={handleSwitchSheet}
      />

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full space-y-6 flex-1">
        
        {/* Toast Notification Banner */}
        {toastMessage && (
          <div
            className={`p-3.5 rounded-xl border text-xs font-medium flex items-center justify-between shadow-sm animate-fadeIn ${
              toastMessage.type === 'error'
                ? 'bg-rose-50 dark:bg-rose-950/60 border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300'
                : toastMessage.type === 'success'
                ? 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-900 text-emerald-700 dark:text-emerald-300'
                : 'bg-brand-50 dark:bg-brand-950/60 border-brand-200 dark:border-brand-900 text-brand-700 dark:text-brand-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              {toastMessage.type === 'error' ? (
                <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              ) : (
                <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
              )}
              <span>{toastMessage.text}</span>
            </div>
            <button
              onClick={() => setToastMessage(null)}
              className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 ml-4 font-bold"
            >
              ✕
            </button>
          </div>
        )}

        {/* Filter Bar */}
        <FilterBar
          filters={state.filters}
          availableColumns={state.dataset_meta?.columns || []}
          onApplyFilter={handleApplyFilter}
          onClearFilter={handleClearFilter}
          onRemoveSlicer={handleRemoveSlicer}
        />

        {/* Dynamic KPI Cards Section */}
        <KPISection
          kpis={state.kpis}
          onDeleteKPI={handleDeleteKPI}
          onQuickKPI={handleQuickKPI}
          availableMetrics={numericCols}
        />

        {/* Charts Grid */}
        <ChartGrid
          charts={state.charts}
          selectedChartId={state.selected_chart_id}
          darkMode={darkMode}
          onSelectChart={handleSelectChart}
          onDeleteChart={handleDeleteChart}
          onUpdateChartType={handleUpdateChartType}
          onToggleWidth={handleToggleWidth}
          onSuggestedCommand={handleSendCommand}
        />

      </main>

      {/* Floating Multilingual AI Chat Assistant */}
      <ChatAssistant
        onSendCommand={handleSendCommand}
        isLoading={isLoadingCommand}
        history={state.command_history}
        onResolveClarification={handleResolveClarification}
      />

      {/* Dataset Schema & Preview Modal */}
      <DatasetInfoModal
        isOpen={isDatasetInfoOpen}
        onClose={() => setIsDatasetInfoOpen(false)}
        metadata={state.dataset_meta}
        onSwitchSheet={handleSwitchSheet}
        onOpenCompleteTable={() => setIsCompleteTableOpen(true)}
      />

      {/* Complete Dataset Full-Screen Table Modal */}
      <CompleteDataTableModal
        isOpen={isCompleteTableOpen}
        onClose={() => setIsCompleteTableOpen(false)}
        sessionId={state.session_id}
        filename={state.dataset_meta?.filename}
        activeSheet={state.dataset_meta?.active_sheet}
      />

      {/* Export Options Modal */}
      <ExportModal
        isOpen={isExportOpen}
        onClose={() => setIsExportOpen(false)}
        sessionId={state.session_id}
        projectName={state.project_name}
      />
    </div>
  );
};

