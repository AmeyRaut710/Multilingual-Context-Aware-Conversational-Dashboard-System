import React, { useEffect, useRef } from 'react';
import { ChartConfig } from '../types/dashboard';
import { 
  BarChart3, LineChart, PieChart, ScatterChart, 
  Trash2, Maximize2, Minimize2, ChevronDown 
} from 'lucide-react';

interface ChartCardProps {
  chart: ChartConfig;
  isSelected: boolean;
  darkMode: boolean;
  onSelect: (chartId: string) => void;
  onDelete: (chartId: string) => void;
  onUpdateType: (chartId: string, newType: string) => void;
  onToggleWidth: (chartId: string) => void;
}

declare global {
  interface Window {
    Plotly: any;
  }
}

export const ChartCard: React.FC<ChartCardProps> = ({
  chart,
  isSelected,
  darkMode,
  onSelect,
  onDelete,
  onUpdateType,
  onToggleWidth,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !window.Plotly) return;

    const spec = chart.plotly_spec || {};
    const data = spec.data || [];
    const layout = {
      ...(spec.layout || {}),
      autosize: true,
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: {
        family: 'Inter, system-ui, sans-serif',
        color: darkMode ? '#cbd5e1' : '#1e293b',
      },
      xaxis: {
        ...(spec.layout?.xaxis || {}),
        gridcolor: darkMode ? '#1e293b' : '#f1f5f9',
        zerolinecolor: darkMode ? '#334155' : '#e2e8f0',
        tickfont: { color: darkMode ? '#94a3b8' : '#64748b' },
      },
      yaxis: {
        ...(spec.layout?.yaxis || {}),
        gridcolor: darkMode ? '#1e293b' : '#f1f5f9',
        zerolinecolor: darkMode ? '#334155' : '#e2e8f0',
        tickfont: { color: darkMode ? '#94a3b8' : '#64748b' },
      },
      margin: { l: 45, r: 25, t: 30, b: 45 },
    };

    const config = {
      responsive: true,
      displayModeBar: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
    };

    window.Plotly.react(containerRef.current, data, layout, config);

    const handleResize = () => {
      if (containerRef.current && window.Plotly) {
        window.Plotly.Plots.resize(containerRef.current);
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, [chart, darkMode]);

  const chartTypes = [
    { value: 'bar', label: 'Bar' },
    { value: 'horizontal_bar', label: 'Horizontal Bar' },
    { value: 'line', label: 'Line' },
    { value: 'pie', label: 'Pie' },
    { value: 'donut', label: 'Donut' },
    { value: 'scatter', label: 'Scatter' },
    { value: 'area', label: 'Area' },
    { value: 'histogram', label: 'Histogram' },
    { value: 'box', label: 'Box Plot' },
  ];

  return (
    <div
      onClick={() => onSelect(chart.id)}
      className={`relative bg-white dark:bg-slate-900 border rounded-xl p-4 shadow-sm hover:shadow-md transition-all flex flex-col cursor-pointer ${
        isSelected
          ? 'border-brand-500 ring-2 ring-brand-500/20 dark:ring-brand-500/30'
          : 'border-slate-200 dark:border-slate-800'
      } ${chart.width === 'full' ? 'col-span-1 lg:col-span-2' : 'col-span-1'}`}
    >
      {/* Header & Controls */}
      <div className="flex items-start justify-between gap-2 mb-2 pb-2 border-b border-slate-100 dark:border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-tight">
              {chart.title}
            </h4>
            {isSelected && (
              <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-brand-100 dark:bg-brand-950 text-brand-700 dark:text-brand-300">
                Selected
              </span>
            )}
          </div>
          <div className="flex items-center space-x-2 mt-1 text-xs text-slate-400 dark:text-slate-500">
            {chart.x_col && <span>X: {chart.x_col}</span>}
            {chart.x_col && chart.y_col && <span>•</span>}
            {chart.y_col && <span>Y: {chart.y_col} ({chart.agg || 'sum'})</span>}
            {chart.top_n && <span>• Top {chart.top_n}</span>}
          </div>
        </div>

        {/* Toolbar */}
        <div className="flex items-center space-x-1" onClick={(e) => e.stopPropagation()}>
          {/* Chart Type Dropdown */}
          <div className="relative inline-block">
            <select
              value={chart.chart_type}
              onChange={(e) => onUpdateType(chart.id, e.target.value)}
              className="text-xs bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 rounded-lg px-2 py-1 pr-6 focus:outline-none appearance-none cursor-pointer"
            >
              {chartTypes.map((t) => (
                <option key={t.value} value={t.value} className="dark:bg-slate-900">
                  {t.label}
                </option>
              ))}
            </select>
            <ChevronDown className="w-3 h-3 text-slate-400 absolute right-1.5 top-2 pointer-events-none" />
          </div>

          {/* Width Toggle */}
          <button
            onClick={() => onToggleWidth(chart.id)}
            className="p-1.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title={chart.width === 'full' ? 'Collapse to half width' : 'Expand to full width'}
          >
            {chart.width === 'full' ? <Minimize2 className="w-3.5 h-3.5" /> : <Maximize2 className="w-3.5 h-3.5" />}
          </button>

          {/* Delete Button */}
          <button
            onClick={() => onDelete(chart.id)}
            className="p-1.5 text-slate-400 hover:text-rose-500 rounded-lg hover:bg-rose-50 dark:hover:bg-rose-950/30 transition-colors"
            title="Delete visualization"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Plotly Chart Container */}
      <div
        ref={containerRef}
        className="w-full flex-1 min-h-[340px]"
        style={{ minHeight: '340px' }}
      />
    </div>
  );
};
