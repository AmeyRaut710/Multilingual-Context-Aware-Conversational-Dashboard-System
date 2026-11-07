# Multilingual Context-Aware Conversational Dashboard Generation and Modification System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178c6.svg)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3.4-38bdf8.svg)](https://tailwindcss.com/)
[![Plotly](https://img.shields.io/badge/Plotly.js-2.35.2-3f4f75.svg)](https://plotly.com/javascript/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A state-of-the-art Business Intelligence (BI) and data analytics system that enables users to create, modify, filter, and export interactive dashboards using natural language voice and text commands in **English**, **Hindi (हिन्दी / Hinglish)**, **Marathi (मराठी / Marathi-English)**, and **code-mixed** dialects.

---

## 🌟 Key Features

1. **Multilingual Speech & Text Understanding**:
   - Understands commands in **English**, **Hindi**, **Marathi**, **Hinglish**, and **Marathi-English**.
   - Built-in offline voice recognition using the browser's native **Web Speech API** (`en-US`, `hi-IN`, `mr-IN`) with backend **Faster-Whisper** audio transcription support.
   - Detects the spoken language automatically and displays language indicators.

2. **Context-Aware Conversational Modification**:
   - Maintains conversation history and active visualization state.
   - Accurately resolves pronouns (`"it"`, `"that chart"`, `"revenue chart"`, `"त्याला"`, `"usse"`) to the correct chart without resetting previous charts.

3. **Ambiguity Detection & Interactive Resolution**:
   - Identifies under-specified requests (e.g., *"Show the top five"* without a metric, or *"Change that chart"* when multiple charts exist).
   - Prompts the user with clarification questions and clickable options (`[Sales]`, `[Profit]`), and automatically resumes the command upon selection.

4. **12+ Interactive Visualization Types (Plotly.js)**:
   - Bar, Horizontal Bar, Line, Pie, Donut, Scatter Plot, Histogram, Area, Box Plot, Heatmap, Stacked Bar, and Grouped Bar.
   - Supports sorting, aggregations (`sum`, `avg`, `min`, `max`, `count`), top-N filters, and time-based grouping (`monthly`, `yearly`, `quarterly`).

5. **Dynamic Key Performance Indicators (KPIs)**:
   - Natural language KPI creation (e.g., *"Show total revenue"*, *"Ekun sales dakhva"*, *"Calculate average profit"*).
   - Automatically recalculates values in real-time when dashboard filters are applied.

6. **Dashboard-Wide Interactive Filtering**:
   - Dropdown and category filters update all charts and KPIs simultaneously.

7. **Multi-Format Export & Restoration**:
   - **Restorable ZIP Project Archive**: Downloads dataset, `dashboard_config.json`, and `metadata.json`. Restores the full dashboard state without needing to re-upload the dataset.
   - **Standalone Interactive HTML**: 100% self-contained single-file HTML embedding Plotly.js and client-side filter logic. Works completely offline without an internet connection or backend server.
   - **Executive PDF Report**: Static report generated via ReportLab with summary tables and chart inventories.

8. **Privacy-First Temporary Architecture**:
   - **Zero permanent database dependencies** (No MongoDB, PostgreSQL, or SQLite).
   - In-memory session management with automatic 60-minute TTL cleanup and a 1-click **Clear Workspace** button.

---

## 🏗️ System Architecture

```
project-root/
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application & static router
│   │   ├── api/endpoints.py           # REST endpoints
│   │   ├── core/config.py             # System configuration
│   │   ├── models/schemas.py          # Pydantic data models
│   │   ├── services/
│   │   │   ├── dataset_service.py     # CSV/XLSX parser & metadata extractor
│   │   │   ├── language_service.py    # Multilingual detector & vocabulary normalizer
│   │   │   ├── intent_service.py      # Intent classifier & entity parser
│   │   │   ├── context_service.py     # Conversation context & pronoun resolver
│   │   │   ├── ambiguity_service.py   # Ambiguity detector & clarification engine
│   │   │   ├── validation_service.py  # Analytical validation & schema checker
│   │   │   ├── visualization_service.py # Plotly JSON & aggregation engine
│   │   │   ├── dashboard_service.py   # Dashboard state orchestrator
│   │   │   ├── export_service.py      # ZIP restore, standalone HTML, PDF generator
│   │   │   ├── session_service.py     # In-memory session store & TTL manager
│   │   │   └── speech_service.py      # Audio transcription service
│   │   └── tests/
│   │       └── test_full_suite.py     # Comprehensive automated test suite
│   └── static/                        # Bundled offline assets (plotly.min.js)
│
├── frontend/
│   ├── src/
│   │   ├── components/                # Navbar, KPISection, ChartGrid, ChartCard,
│   │   │                              # FilterBar, ChatAssistant, DatasetInfoModal, ExportModal
│   │   ├── pages/                     # WelcomePage, DashboardWorkspace
│   │   ├── services/                  # api.ts, speech.ts
│   │   ├── types/                     # dashboard.ts
│   │   ├── App.tsx                    # Theme management & page routing
│   │   └── main.tsx                   # React root entry
│   ├── public/                        # Offline plotly.min.js & sample datasets
│   ├── dist/                          # Production-compiled frontend build
│   └── package.json
│
├── sample_datasets/
│   ├── superstore_sales.csv           # 500-row realistic retail sales benchmark dataset
│   ├── retail_sales_multisheet.xlsx   # 3-sheet Excel workbook (2023, 2024, Category Summary)
│   └── generate_samples.py            # Reproducible sample generator script
│
├── documentation/
│   ├── architecture.md                # Technical architecture document
│   ├── multilingual_nlp_guide.md      # Command syntax and NLP parsing guide
│   └── user_manual.md                 # Complete user guide
│
├── requirements.txt                   # Backend Python dependencies
└── README.md
```

---

## 💻 Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Plotly.js |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pandas, NumPy, OpenPyXL, Pydantic, ReportLab |
| **Speech & NLP** | Web Speech API (`en-US`, `hi-IN`, `mr-IN`), Faster-Whisper, Rule & Synonym Parsing |
| **Storage** | Volatile in-memory sessions with TTL expiration (No permanent DB) |
| **Export Formats**| ZIP Archive, Standalone HTML (Client-side JS filters), PDF Document |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm (optional if using pre-built distribution)

### 2. Backend Setup
From the project root:
```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt
```

### 3. Run the Unified Application
You can run the full application with a single command. The backend will automatically serve both the REST API and the compiled React frontend:
```bash
# Set PYTHONPATH and start the server
$env:PYTHONPATH="d:\Major Project 2\backend"
python backend/app/main.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

### 4. Running the Frontend in Development Mode (Optional)
If you wish to make changes to the React code with live Hot Module Replacement (HMR):
```bash
cd frontend
npm install
npm run dev
```
Navigate to **`http://localhost:5173`** (Vite proxies all API requests to `http://127.0.0.1:8000`).

---

## 🎙️ Using Voice & Text Commands

### 1. Voice Commands
1. Click the **Microphone** button in the chat assistant (bottom right).
2. Choose your preferred language from the dropdown (**English**, **Hindi**, or **Marathi**).
3. Speak your instruction. The recognized text appears in the input field and executes.

### 2. Natural Language Text Commands
Type instructions into the chat box. Examples:

#### English Commands
- `Create a bar chart of monthly sales`
- `Show total revenue`
- `Compare sales by region`
- `Change it to a line chart`
- `Show the top five products by profit`

#### Hindi Commands
- `Monthly sales ka bar chart banao`
- `Total revenue dikhao`
- `Region ke according sales compare karo`
- `Revenue chart ko line chart mein change karo`
- `कुल बिक्री दिखाओ`

#### Marathi Commands
- `Monthly sales cha bar chart tayar kara`
- `Ekun revenue dakhva`
- `Region nusar sales compare kara`
- `Revenue chart line chart madhe badla`
- `एकूण विक्री दाखवा`

#### Context & Ambiguity Handling
- **Context Pronouns**: After creating a profit chart, saying `"Change it to a pie chart"` will modify the profit chart without affecting other charts.
- **Ambiguity Clarification**: Saying `"Show the top five"` will prompt:
  *"Top 5 based on which metric: Sales, Profit, Quantity?"* with clickable buttons to resolve and continue immediately.

---

## 🧪 Automated Testing

A comprehensive automated test suite validates all 24 required capabilities:

```bash
$env:PYTHONPATH="d:\Major Project 2\backend"
python -m unittest discover -s backend/app/tests -v
```

### Verified Test Cases:
1. `test_01_upload_csv`: Validates CSV ingestion and column statistics.
2. `test_02_upload_excel`: Validates multi-sheet XLSX file processing.
3. `test_03_switch_worksheet`: Verifies worksheet switching and state resetting.
4. `test_04_create_bar_chart`: Verifies text command bar chart generation.
5. `test_05_speech_service_status`: Verifies speech service availability and diagnostics.
6. `test_06_create_multiple_charts`: Ensures adding new charts never deletes previous charts.
7. `test_07_generate_kpi_cards`: Tests dynamic KPI generation and formatting.
8. `test_08_09_context_resolution_and_modification`: Tests pronoun resolution (`"it"`) to the active chart.
9. `test_10_11_ambiguity_detection_and_clarification`: Tests detection of missing metrics and resumption after clarification.
10. `test_12_english_commands`: Validates English command execution.
11. `test_13_hindi_commands`: Validates Hindi (Devanagari & Hinglish) execution.
12. `test_14_marathi_commands`: Validates Marathi (Devanagari & Marathi-English) execution.
13. `test_15_code_mixed_commands`: Validates mixed-language queries.
14. `test_16_validate_incorrect_column`: Validates rejection of non-existent or incompatible columns.
15. `test_17_18_filtering_and_kpi_update`: Verifies real-time recalculation of charts and KPIs on filtering.
16. `test_19_20_zip_export_and_restore`: Tests complete ZIP export, security validation, and restoration.
17. `test_21_22_standalone_html_export`: Verifies offline interactive HTML export with client-side filters.
18. `test_23_pdf_export`: Validates ReportLab PDF document generation.
19. `test_24_clear_workspace`: Verifies temporary in-memory session data destruction.

---

## 📦 Project Export & Restoration

Click **Export** in the top navigation bar to select:
1. **Project ZIP Archive**: Generates a restorable `.zip` containing the original dataset and dashboard configuration. Restoring this archive on the home page brings back all charts, KPIs, filters, and conversation history without re-uploading the dataset.
2. **Standalone Interactive HTML**: Downloads a single-file dashboard with embedded Plotly and client-side JavaScript filtering that works 100% offline without the backend.
3. **PDF Summary Report**: Generates a clean executive report for documentation and printing.

---

## 🔒 Security & Privacy Guarantees
- No user datasets or session information are permanently stored in a database.
- Sessions are maintained in volatile memory and expired after 60 minutes of inactivity.
- ZIP file restoration implements strict path traversal guards (anti-Zip Slip) and file size limits.
- No dataset contents are sent to external paid AI services.

---

## ⚠️ Known Technical Limitations & Solutions

1. **Browser Closure vs Server Session Expiration**:
   - *Limitation*: Browsers cannot guarantee an HTTP request reaches the server upon sudden tab or window closure.
   - *Solution*: Explicit **Clear Workspace** button provided for manual deletion, backed by a server-side 60-minute inactivity TTL cleanup thread.
2. **Offline Speech Recognition Dependencies**:
   - *Limitation*: Installing heavy PyTorch/CUDA-based speech models like Faster-Whisper may require specific C++ compilers or hardware.
   - *Solution*: Seamless dual-mode architecture: modern browsers (Chrome/Edge/Safari) use the built-in offline Web Speech API with zero installations required, while the backend `/api/command/transcribe` endpoint provides optional server-side Whisper transcription.
3. **HTML Export Interactive Scope**:
   - *Limitation*: Standalone HTML files cannot run Python NLP logic without a backend.
   - *Solution*: The exported HTML embeds a custom client-side JavaScript engine that executes dataset filtering and updates all Plotly charts and KPI cards offline in the browser. Conversational chart creation remains available within the main application via ZIP project restoration.

---

## 📄 License
This project is developed for educational and research purposes as a B.Tech Computer Science Engineering Major Project. MIT License.
