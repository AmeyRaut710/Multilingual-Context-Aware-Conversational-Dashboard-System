# System Architecture & Technical Specification

## Project Title
**Multilingual Context-Aware Conversational Dashboard Generation and Modification System**

---

## 1. High-Level Architecture Overview

The system follows a modern decoupled architecture consisting of an asynchronous Python FastAPI backend, a reactive TypeScript React frontend, a rule- and semantic-based multilingual natural language processing pipeline, and temporary in-memory session management.

```
+-----------------------------------------------------------------------------------------+
|                                    REACT FRONTEND                                       |
|  +--------------------+  +----------------------+  +---------------------------------+  |
|  |  Welcome / Upload  |  | Dashboard Workspace  |  |     Conversational Assistant    |  |
|  |  - New Project     |  | - Filter Bar         |  |     - Web Speech API (EN/HI/MR) |  |
|  |  - Restore ZIP     |  | - Dynamic KPI Cards  |  |     - Ambiguity Option Buttons  |  |
|  |  - Sample Loaders  |  | - Plotly Chart Grid  |  |     - Detected Language Badge   |  |
|  +--------------------+  +----------------------+  +---------------------------------+  |
+--------------------------------------------|--------------------------------------------+
                                             | HTTP / REST API (Port 8000)
+--------------------------------------------v--------------------------------------------+
|                                   FASTAPI BACKEND                                       |
|                                                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |                                API ROUTERS (/api)                                 |  |
|  |  /project/new  /project/upload  /dataset/upload  /command/process  /export/zip... |  |
|  +-----------------------------------------|-----------------------------------------+  |
|                                            |                                            |
|  +-----------------------------------------v-----------------------------------------+  |
|  |                               CORE SERVICES                                       |  |
|  |  +-----------------------+ +---------------------+ +---------------------------+  |  |
|  |  |  LanguageService      | | ContextService      | | AmbiguityService          |  |  |
|  |  |  - Script detection   | | - Active chart ID   | | - Ambiguous target detect |  |  |
|  |  |  - Vocabulary mapping | | - Pronoun ('it')    | | - Missing metric detect   |  |  |
|  |  |  - Multilingual regex | | - Command history   | | - Clarification & resume  |  |  |
|  |  +-----------------------+ +---------------------+ +---------------------------+  |  |
|  |  +-----------------------+ +---------------------+ +---------------------------+  |  |
|  |  |  DatasetService       | | VisualizationService| | ExportService             |  |  |
|  |  |  - CSV/XLSX parser    | | - 12 Plotly charts  | | - Restorable ZIP bundle   |  |  |
|  |  |  - Multi-sheet switch | | - Pandas agg engine | | - Offline standalone HTML |  |  |
|  |  |  - Summary stats      | | - Dynamic KPI cards | | - ReportLab PDF generator |  |  |
|  |  +-----------------------+ +---------------------+ +---------------------------+  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |  |  SessionManager: In-Memory TTL Store (60-min expiry, explicit clear, no DB) |  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  +-----------------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------------+
```

---

## 2. Key Modules and Responsibilities

### 2.1 Multilingual NLP Pipeline
- **Language Detection**: Detects input script (Devanagari vs Latin) and grammatical markers:
  - **Devanagari Marathi**: "करा", "दाखवा", "बदला", "तयार करा", "एकूण", "मधील", "नुसार", "कमी", "जास्त".
  - **Devanagari Hindi**: "बनाओ", "दिखाओ", "करो", "में", "का", "की", "कुल", "सहित", "हटाओ", "बदलो".
  - **Hinglish**: "banao", "dikhao", "karo", "badlo", "ka", "ki", "mein", "kul", "sabse".
  - **Marathi-English**: "kara", "dakhva", "badla", "tayar", "ekun", "nusar", "madhe", "cha", "chi".
  - **English**: Standard English phrases.
- **Entity & Metric Extraction**: Maps user terms to dataset columns using domain synonyms (e.g., `Sales` / `Revenue` / `विक्री` / `उत्पन्न`, `Profit` / `नफा` / `लाभ`).
- **Aggregations & Time Groupings**: Normalizes `sum`, `avg`, `min`, `max`, `count`, and time dimensions (`month`, `year`, `quarter`, `day`).

### 2.2 Context & Pronoun Resolution
- Maintains `selected_chart_id`, `last_modified_chart_id`, and full conversation history.
- Resolves pronouns (`it`, `that`, `that chart`, `त्याला`, `usse`, `isko`) to the active chart without requiring explicit chart names.
- Preserves all previously generated charts when a new chart is added.

### 2.3 Ambiguity Detection & Resumption
- Detects under-specified commands:
  - If user commands `"Change that chart"` when multiple charts exist with no explicit active selection, the system prompts: `"Which chart would you like to modify?"` and provides clickable option pills for existing charts.
  - If user commands `"Show the top 5"` without a metric, the system asks: `"Top 5 based on which metric: Sales, Profit, Quantity?"`.
- When the user clicks an option or replies, the system resumes execution of the original command automatically.

### 2.4 Analytical Validation Module
- Validates that columns exist in the active worksheet.
- Enforces strict analytical rules:
  - Rejects mathematical aggregations (`sum`, `average`) on non-numeric columns and suggests `count`.
  - Rejects time groupings when no date/time column is available.
  - Never hallucinates phantom columns or manufactured metrics.

### 2.5 Visualization & KPI Engine
- Supports 12 chart types:
  1. Bar Chart (vertical)
  2. Horizontal Bar Chart
  3. Line Chart (with spline curves and markers)
  4. Pie Chart
  5. Donut Chart (with hole percentage)
  6. Scatter Plot (2 numeric dimensions, optional category color hue)
  7. Histogram (frequency distribution)
  8. Area Chart (filled curve)
  9. Box Plot (distribution and outliers)
  10. Heatmap (pivot correlation)
  11. Stacked Bar Chart
  12. Grouped Bar Chart
- Renders responsive Plotly JSON specs with professional color palettes and dark mode support.
- KPI Engine computes scalar values, currency/number formatting, and updates dynamically upon filtering.

### 2.6 Privacy & Temporary Storage Management
- Strictly **zero permanent database storage** (no MongoDB, no PostgreSQL, no SQLite).
- All uploaded files and dataframes reside in volatile session memory.
- Automatic TTL cleanup (60-minute inactivity threshold) and an explicit **Clear Workspace** button.

### 2.7 Export & Restoration System
1. **ZIP Project Export & Restore**:
   - `project.zip` contains:
     - `dataset/original_dataset.(csv|xlsx)`
     - `dashboard_config.json` (charts, KPIs, filters, layout)
     - `metadata.json` (project name, version, timestamp, sheets)
   - ZIP restoration checks for path traversal, file size limits, required files, and restores the full dashboard without re-uploading the dataset.
2. **Standalone Interactive HTML Export**:
   - 100% self-contained single-file HTML.
   - Inlines Plotly.js, serialized dataset rows, chart configs, and an offline JavaScript filtering engine.
   - Operates completely offline without internet or server connectivity.
3. **PDF Export**:
   - Generates a formatted PDF report with ReportLab featuring summary tables, KPIs, and visualization metadata.

