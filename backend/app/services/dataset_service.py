import io
import warnings
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np
from app.models.schemas import DatasetMeta, ColumnMeta
from app.services.session_service import SessionData

class DatasetService:
    @staticmethod
    def infer_column_type(series: pd.Series) -> str:
        """Infer high-level column type: numeric, datetime, categorical, or boolean."""
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
        
        # Check if it could be datetime
        non_null = series.dropna()
        if len(non_null) > 0:
            # Quick sample check to avoid slow parsing on massive string columns
            sample = non_null.head(50)
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    pd.to_datetime(sample, errors="raise")
                return "datetime"
            except (ValueError, TypeError):
                pass

        return "categorical"

    @staticmethod
    def compute_metadata(df: pd.DataFrame, filename: str, file_type: str, sheet_names: List[str] = [], active_sheet: Optional[str] = None) -> DatasetMeta:
        total_rows = len(df)
        total_columns = len(df.columns)
        duplicate_count = int(df.duplicated().sum())

        columns_meta: List[ColumnMeta] = []
        for col in df.columns:
            series = df[col]
            dtype_label = DatasetService.infer_column_type(series)
            null_count = int(series.isnull().sum())
            unique_count = int(series.nunique(dropna=True))
            sample_vals = [str(x) for x in series.dropna().unique()[:5]]

            min_val = None
            max_val = None
            mean_val = None

            if dtype_label == "numeric":
                valid_num = series.dropna()
                if len(valid_num) > 0:
                    min_val = float(valid_num.min())
                    max_val = float(valid_num.max())
                    mean_val = round(float(valid_num.mean()), 2)
            elif dtype_label == "datetime":
                try:
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        dt_series = pd.to_datetime(series, errors="coerce", format="mixed")
                    min_val = str(dt_series.min())[:10]
                    max_val = str(dt_series.max())[:10]
                except Exception:
                    pass

            columns_meta.append(ColumnMeta(
                name=str(col),
                dtype=dtype_label,
                null_count=null_count,
                unique_count=unique_count,
                sample_values=sample_vals,
                min_val=min_val,
                max_val=max_val,
                mean_val=mean_val
            ))

        # Preview of first 15 rows with clean JSON-serializable types
        preview_df = df.head(15).copy()
        # Convert NaN to None
        preview_df = preview_df.replace({np.nan: None})
        preview_rows = preview_df.to_dict(orient="records")

        return DatasetMeta(
            filename=filename,
            file_type=file_type,
            total_rows=total_rows,
            total_columns=total_columns,
            columns=columns_meta,
            sheet_names=sheet_names,
            active_sheet=active_sheet,
            duplicate_count=duplicate_count,
            preview_rows=preview_rows
        )

    @classmethod
    def process_file_bytes(cls, file_bytes: bytes, filename: str, session: SessionData) -> DatasetMeta:
        file_ext = filename.split(".")[-1].lower() if "." in filename else "csv"
        session.original_file_bytes = file_bytes
        session.original_filename = filename
        session.file_type = file_ext

        if file_ext in ["xlsx", "xls"]:
            excel_file = pd.ExcelFile(io.BytesIO(file_bytes), engine="openpyxl")
            sheet_names = excel_file.sheet_names
            session.excel_sheets = {}
            for sname in sheet_names:
                session.excel_sheets[sname] = excel_file.parse(sname)
            
            active_sheet = sheet_names[0]
            session.active_sheet = active_sheet
            df = session.excel_sheets[active_sheet].copy()
        else:
            # CSV file
            sheet_names = []
            active_sheet = None
            try:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin1")

        # Strip whitespace from column names
        df.columns = [str(c).strip() for c in df.columns]

        session.df_original = df.copy()
        session.df_working = df.copy()
        session.dataset_meta = cls.compute_metadata(df, filename, file_ext, sheet_names, active_sheet)
        return session.dataset_meta

    @classmethod
    def switch_sheet(cls, session: SessionData, sheet_name: str) -> DatasetMeta:
        if sheet_name not in session.excel_sheets:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {list(session.excel_sheets.keys())}")
        
        df = session.excel_sheets[sheet_name].copy()
        df.columns = [str(c).strip() for c in df.columns]
        session.active_sheet = sheet_name
        session.df_original = df.copy()
        session.df_working = df.copy()
        
        # Reset charts, KPIs, filters for the new sheet
        session.charts = []
        session.kpis = []
        session.filters = []
        session.active_filters = {}
        session.selected_chart_id = None
        session.last_modified_chart_id = None

        meta = cls.compute_metadata(
            df,
            session.original_filename or "dataset.xlsx",
            "xlsx",
            list(session.excel_sheets.keys()),
            sheet_name
        )
        session.dataset_meta = meta
        return meta

    @classmethod
    def get_paginated_table(
        cls,
        session: SessionData,
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
        column_filters: Optional[Dict[str, str]] = None,
        use_dashboard_filters: bool = True
    ) -> Dict[str, Any]:
        df = session.df_working if session.df_working is not None else session.df_original
        if df is None:
            raise ValueError("No active dataset in session.")

        total_rows = len(df)
        total_columns = len(df.columns)
        columns = [str(c) for c in df.columns]

        if use_dashboard_filters and session.active_filters:
            work_df = session.get_filtered_df()
        else:
            work_df = df.copy()

        # 1. Global Search across all columns
        if search and search.strip():
            s = search.strip().lower()
            mask = pd.Series(False, index=work_df.index)
            for col in work_df.columns:
                col_str = work_df[col].astype(str).str.lower()
                mask = mask | col_str.str.contains(s, regex=False, na=False)
            work_df = work_df[mask]

        # 2. Individual Column Filters
        if column_filters:
            for col, val in column_filters.items():
                if val and str(val).strip() and col in work_df.columns:
                    val_str = str(val).strip().lower()
                    col_str = work_df[col].astype(str).str.lower()
                    work_df = work_df[col_str.str.contains(val_str, regex=False, na=False)]

        # 3. Sorting across the complete filtered dataset
        if sort_by and sort_by in work_df.columns:
            ascending = (sort_order or "asc").lower() != "desc"
            work_df = work_df.sort_values(by=sort_by, ascending=ascending, na_position="last")

        filtered_rows = len(work_df)
        page_size = max(1, page_size)
        total_pages = max(1, (filtered_rows + page_size - 1) // page_size)
        
        page = max(1, min(page, total_pages))
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, filtered_rows)

        page_slice = work_df.iloc[start_idx:end_idx].copy()
        page_slice = page_slice.replace({np.nan: None})
        rows = page_slice.to_dict(orient="records")

        columns_meta = session.dataset_meta.columns if session.dataset_meta else []

        start_row = start_idx + 1 if filtered_rows > 0 else 0
        end_row = end_idx

        return {
            "success": True,
            "total_rows": total_rows,
            "total_columns": total_columns,
            "filtered_rows": filtered_rows,
            "total_pages": total_pages,
            "current_page": page,
            "page_size": page_size,
            "start_row": start_row,
            "end_row": end_row,
            "columns": columns,
            "columns_meta": columns_meta,
            "rows": rows
        }

dataset_service = DatasetService()
