import re
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
from app.models.schemas import DatasetMeta, ColumnMeta

class ValidationService:
    # Common domain synonyms for business analytics
    COLUMN_SYNONYMS = {
        "sales": ["sales", "sale", "revenue", "turnover", "income", "earnings", "विक्री", "उत्पन्न", "कमाई", "vikri"],
        "revenue": ["revenue", "sales", "turnover", "income", "earnings", "विक्री", "उत्पन्न", "कमाई", "vikri"],
        "profit": ["profit", "margin", "gain", "earnings", "income", "नफा", "लाभ", "nafa", "labh"],
        "quantity": ["quantity", "qty", "volume", "units", "count", "प्रमाण", "संख्या", "मात्रा", "praman", "sankhya"],
        "discount": ["discount", "rebate", "offer", "सूट", "सवलत", "chhoot", "savalat"],
        "region": ["region", "zone", "area", "territory", "प्रदेश", "विभाग", "क्षेत्र", "pradesh", "vibhag"],
        "state": ["state", "province", "राज्य", "rajya"],
        "city": ["city", "town", "शहर", "shahar"],
        "category": ["category", "segment", "type", "class", "वर्ग", "प्रकार", "varga", "prakar"],
        "sub_category": ["sub category", "subcategory", "sub-category", "उपवर्ग", "upvarga"],
        "product": ["product", "product name", "item", "good", "उत्पादन", "वस्तू", "utpadan", "vastu", "maal"],
        "order_id": ["order id", "order", "orders", "order number", "ऑर्डर"],
        "date": ["date", "order date", "ship date", "time", "day", "month", "दिनांक", "तारीख", "वेळ", "dinank", "tarikh"]
    }

    @classmethod
    def find_best_matching_column(cls, text: str, available_columns: List[ColumnMeta], preferred_dtype: Optional[str] = None) -> Optional[ColumnMeta]:
        """
        Fuzzy and synonym-aware column search from natural language text.
        """
        text_lower = text.lower()
        col_names = [c.name for c in available_columns]
        
        # 1. Exact or normalized column name in text
        for col in available_columns:
            clean_col = col.name.lower().replace("_", " ").strip()
            # Boundary search for clean col name
            if re.search(r'\b' + re.escape(clean_col) + r'\b', text_lower):
                if preferred_dtype is None or col.dtype == preferred_dtype:
                    return col

        # 2. Check domain synonyms
        for canonical, syn_list in cls.COLUMN_SYNONYMS.items():
            for syn in syn_list:
                if re.search(r'\b' + re.escape(syn.lower()) + r'\b', text_lower):
                    # Find a column in available_columns that matches this canonical concept
                    # e.g., if canonical is "sales", look for column containing "sales" or "revenue"
                    for col in available_columns:
                        c_lower = col.name.lower()
                        if canonical in c_lower or any(s in c_lower for s in syn_list if len(s) > 3):
                            if preferred_dtype is None or col.dtype == preferred_dtype:
                                return col

        # 3. Substring match
        for col in available_columns:
            clean_col = col.name.lower().replace("_", " ")
            parts = clean_col.split()
            for part in parts:
                if len(part) >= 4 and part in text_lower:
                    if preferred_dtype is None or col.dtype == preferred_dtype:
                        return col

        return None

    @classmethod
    def get_date_column(cls, available_columns: List[ColumnMeta]) -> Optional[ColumnMeta]:
        """Find the primary datetime column in the dataset."""
        date_cols = [c for c in available_columns if c.dtype == "datetime"]
        if date_cols:
            return date_cols[0]
        # Check by name if dtype wasn't strictly parsed
        for c in available_columns:
            c_lower = c.name.lower()
            if any(term in c_lower for term in ["date", "time", "year", "month", "day"]):
                return c
        return None

    @classmethod
    def get_numeric_columns(cls, available_columns: List[ColumnMeta]) -> List[ColumnMeta]:
        return [c for c in available_columns if c.dtype == "numeric"]

    @classmethod
    def get_categorical_columns(cls, available_columns: List[ColumnMeta]) -> List[ColumnMeta]:
        return [c for c in available_columns if c.dtype in ["categorical", "boolean"] or (c.unique_count <= 50 and c.dtype != "datetime")]

    @classmethod
    def validate_chart_request(cls, 
                               x_col: Optional[str], 
                               y_col: Optional[str], 
                               chart_type: str, 
                               agg: str, 
                               available_columns: List[ColumnMeta]) -> Tuple[bool, Optional[str]]:
        """
        Analytically validate the requested visualization against dataset schema.
        """
        col_dict = {c.name: c for c in available_columns}

        # Validate x_col
        if x_col and x_col not in col_dict:
            return False, f"The column '{x_col}' does not exist in this dataset. Available columns are: {', '.join(col_dict.keys())}"

        # Validate y_col
        if y_col and y_col not in col_dict:
            return False, f"The column '{y_col}' does not exist in this dataset. Available columns are: {', '.join(col_dict.keys())}"

        # Check aggregation validity on numeric
        if y_col and col_dict[y_col].dtype != "numeric" and agg in ["sum", "avg"]:
            return False, f"Cannot calculate '{agg}' on '{y_col}' because it is not a numeric column ({col_dict[y_col].dtype}). You can use 'count' instead."

        # Check chart specific requirements
        if chart_type in ["line", "area"] and x_col:
            x_meta = col_dict[x_col]
            # Line charts are best for date/time or ordered numeric
            if x_meta.dtype not in ["datetime", "numeric"] and x_meta.unique_count > 100:
                return False, f"Column '{x_col}' has too many distinct unordered values ({x_meta.unique_count}) for a {chart_type} chart."

        if chart_type in ["pie", "donut"] and x_col:
            x_meta = col_dict[x_col]
            if x_meta.unique_count > 30:
                return False, f"Column '{x_col}' has {x_meta.unique_count} distinct categories. A pie or donut chart is unreadable with more than 20 categories. Consider using a bar chart or filtering for the top 5."

        return True, None

    @classmethod
    def validate_kpi_request(cls, metric_col: str, agg: str, available_columns: List[ColumnMeta]) -> Tuple[bool, Optional[str]]:
        col_dict = {c.name: c for c in available_columns}
        if metric_col not in col_dict:
            return False, f"Metric column '{metric_col}' was not found in the dataset. Available numeric metrics are: {', '.join([c.name for c in available_columns if c.dtype == 'numeric'])}"

        col_meta = col_dict[metric_col]
        if agg in ["sum", "avg", "min", "max"] and col_meta.dtype != "numeric":
            return False, f"Cannot calculate {agg.upper()} on '{metric_col}' because it contains non-numeric data ({col_meta.dtype}). Use 'count' or 'distinct_count' instead."

        return True, None

validation_service = ValidationService()
