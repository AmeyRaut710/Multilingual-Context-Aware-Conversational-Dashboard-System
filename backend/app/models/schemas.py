from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ColumnMeta(BaseModel):
    name: str
    dtype: str  # numeric, datetime, categorical, boolean
    null_count: int
    unique_count: int
    sample_values: List[Any] = []
    min_val: Optional[Any] = None
    max_val: Optional[Any] = None
    mean_val: Optional[float] = None

class DatasetMeta(BaseModel):
    filename: str
    file_type: str  # csv, xlsx
    total_rows: int
    total_columns: int
    columns: List[ColumnMeta]
    sheet_names: List[str] = []
    active_sheet: Optional[str] = None
    duplicate_count: int = 0
    preview_rows: List[Dict[str, Any]] = []

class ChartConfig(BaseModel):
    id: str
    title: str
    chart_type: str  # bar, horizontal_bar, line, pie, donut, scatter, histogram, area, box, heatmap, stacked_bar, grouped_bar
    x_col: Optional[str] = None
    y_col: Optional[str] = None
    color_col: Optional[str] = None
    agg: Optional[str] = "sum"  # sum, avg, count, min, max
    top_n: Optional[int] = None
    sort_order: Optional[str] = "desc"  # asc, desc
    time_group: Optional[str] = None  # month, quarter, year, day
    filter_conditions: List[Dict[str, Any]] = []
    plotly_spec: Dict[str, Any] = {}
    width: str = "half"  # half, full
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class KPIConfig(BaseModel):
    id: str
    title: str
    metric_col: str
    agg: str = "sum"  # sum, avg, count, distinct_count, min, max
    value: float = 0.0
    formatted_value: str = "0"
    prefix: str = ""
    suffix: str = ""
    filter_conditions: List[Dict[str, Any]] = []

class FilterItem(BaseModel):
    id: str
    column: str
    filter_type: str  # dropdown, category, date_range, numeric_range, search
    options: List[Any] = []
    current_value: Optional[Any] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None

class DashboardState(BaseModel):
    project_name: str = "Untitled Project"
    session_id: str
    dataset_meta: Optional[DatasetMeta] = None
    charts: List[ChartConfig] = []
    kpis: List[KPIConfig] = []
    filters: List[FilterItem] = []
    selected_chart_id: Optional[str] = None
    last_modified_chart_id: Optional[str] = None
    command_history: List[Dict[str, Any]] = []

class ClarificationQuestion(BaseModel):
    question: str
    parameter_needed: str  # target_chart, metric_col, category_col, chart_type, filter_value
    options: List[str] = []
    original_intent: str
    partial_entities: Dict[str, Any] = {}

class CommandRequest(BaseModel):
    session_id: str
    command: str
    context_override: Optional[Dict[str, Any]] = None

class CommandResponse(BaseModel):
    success: bool
    detected_language: str  # English, Hindi, Marathi, Hinglish, Marathi-English
    intent: str
    message: str
    entities: Dict[str, Any] = {}
    requires_clarification: bool = False
    clarification: Optional[ClarificationQuestion] = None
    updated_state: Optional[DashboardState] = None
    error_details: Optional[str] = None

class NewProjectRequest(BaseModel):
    project_name: str = "Untitled Project"

class SelectSheetRequest(BaseModel):
    session_id: str
    sheet_name: str

class FilterUpdateRequest(BaseModel):
    session_id: str
    column: str
    value: Any

class ClearFilterRequest(BaseModel):
    session_id: str
    column: Optional[str] = None  # None clears all filters

class DataTableRequest(BaseModel):
    session_id: str
    page: int = 1
    page_size: int = 100  # 25, 50, 100, 250
    search: Optional[str] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "asc"  # asc, desc
    column_filters: Optional[Dict[str, str]] = None
    use_dashboard_filters: bool = True

class DataTableResponse(BaseModel):
    success: bool
    total_rows: int
    total_columns: int
    filtered_rows: int
    total_pages: int
    current_page: int
    page_size: int
    start_row: int
    end_row: int
    columns: List[str]
    columns_meta: List[ColumnMeta] = []
    rows: List[Dict[str, Any]]


class ChartUpdateRequest(BaseModel):
    session_id: str
    chart_id: str
    chart_type: Optional[str] = None
    title: Optional[str] = None
    agg: Optional[str] = None
    top_n: Optional[int] = None
    sort_order: Optional[str] = None

class ChartDeleteRequest(BaseModel):
    session_id: str
    chart_id: str

class KPIDeleteRequest(BaseModel):
    session_id: str
    kpi_id: str

