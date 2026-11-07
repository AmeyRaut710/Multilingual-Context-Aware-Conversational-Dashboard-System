import { DashboardState, CommandResponse, DatasetMeta, DataTableParams, DataTableResponse } from '../types/dashboard';

const API_BASE = '/api';

export const api = {
  async createProject(projectName: string = "Untitled Project"): Promise<{ session_id: string; state: DashboardState }> {
    const res = await fetch(`${API_BASE}/project/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ project_name: projectName }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async uploadProjectZip(file: File): Promise<{ session_id: string; message: string; state: DashboardState }> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/project/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async uploadDataset(sessionId: string, file: File): Promise<{ metadata: DatasetMeta; state: DashboardState; message: string }> {
    const formData = new FormData();
    formData.append('session_id', sessionId);
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/dataset/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async switchSheet(sessionId: string, sheetName: string): Promise<{ metadata: DatasetMeta; state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dataset/sheet`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, sheet_name: sheetName }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async processCommand(sessionId: string, command: string): Promise<CommandResponse> {
    const res = await fetch(`${API_BASE}/command/process`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, command }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async transcribeAudio(audioBlob: Blob): Promise<{ success: boolean; text: string; details: any }> {
    const formData = new FormData();
    formData.append('file', audioBlob, 'recording.wav');
    const res = await fetch(`${API_BASE}/command/transcribe`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async applyFilter(sessionId: string, column: string, value: any): Promise<{ state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dashboard/filter`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, column, value }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async clearFilter(sessionId: string, column?: string): Promise<{ state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dashboard/filter/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, column }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async removeSlicer(sessionId: string, column: string): Promise<{ state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dashboard/filter/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, column }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async deleteChart(sessionId: string, chartId: string): Promise<{ state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dashboard/chart/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, chart_id: chartId }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async updateChart(sessionId: string, chartId: string, updates: { chart_type?: string; title?: string; agg?: string; top_n?: number }): Promise<{ state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dashboard/chart/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, chart_id: chartId, ...updates }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async deleteKPI(sessionId: string, kpiId: string): Promise<{ state: DashboardState }> {
    const res = await fetch(`${API_BASE}/dashboard/kpi/delete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, kpi_id: kpiId }),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async fetchCompleteDataTable(params: DataTableParams): Promise<DataTableResponse> {
    const res = await fetch(`${API_BASE}/dataset/table`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  async clearWorkspace(sessionId: string): Promise<void> {
    await fetch(`${API_BASE}/session/clear?session_id=${encodeURIComponent(sessionId)}`, {
      method: 'DELETE',
    });
  },

  getZipExportUrl(sessionId: string): string {
    return `${API_BASE}/project/export/zip?session_id=${encodeURIComponent(sessionId)}`;
  },

  getHtmlExportUrl(sessionId: string): string {
    return `${API_BASE}/project/export/html?session_id=${encodeURIComponent(sessionId)}`;
  },

  getPdfExportUrl(sessionId: string): string {
    return `${API_BASE}/project/export/pdf?session_id=${encodeURIComponent(sessionId)}`;
  }
};

