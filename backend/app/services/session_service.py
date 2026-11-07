import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import pandas as pd
from app.models.schemas import DashboardState, DatasetMeta, ChartConfig, KPIConfig, FilterItem, ClarificationQuestion

class SessionData:
    def __init__(self, session_id: str, project_name: str = "Untitled Project"):
        self.session_id: str = session_id
        self.project_name: str = project_name
        self.created_at: datetime = datetime.utcnow()
        self.last_active_at: datetime = datetime.utcnow()
        
        # Raw files and dataframes
        self.original_file_bytes: Optional[bytes] = None
        self.original_filename: Optional[str] = None
        self.file_type: Optional[str] = None  # csv, xlsx
        self.excel_sheets: Dict[str, pd.DataFrame] = {}
        self.active_sheet: Optional[str] = None
        self.df_original: Optional[pd.DataFrame] = None
        self.df_working: Optional[pd.DataFrame] = None
        
        # Metadata
        self.dataset_meta: Optional[DatasetMeta] = None
        
        # Dashboard elements
        self.charts: List[ChartConfig] = []
        self.kpis: List[KPIConfig] = []
        self.filters: List[FilterItem] = []  # Configured filter controls
        self.active_filters: Dict[str, Any] = {}  # {col_name: value}
        self.selected_chart_id: Optional[str] = None
        self.last_modified_chart_id: Optional[str] = None
        
        # Conversational context
        self.command_history: List[Dict[str, Any]] = []
        self.pending_clarification: Optional[ClarificationQuestion] = None

    def touch(self):
        self.last_active_at = datetime.utcnow()

    def get_filtered_df(self) -> pd.DataFrame:
        """Returns the working dataframe with active dashboard filters applied."""
        if self.df_working is None:
            return pd.DataFrame()
        
        df = self.df_working.copy()
        for col, val in self.active_filters.items():
            if val is None or val == "" or val == [] or val == "All" or val == "all":
                continue
            if col not in df.columns:
                continue
            
            # List of values (e.g. multi-select category)
            if isinstance(val, list):
                if len(val) > 0:
                    df = df[df[col].astype(str).isin([str(v) for v in val])]
            # Range filter (e.g. [min, max])
            elif isinstance(val, (list, tuple)) and len(val) == 2:
                df = df[(df[col] >= val[0]) & (df[col] <= val[1])]
            # Date range string e.g. "2023-01-01 to 2023-06-30"
            elif isinstance(val, str) and " to " in val:
                parts = val.split(" to ")
                if len(parts) == 2:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                    df = df[(df[col] >= parts[0]) & (df[col] <= parts[1])]
            # Single value
            else:
                df = df[df[col].astype(str) == str(val)]
        return df

    def to_dashboard_state(self) -> DashboardState:
        return DashboardState(
            project_name=self.project_name,
            session_id=self.session_id,
            dataset_meta=self.dataset_meta,
            charts=self.charts,
            kpis=self.kpis,
            filters=self.filters,
            selected_chart_id=self.selected_chart_id,
            last_modified_chart_id=self.last_modified_chart_id,
            command_history=self.command_history
        )


class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}

    def create_session(self, project_name: str = "Untitled Project") -> SessionData:
        self.cleanup_expired()
        session_id = str(uuid.uuid4())
        session = SessionData(session_id, project_name)
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        session = self._sessions.get(session_id)
        if session:
            session.touch()
        return session

    def clear_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def cleanup_expired(self, ttl_minutes: int = 60):
        cutoff = datetime.utcnow() - timedelta(minutes=ttl_minutes)
        expired_ids = [sid for sid, s in self._sessions.items() if s.last_active_at < cutoff]
        for sid in expired_ids:
            del self._sessions[sid]

session_manager = SessionManager()
