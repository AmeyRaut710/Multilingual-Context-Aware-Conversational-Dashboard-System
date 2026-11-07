# User Manual & Operator Guide

## 1. Getting Started

When you open the application in your browser (`http://127.0.0.1:8000`), you will see the **Welcome Page** offering two paths:

### Option 1: New Project
1. Enter your project name (e.g., `Superstore Q4 Performance`).
2. Upload a dataset file (`.csv` or `.xlsx`) using the drag-and-drop zone.
   - Alternatively, click **Load Superstore Sales (.CSV)** or **Load Multi-Sheet Retail (.XLSX)** to start immediately with pre-generated sample data.
3. Click **Open Dashboard Workspace**.

### Option 2: Upload Existing Project
1. Switch to the **Upload Existing Project** tab.
2. Select a previously downloaded `project.zip` file.
3. The application will validate the archive, extract the original dataset, restore all charts, KPI cards, applied filters, and conversation history, and reopen the dashboard in an editable state.

---

## 2. Using Voice and Text Commands

In the bottom-right corner of the workspace, you will find the **Conversational Assistant**.

### Voice Input (Microphone Button)
1. Select your preferred speech dialect from the dropdown:
   - **English (US/India)**
   - **Hindi (हिन्दी)**
   - **Marathi (मराठी)**
2. Click the **Microphone** icon. It will turn red and pulse, indicating active listening.
3. Speak your instruction clearly into your microphone.
4. The recognized speech will appear in the input box and can be sent immediately.

### Text Input
Type instructions directly into the input box and press **Enter** or click the **Send** button.

### Example Commands to Try:
- **English**:
  - `Create a bar chart of monthly sales`
  - `Show total revenue`
  - `Compare sales by region`
  - `Change it to a line chart`
  - `Show the top 5 products by profit`
- **Hindi / Hinglish**:
  - `Monthly sales ka bar chart banao`
  - `Total revenue dikhao`
  - `Region ke according sales compare karo`
  - `Revenue chart ko line chart mein change karo`
- **Marathi / Marathi-English**:
  - `Monthly sales cha bar chart tayar kara`
  - `Ekun revenue dakhva`
  - `Region nusar sales compare kara`
  - `Revenue chart line chart madhe badla`

---

## 3. Ambiguity Clarifications

If you issue an incomplete instruction such as:
- `Show the top five`
The system will display a clarification prompt with buttons:
`[Sales] [Profit] [Quantity]`
Clicking any button immediately resolves the ambiguity and creates your visualization.

---

## 4. Dashboard Controls & Customization

- **View Complete Data**: Click the **View Complete Data** button in the top navigation bar or inside the Dataset Information modal to open a full-screen, high-performance table view:
  - Displays all rows and columns using backend pagination with selectable page sizes: **25, 50, 100, and 250** rows per page.
  - Search across all columns simultaneously using the global search input.
  - Sort by any column by clicking its header (toggles ascending/descending) — sorting is executed across the complete dataset in the backend, not merely the visible page.
  - Apply individual column filters in the filter row.
  - Clear `null` value badges and horizontal/vertical scrolling for wide and long datasets.
  - Click **Close** or press **Esc** to return to your dashboard without losing any dashboard state.
- **Selecting a Chart**: Click on any chart card. A glowing indigo border will indicate that this chart is now the active focus for subsequent pronoun commands (e.g. `Change it to a donut chart`).
- **Changing Chart Types**: Use the dropdown selector in the top-right toolbar of any chart card.
- **Expanding Width**: Click the maximize/minimize icon on any chart card to toggle between 1-column and full-width 2-column views.
- **Deleting Visualizations**: Click the trash icon on any chart card or KPI card.
- **Interactive Filtering**: Use the top filter bar dropdowns. When you select a category (e.g., `Region = West`), **all charts and KPIs instantly update** to reflect only data from that category! Click **Reset Filters** to return to the full dataset view.
- **Worksheet Switcher**: If using a multi-sheet Excel file, use the Sheet dropdown in the top navbar to switch between tabs (e.g. `Sales_2023`, `Sales_2024`, `Category_Summary`).

---

## 5. Exporting Your Work

Click the **Export** button in the top navbar to open the Export modal:

1. **Full Project ZIP Archive**: Download a restorable ZIP package containing your original dataset, `dashboard_config.json`, and `metadata.json`. You can reload this ZIP anytime using **Option 2** on the welcome page.
2. **Standalone Interactive HTML**: Download a single self-contained HTML file. Open it directly in Chrome, Edge, or Firefox without running any backend. It includes embedded Plotly.js and interactive client-side filters!
3. **Static PDF Report**: Download a printable executive summary PDF report generated via ReportLab with dataset summaries, KPI tables, and visualization inventories.

---

## 6. Privacy & Workspace Clearing

- The system stores no data in any permanent database.
- Click the **Clear** button in the top navbar to purge all session data and temporary working data from server memory.

