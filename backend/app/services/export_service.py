import io
import json
import os
import zipfile
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
import pandas as pd
import numpy as np
from app.services.session_service import SessionData
from app.services.dataset_service import dataset_service
from app.models.schemas import ChartConfig, KPIConfig, FilterItem

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)

class ExportService:
    @classmethod
    def generate_zip_export(cls, session: SessionData) -> bytes:
        """
        Creates downloadable ZIP containing:
        - dataset/original_dataset.(csv|xlsx)
        - dashboard_config.json
        - metadata.json
        """
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # 1. Dataset file
            ds_name = session.original_filename or f"original_dataset.{session.file_type or 'csv'}"
            if session.original_file_bytes:
                zf.writestr(f"dataset/{ds_name}", session.original_file_bytes)
            elif session.df_original is not None:
                csv_bytes = session.df_original.to_csv(index=False).encode("utf-8")
                zf.writestr(f"dataset/{ds_name}", csv_bytes)

            # 2. Metadata JSON
            meta = {
                "project_name": session.project_name,
                "project_version": "1.0.0",
                "dataset_filename": ds_name,
                "dataset_format": session.file_type or "csv",
                "worksheet_information": list(session.excel_sheets.keys()) if session.excel_sheets else [],
                "active_sheet": session.active_sheet,
                "export_timestamp": datetime.utcnow().isoformat()
            }
            zf.writestr("metadata.json", json.dumps(meta, indent=2))

            # 3. Dashboard Config JSON
            cfg = {
                "charts": [c.model_dump() for c in session.charts],
                "kpis": [k.model_dump() for k in session.kpis],
                "filters": [f.model_dump() for f in session.filters],
                "active_filters": session.active_filters,
                "selected_chart_id": session.selected_chart_id,
                "last_modified_chart_id": session.last_modified_chart_id,
                "command_history": session.command_history
            }
            zf.writestr("dashboard_config.json", json.dumps(cfg, indent=2))

        buf.seek(0)
        return buf.getvalue()

    @classmethod
    def restore_from_zip(cls, zip_bytes: bytes, session: SessionData) -> Tuple[bool, str]:
        """
        Validates and restores a dashboard project from a ZIP file.
        Includes security checks against zip slip and corrupted files.
        """
        if len(zip_bytes) > 50 * 1024 * 1024:
            return False, "ZIP file exceeds maximum allowed size (50MB)."

        try:
            buf = io.BytesIO(zip_bytes)
            with zipfile.ZipFile(buf, "r") as zf:
                file_list = zf.namelist()

                # Security validation: reject path traversal
                for name in file_list:
                    if ".." in name or name.startswith("/") or name.startswith("\\"):
                        return False, f"Invalid or unsafe path in ZIP archive: '{name}'"

                # Check required files
                if "metadata.json" not in file_list:
                    return False, "Invalid project ZIP: missing 'metadata.json'."
                if "dashboard_config.json" not in file_list:
                    return False, "Invalid project ZIP: missing 'dashboard_config.json'."

                dataset_files = [f for f in file_list if f.startswith("dataset/") and not f.endswith("/")]
                if not dataset_files:
                    return False, "Invalid project ZIP: missing dataset file in 'dataset/' directory."

                # Read metadata
                meta_data = json.loads(zf.read("metadata.json").decode("utf-8"))
                session.project_name = meta_data.get("project_name", "Restored Project")

                # Read and process dataset
                target_ds_file = dataset_files[0]
                ds_bytes = zf.read(target_ds_file)
                ds_filename = os.path.basename(target_ds_file)

                dataset_service.process_file_bytes(ds_bytes, ds_filename, session)

                # Switch worksheet if applicable
                target_sheet = meta_data.get("active_sheet")
                if target_sheet and session.excel_sheets and target_sheet in session.excel_sheets:
                    dataset_service.switch_sheet(session, target_sheet)

                # Read dashboard config
                cfg_data = json.loads(zf.read("dashboard_config.json").decode("utf-8"))

                # Reconstruct charts
                session.charts = []
                for c_dict in cfg_data.get("charts", []):
                    session.charts.append(ChartConfig(**c_dict))

                # Reconstruct KPIs
                session.kpis = []
                for k_dict in cfg_data.get("kpis", []):
                    session.kpis.append(KPIConfig(**k_dict))

                # Reconstruct Filters
                session.filters = []
                for f_dict in cfg_data.get("filters", []):
                    session.filters.append(FilterItem(**f_dict))

                session.active_filters = cfg_data.get("active_filters", {})
                session.selected_chart_id = cfg_data.get("selected_chart_id")
                session.last_modified_chart_id = cfg_data.get("last_modified_chart_id")
                session.command_history = cfg_data.get("command_history", [])

                # Recompute specs to ensure all specs match restored data
                from app.services.dashboard_service import dashboard_service
                dashboard_service.recompute_all(session)

                return True, f"Project '{session.project_name}' successfully restored with {len(session.charts)} charts and {len(session.kpis)} KPIs."

        except zipfile.BadZipFile:
            return False, "The uploaded file is not a valid ZIP file."
        except Exception as e:
            return False, f"Failed to restore project from ZIP: {str(e)}"

    @classmethod
    def generate_standalone_html(cls, session: SessionData) -> str:
        """
        Generates a 100% self-contained standalone interactive HTML dashboard.
        Includes client-side filter engine that updates Plotly charts and KPIs offline in browser!
        """
        project_name = session.project_name
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

        # Serialized dataset for client-side filtering
        df = session.df_original if session.df_original is not None else pd.DataFrame()
        # Clean nulls
        clean_df = df.replace({np.nan: None})
        records_json = clean_df.to_json(orient="records")

        # Serialized charts and KPIs
        charts_data = [c.model_dump() for c in session.charts]
        kpis_data = [k.model_dump() for k in session.kpis]
        filters_data = [f.model_dump() for f in session.filters]

        # Check if local plotly.min.js exists to inline
        plotly_js_content = ""
        local_plotly_path = os.path.join(os.path.dirname(__file__), "..", "static", "plotly.min.js")
        if os.path.exists(local_plotly_path):
            try:
                with open(local_plotly_path, "r", encoding="utf-8") as f:
                    plotly_js_content = f.read()
            except Exception:
                pass

        plotly_script_tag = f"<script>{plotly_js_content}</script>" if plotly_js_content else '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'

        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{project_name} - Interactive Dashboard</title>
  {plotly_script_tag}
  <style>
    :root {{
      --primary: #4f46e5;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --border: #e2e8f0;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding: 24px;
    }}
    header {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px 24px;
      margin-bottom: 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    h1 {{ font-size: 22px; font-weight: 700; color: var(--text); }}
    .badge {{
      display: inline-block;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 600;
      color: var(--primary);
      background: #eef2ff;
      border-radius: 9999px;
      margin-left: 8px;
    }}
    .subtitle {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; }}
    
    /* Filters */
    .filter-section {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
    }}
    .filter-item {{ display: flex; flex-direction: column; gap: 4px; }}
    .filter-item label {{ font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.03em; }}
    .filter-item select {{
      padding: 8px 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #fff;
      font-size: 14px;
      color: var(--text);
      min-width: 180px;
      outline: none;
    }}
    .reset-btn {{
      padding: 8px 16px;
      background: #f1f5f9;
      color: #334155;
      border: 1px solid var(--border);
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
      cursor: pointer;
      margin-top: auto;
      transition: all 0.2s;
    }}
    .reset-btn:hover {{ background: #e2e8f0; }}

    /* KPI Cards */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}
    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      border-left: 4px solid var(--primary);
    }}
    .kpi-title {{ font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }}
    .kpi-value {{ font-size: 28px; font-weight: 700; color: var(--text); margin-top: 8px; }}

    /* Chart Grid */
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(480px, 1fr));
      gap: 24px;
    }}
    .chart-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
      min-height: 420px;
    }}
    .chart-container {{ width: 100%; height: 380px; }}
  </style>
</head>
<body>
  <header>
    <div>
      <h1>{project_name} <span class="badge">Offline Interactive</span></h1>
      <div class="subtitle">Generated {timestamp} • {len(df)} total rows</div>
    </div>
  </header>

  <div class="filter-section" id="filterBar">
    <div style="font-weight:600; font-size: 14px; margin-right: 8px;">Filters:</div>
    <!-- Populated by JavaScript -->
    <button class="reset-btn" onclick="resetAllFilters()">Reset All Filters</button>
  </div>

  <div class="kpi-grid" id="kpiContainer">
    <!-- Populated by JavaScript -->
  </div>

  <div class="chart-grid" id="chartContainer">
    <!-- Populated by JavaScript -->
  </div>

  <script>
    // Embedded Data and Configs
    const rawData = {records_json};
    const chartConfigs = {json.dumps(charts_data)};
    const kpiConfigs = {json.dumps(kpis_data)};
    const initialFilters = {json.dumps(filters_data)};

    let activeFilterValues = {{}};

    // Setup Filter Bar
    function initFilters() {{
      const bar = document.getElementById("filterBar");
      const resetBtn = bar.querySelector(".reset-btn");

      // Extract unique categorical columns from charts
      const filterCols = new Set();
      chartConfigs.forEach(c => {{
        if (c.x_col && typeof rawData[0]?.[c.x_col] === "string") {{
          filterCols.add(c.x_col);
        }}
      }});
      initialFilters.forEach(f => filterCols.add(f.column));

      filterCols.forEach(col => {{
        const vals = [...new Set(rawData.map(r => r[col]).filter(Boolean))].sort();
        if (vals.length > 1 && vals.length <= 40) {{
          const item = document.createElement("div");
          item.className = "filter-item";
          item.innerHTML = `
            <label>${{col}}</label>
            <select id="filter_${{col}}" onchange="onFilterChange('${{col}}', this.value)">
              <option value="">All</option>
              ${{vals.map(v => `<option value="${{v}}">${{v}}</option>`).join("")}}
            </select>
          `;
          bar.insertBefore(item, resetBtn);
        }}
      }});
    }}

    function onFilterChange(col, val) {{
      if (!val) {{
        delete activeFilterValues[col];
      }} else {{
        activeFilterValues[col] = val;
      }}
      applyFiltering();
    }}

    function resetAllFilters() {{
      activeFilterValues = {{}};
      document.querySelectorAll(".filter-item select").forEach(sel => sel.value = "");
      applyFiltering();
    }}

    function getFilteredData() {{
      return rawData.filter(row => {{
        for (const [col, val] of Object.entries(activeFilterValues)) {{
          if (String(row[col]) !== String(val)) return false;
        }}
        return true;
      }});
    }}

    function renderKPIs(filtered) {{
      const container = document.getElementById("kpiContainer");
      container.innerHTML = "";
      
      kpiConfigs.forEach(kpi => {{
        const col = kpi.metric_col;
        const vals = filtered.map(r => Number(r[col])).filter(n => !isNaN(n));
        let result = 0;
        
        if (vals.length > 0) {{
          if (kpi.agg === "sum") result = vals.reduce((a, b) => a + b, 0);
          else if (kpi.agg === "avg") result = vals.reduce((a, b) => a + b, 0) / vals.length;
          else if (kpi.agg === "min") result = Math.min(...vals);
          else if (kpi.agg === "max") result = Math.max(...vals);
          else result = vals.length;
        }}

        let formatted = result >= 1e6 ? (result/1e6).toFixed(2) + "M" : (result >= 1e3 ? (result/1e3).toFixed(2) + "K" : result.toLocaleString(undefined, {{maximumFractionDigits: 2}}));

        const card = document.createElement("div");
        card.className = "kpi-card";
        card.innerHTML = `
          <div class="kpi-title">${{kpi.title}}</div>
          <div class="kpi-value">${{kpi.prefix || ""}}${{formatted}}</div>
        `;
        container.appendChild(card);
      }});
    }}

    function renderCharts(filtered) {{
      chartConfigs.forEach(cfg => {{
        const divId = "chart_" + cfg.id;
        let card = document.getElementById("card_" + cfg.id);
        if (!card) {{
          card = document.createElement("div");
          card.id = "card_" + cfg.id;
          card.className = "chart-card";
          card.innerHTML = `<div id="${{divId}}" class="chart-container"></div>`;
          document.getElementById("chartContainer").appendChild(card);
        }}

        // Dynamic trace recalculation
        const x_col = cfg.x_col;
        const y_col = cfg.y_col;
        const agg = cfg.agg || "sum";

        if (x_col && y_col) {{
          // Group by x_col
          const map = {{}};
          filtered.forEach(r => {{
            const k = r[x_col] || "Unknown";
            const v = Number(r[y_col]) || 0;
            if (!map[k]) map[k] = [];
            map[k].push(v);
          }});

          let xVals = Object.keys(map);
          let yVals = xVals.map(k => {{
            const arr = map[k];
            if (agg === "sum") return arr.reduce((a, b) => a + b, 0);
            if (agg === "avg") return arr.reduce((a, b) => a + b, 0) / arr.length;
            if (agg === "min") return Math.min(...arr);
            if (agg === "max") return Math.max(...arr);
            return arr.length;
          }});

          if (cfg.top_n) {{
            const paired = xVals.map((x, i) => ({{ x, y: yVals[i] }}));
            paired.sort((a, b) => b.y - a.y);
            const sliced = paired.slice(0, cfg.top_n);
            xVals = sliced.map(p => p.x);
            yVals = sliced.map(p => p.y);
          }}

          const spec = cfg.plotly_spec || {{}};
          const layout = spec.layout || {{}};
          layout.autosize = true;

          let traceType = cfg.chart_type === "horizontal_bar" ? "bar" : (cfg.chart_type === "area" ? "scatter" : cfg.chart_type);
          let newTrace = {{
            type: traceType,
            x: cfg.chart_type === "horizontal_bar" ? yVals : xVals,
            y: cfg.chart_type === "horizontal_bar" ? xVals : yVals,
            orientation: cfg.chart_type === "horizontal_bar" ? "h" : "v",
            marker: {{ color: "#4f46e5" }}
          }};
          if (cfg.chart_type === "pie" || cfg.chart_type === "donut") {{
            newTrace = {{
              type: "pie",
              labels: xVals,
              values: yVals,
              hole: cfg.chart_type === "donut" ? 0.5 : 0
            }};
          }}
          if (cfg.chart_type === "area") {{
            newTrace.fill = "tozeroy";
          }}

          Plotly.react(divId, [newTrace], layout, {{ responsive: true, displayModeBar: false }});
        }} else {{
          // Direct fallback from spec
          if (cfg.plotly_spec && cfg.plotly_spec.data) {{
            Plotly.react(divId, cfg.plotly_spec.data, cfg.plotly_spec.layout, {{ responsive: true, displayModeBar: false }});
          }}
        }}
      }});
    }}

    function applyFiltering() {{
      const filtered = getFilteredData();
      renderKPIs(filtered);
      renderCharts(filtered);
    }}

    // Initial Load
    window.addEventListener("DOMContentLoaded", () => {{
      initFilters();
      applyFiltering();
    }});
  </script>
</body>
</html>"""
        return html_template

    @classmethod
    def generate_pdf_report(cls, session: SessionData) -> bytes:
        """
        Generates a professional static PDF report of the dashboard using ReportLab.
        """
        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b")
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#64748b")
        )
        h2_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#4f46e5"),
            spaceBefore=14,
            spaceAfter=6
        )
        cell_style = ParagraphStyle(
            "CellText",
            parent=styles["Normal"],
            fontSize=9,
            leading=11
        )
        cell_header_style = ParagraphStyle(
            "CellHeaderText",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            textColor=colors.white,
            fontName="Helvetica-Bold"
        )

        story = []

        # Title & Header
        story.append(Paragraph(f"Dashboard Report: {session.project_name}", title_style))
        export_time = datetime.utcnow().strftime("%B %d, %Y - %H:%M UTC")
        story.append(Paragraph(f"Generated on {export_time} | Multilingual Conversational Analytics System", subtitle_style))
        story.append(Spacer(1, 14))

        # 1. Dataset Overview
        story.append(Paragraph("1. Dataset Overview", h2_style))
        total_rows = session.dataset_meta.total_rows if session.dataset_meta else (len(session.df_original) if session.df_original is not None else 0)
        total_cols = session.dataset_meta.total_columns if session.dataset_meta else (len(session.df_original.columns) if session.df_original is not None else 0)
        filename = session.original_filename or "N/A"
        active_sheet = session.active_sheet or "Default"
        dups = session.dataset_meta.duplicate_count if session.dataset_meta else 0

        ds_summary_data = [
            [Paragraph("Dataset File", cell_header_style), Paragraph("Total Records", cell_header_style), Paragraph("Total Columns", cell_header_style), Paragraph("Active Worksheet", cell_header_style), Paragraph("Duplicate Rows", cell_header_style)],
            [Paragraph(str(filename), cell_style), Paragraph(f"{total_rows:,}", cell_style), Paragraph(str(total_cols), cell_style), Paragraph(str(active_sheet), cell_style), Paragraph(str(dups), cell_style)]
        ]
        t_ds = Table(ds_summary_data, colWidths=[150, 80, 80, 110, 80])
        t_ds.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor("#f8fafc"))
        ]))
        story.append(t_ds)
        story.append(Spacer(1, 14))

        # 2. Key Performance Indicators (KPIs)
        if session.kpis:
            story.append(Paragraph("2. Key Performance Indicators (KPIs)", h2_style))
            kpi_table_data = [
                [Paragraph("KPI Title", cell_header_style), Paragraph("Metric Column", cell_header_style), Paragraph("Aggregation", cell_header_style), Paragraph("Calculated Value", cell_header_style)]
            ]
            for kpi in session.kpis:
                kpi_table_data.append([
                    Paragraph(kpi.title, cell_style),
                    Paragraph(kpi.metric_col, cell_style),
                    Paragraph(kpi.agg.upper(), cell_style),
                    Paragraph(f"<b>{kpi.prefix}{kpi.formatted_value}</b>", cell_style)
                ])
            t_kpi = Table(kpi_table_data, colWidths=[180, 120, 90, 110])
            t_kpi.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#06b6d4")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
            ]))
            story.append(t_kpi)
            story.append(Spacer(1, 14))

        # 3. Visualizations Summary
        if session.charts:
            story.append(Paragraph("3. Visualizations Summary", h2_style))
            chart_table_data = [
                [Paragraph("Chart Title", cell_header_style), Paragraph("Type", cell_header_style), Paragraph("Dimension (X)", cell_header_style), Paragraph("Metric (Y)", cell_header_style), Paragraph("Aggregation", cell_header_style), Paragraph("Top N", cell_header_style)]
            ]
            for c in session.charts:
                chart_table_data.append([
                    Paragraph(c.title, cell_style),
                    Paragraph(c.chart_type.replace("_", " ").title(), cell_style),
                    Paragraph(c.x_col or "-", cell_style),
                    Paragraph(c.y_col or "-", cell_style),
                    Paragraph((c.agg or "-").upper(), cell_style),
                    Paragraph(str(c.top_n) if c.top_n else "All", cell_style)
                ])
            t_chart = Table(chart_table_data, colWidths=[150, 80, 90, 90, 60, 40])
            t_chart.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")])
            ]))
            story.append(t_chart)
            story.append(Spacer(1, 14))

        # 4. Active Filters
        if session.active_filters:
            story.append(Paragraph("4. Applied Filters", h2_style))
            flt_data = [
                [Paragraph("Filtered Column", cell_header_style), Paragraph("Active Value", cell_header_style)]
            ]
            for col, val in session.active_filters.items():
                flt_data.append([
                    Paragraph(col, cell_style),
                    Paragraph(str(val), cell_style)
                ])
            t_flt = Table(flt_data, colWidths=[200, 300])
            t_flt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#64748b")),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('PADDING', (0, 0), (-1, -1), 5)
            ]))
            story.append(t_flt)

        doc.build(story)
        buf.seek(0)
        return buf.getvalue()

export_service = ExportService()
