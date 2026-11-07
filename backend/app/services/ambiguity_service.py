from typing import Optional, List, Dict, Any, Tuple
from app.models.schemas import ClarificationQuestion, ChartConfig
from app.services.session_service import SessionData

class AmbiguityService:
    @classmethod
    def check_chart_modification_ambiguity(cls, text: str, session: SessionData) -> Optional[ClarificationQuestion]:
        """
        Detects if user wants to modify/delete a chart, but multiple exist and it's unclear which one.
        """
        charts = session.charts
        if not charts:
            return None

        text_lower = text.lower()
        is_modify_or_delete = any(w in text_lower for w in [
            "change chart", "modify chart", "delete chart", "remove chart", 
            "that chart", "the chart", "charcha chart", "chart badla", "chart hatao"
        ])

        # If user explicitly selected a chart, there is no ambiguity
        if session.selected_chart_id:
            return None

        # If only 1 chart exists, there is no ambiguity
        if len(charts) == 1:
            return None

        # If text specifically says "change that chart" without naming the chart or metric
        if ("that chart" in text_lower or "the chart" in text_lower or "chart ko" in text_lower) and not any(c.title.lower() in text_lower for c in charts):
            # Check if previous context gives an unambiguous recent chart
            if not session.last_modified_chart_id:
                chart_titles = [f"{c.title} (ID: {c.id})" for c in charts]
                return ClarificationQuestion(
                    question="Which chart would you like to modify?",
                    parameter_needed="target_chart",
                    options=chart_titles,
                    original_intent="MODIFY_CHART",
                    partial_entities={"raw_command": text}
                )

        return None

    @classmethod
    def check_metric_ambiguity(cls, text: str, session: SessionData, available_metrics: List[str]) -> Optional[ClarificationQuestion]:
        """
        Detects if command requests an operation like top 5, aggregation, or comparison, but metric is missing.
        """
        text_lower = text.lower()
        
        # Check if text asks for top N or bottom N without any metric
        has_top_n = any(w in text_lower for w in ["top 5", "top 10", "top five", "top three", "top ten", "sabse jyada", "sarvat jast"])
        has_any_metric = any(m.lower() in text_lower for m in available_metrics)

        if has_top_n and not has_any_metric:
            return ClarificationQuestion(
                question=f"Top 5 based on which metric: {', '.join(available_metrics[:4])}?",
                parameter_needed="metric_col",
                options=available_metrics[:5],
                original_intent="SHOW_TOP_N",
                partial_entities={"top_n": 5, "raw_command": text}
            )

        # Check if user says "calculate average" or "show total" without a metric
        is_bare_calc = any(text_lower.strip() == w for w in [
            "show total", "total dikhao", "ekun dakhva", 
            "calculate average", "average dikhao", "ausat nikalo", "sarasari kadha"
        ])
        if is_bare_calc and not has_any_metric:
            return ClarificationQuestion(
                question="Which metric would you like to calculate?",
                parameter_needed="metric_col",
                options=available_metrics[:5],
                original_intent="CREATE_KPI",
                partial_entities={"raw_command": text}
            )

        return None

    @classmethod
    def resolve_clarification(cls, session: SessionData, answer: str) -> Tuple[str, Dict[str, Any]]:
        """
        Merges clarification response into pending command.
        """
        pending = session.pending_clarification
        if not pending:
            return "", {}

        answer_clean = answer.strip()
        merged_entities = dict(pending.partial_entities)

        if pending.parameter_needed == "target_chart":
            # Extract chart ID if present in options like "Title (ID: chart_1)"
            target_id = None
            for chart in session.charts:
                if chart.id.lower() in answer_clean.lower() or chart.title.lower() in answer_clean.lower():
                    target_id = chart.id
                    break
            merged_entities["target_chart_id"] = target_id or session.charts[0].id
        elif pending.parameter_needed == "metric_col":
            merged_entities["metric_col"] = answer_clean

        original_intent = pending.original_intent
        # Clear pending clarification
        session.pending_clarification = None
        return original_intent, merged_entities

ambiguity_service = AmbiguityService()
