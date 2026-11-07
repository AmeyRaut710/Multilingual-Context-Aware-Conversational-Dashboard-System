import re
from typing import Dict, Any, Tuple, Optional, List
from app.services.language_service import language_service
from app.services.validation_service import validation_service
from app.services.context_service import context_service
from app.services.ambiguity_service import ambiguity_service
from app.services.session_service import SessionData
from app.models.schemas import CommandResponse, ClarificationQuestion, ChartConfig

class IntentService:
    @classmethod
    def parse_command(cls, command: str, session: SessionData) -> Dict[str, Any]:
        """
        Parses multilingual natural language command and extracts intent, entities, and context.
        """
        text = command.strip()
        lang = language_service.detect_language(text)
        text_lower = text.lower()

        available_cols = session.dataset_meta.columns if session.dataset_meta else []
        col_names = [c.name for c in available_cols]
        numeric_cols = [c.name for c in available_cols if c.dtype == "numeric"]

        # 1. Check if this is an answer to a pending clarification
        if session.pending_clarification:
            orig_intent, merged_entities = ambiguity_service.resolve_clarification(session, text)
            if orig_intent:
                return {
                    "intent": orig_intent,
                    "language": lang,
                    "entities": merged_entities,
                    "is_clarification_response": True
                }

        # 2. Check for Ambiguity first
        # A. Missing target chart when user says "change that chart"
        chart_ambiguity = ambiguity_service.check_chart_modification_ambiguity(text, session)
        if chart_ambiguity:
            session.pending_clarification = chart_ambiguity
            return {
                "intent": "AMBIGUOUS",
                "language": lang,
                "clarification": chart_ambiguity
            }

        # B. Missing metric for Top N
        metric_ambiguity = ambiguity_service.check_metric_ambiguity(text, session, numeric_cols)
        if metric_ambiguity:
            session.pending_clarification = metric_ambiguity
            return {
                "intent": "AMBIGUOUS",
                "language": lang,
                "clarification": metric_ambiguity
            }

        # 3. Intent Classification Rules
        # Filter / Slicer removals
        if any(w in text_lower for w in [
            "clear filter", "reset filter", "remove filter", "clear all filters", 
            "remove all filters", "clear slicer", "remove slicer", "filter hatao", 
            "filter kadha", "slicer hatao", "slicer kadha"
        ]):
            return {"intent": "REMOVE_FILTER", "language": lang, "entities": {}}

        # Slicer Creation Intent (e.g. "Add the slicer of Region and State", "Create Region slicer")
        has_slicer_word = any(w in text_lower for w in [
            "slicer", "slicers", "स्लाइसर", "स्लाइज़र", "स्लायसर", 
            "filter control", "filter bar", "add filter for", "add filter of"
        ])
        if has_slicer_word:
            all_slicer_cols = validation_service.find_all_matching_columns(text, available_cols)
            if all_slicer_cols:
                return {
                    "intent": "ADD_SLICER",
                    "language": lang,
                    "entities": {"columns": [c.name for c in all_slicer_cols]}
                }
            else:
                # If user says "add a slicer" with no column mentioned
                cat_cols = validation_service.get_categorical_columns(available_cols)
                cat_names = [c.name for c in cat_cols[:5]]
                clarification = ClarificationQuestion(
                    question=f"Which column would you like to create a slicer for ({', '.join(cat_names)})?",
                    parameter_needed="category_col",
                    options=cat_names,
                    original_intent="ADD_SLICER",
                    partial_entities={"raw_command": text}
                )
                session.pending_clarification = clarification
                return {
                    "intent": "AMBIGUOUS",
                    "language": lang,
                    "clarification": clarification
                }

        # Export Intent
        if any(w in text_lower for w in ["export", "download", "save project", "zip", "pdf", "html export", "डैशबोर्ड निर्यात"]):
            export_fmt = "zip"
            if "pdf" in text_lower:
                export_fmt = "pdf"
            elif "html" in text_lower:
                export_fmt = "html"
            return {"intent": "EXPORT_DASHBOARD", "language": lang, "entities": {"format": export_fmt}}

        # Clear Workspace
        if any(w in text_lower for w in ["clear workspace", "reset dashboard", "delete all", "start over"]):
            return {"intent": "CLEAR_WORKSPACE", "language": lang, "entities": {}}

        # Delete Chart
        if any(w in text_lower for w in ["delete chart", "remove chart", "chart hatao", "chart kadha", "chart delete"]):
            target_chart, _ = context_service.resolve_target_chart(text, session)
            return {
                "intent": "DELETE_CHART",
                "language": lang,
                "entities": {"target_chart_id": target_chart.id if target_chart else None}
            }

        # Modify Chart Type (e.g. "change it to a pie chart", "revenue chart ko line chart mein change karo")
        has_change_verb = any(w in text_lower for w in ["change", "convert", "switch", "modify", "badlo", "badla", "parivartan"])
        extracted_chart_type, chart_token = language_service.extract_chart_type(text)
        
        if has_change_verb and chart_token:
            target_chart, resolved = context_service.resolve_target_chart(text, session)
            return {
                "intent": "CHANGE_CHART_TYPE",
                "language": lang,
                "entities": {
                    "chart_type": extracted_chart_type,
                    "target_chart_id": target_chart.id if target_chart else (session.charts[-1].id if session.charts else None)
                }
            }

        # Top N intent (e.g. "show the top five products by profit", "top 5 regions")
        top_n, sort_order = language_service.extract_top_n(text)
        has_top_phrase = (top_n is not None) or any(w in text_lower for w in ["top", "bottom", "highest", "lowest", "sabse jyada", "sarvat jast"])

        # Detect Metrics and Dimensions
        metric_col_meta = validation_service.find_best_matching_column(text, available_cols, preferred_dtype="numeric")
        cat_col_meta = validation_service.find_best_matching_column(text, available_cols, preferred_dtype="categorical")
        date_col_meta = validation_service.get_date_column(available_cols)
        time_group = language_service.extract_time_group(text)
        agg_method, _ = language_service.extract_aggregation(text)

        # Apply Filter Intent (e.g. "filter for Electronics", "filter it for the top five regions")
        if any(w in text_lower for w in ["filter", "filter it", "sirf", "fakta", "only"]):
            # Check if filter specifies a column or value
            target_chart, _ = context_service.resolve_target_chart(text, session)
            filter_col = cat_col_meta.name if cat_col_meta else None
            return {
                "intent": "APPLY_FILTER",
                "language": lang,
                "entities": {
                    "column": filter_col,
                    "top_n": top_n,
                    "target_chart_id": target_chart.id if target_chart else None,
                    "raw_text": text
                }
            }

        # KPI Intent (e.g. "Show total revenue", "Total sales", "Calculate average profit", "Ekun revenue dakhva")
        # Distinct from chart if it asks for a single scalar metric and mentions no categories, no chart words
        is_kpi_phrase = any(w in text_lower for w in [
            "kpi", "show total", "total revenue", "total sales", "ekun", "kul", "average revenue", 
            "average profit", "calculate", "ausat", "sarasari", "number of orders", "total orders"
        ])
        has_chart_word = chart_token is not None or any(w in text_lower for w in ["chart", "plot", "graph", "आलेख", "चार्ट"])

        if is_kpi_phrase and not has_chart_word and metric_col_meta and not cat_col_meta and not time_group:
            return {
                "intent": "CREATE_KPI",
                "language": lang,
                "entities": {
                    "metric_col": metric_col_meta.name,
                    "agg": agg_method
                }
            }

        # Chart Creation Intent (Bar, Line, Pie, etc. or Top N chart)
        if has_chart_word or has_top_phrase or any(w in text_lower for w in ["compare", "banao", "dikhao", "dakhva", "tayar kara", "show", "plot"]):
            # Determine x_col and y_col
            x_col = None
            y_col = metric_col_meta.name if metric_col_meta else None

            # If time dimension mentioned (e.g. "monthly sales"), x is date column
            if time_group and date_col_meta:
                x_col = date_col_meta.name
                if chart_token is None:
                    # Default time series to line chart
                    extracted_chart_type = "line"
            elif cat_col_meta:
                x_col = cat_col_meta.name
            elif date_col_meta and any(w in text_lower for w in ["date", "time", "trend", "daily", "monthly", "yearly"]):
                x_col = date_col_meta.name
                if chart_token is None:
                    extracted_chart_type = "line"

            # If user wants top N, default to horizontal bar or bar for clean display
            if top_n and chart_token is None:
                extracted_chart_type = "horizontal_bar"

            return {
                "intent": "CREATE_CHART",
                "language": lang,
                "entities": {
                    "chart_type": extracted_chart_type,
                    "x_col": x_col,
                    "y_col": y_col,
                    "agg": agg_method,
                    "top_n": top_n,
                    "sort_order": sort_order or "desc",
                    "time_group": time_group
                }
            }

        # Fallback question or help
        return {
            "intent": "ASK_QUESTION",
            "language": lang,
            "entities": {"query": text}
        }

intent_service = IntentService()

