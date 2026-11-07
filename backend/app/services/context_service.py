import re
from typing import Optional, List, Dict, Any, Tuple
from app.models.schemas import ChartConfig, KPIConfig
from app.services.session_service import SessionData

class ContextService:
    PRONOUN_TOKENS = [
        "it", "that", "this", "the chart", "that chart", "this chart", "previous chart", "last chart",
        "chart ko", "chart la", "use", "usse", "isse", "isko", "usko",
        "त्याला", "तो", "ते", "हा", "याला", "त्या", "त्या चार्टला", "तो चार्ट"
    ]

    @classmethod
    def resolve_target_chart(cls, text: str, session: SessionData) -> Tuple[Optional[ChartConfig], bool]:
        """
        Resolves which chart the user is referring to.
        Returns: (resolved_chart, is_explicitly_referenced_or_pronoun)
        """
        charts = session.charts
        if not charts:
            return None, False

        text_lower = text.lower().strip()

        # 1. Check for specific chart ID or exact title match
        for chart in charts:
            if chart.id.lower() in text_lower:
                return chart, True
            if chart.title.lower() in text_lower:
                return chart, True

        # 2. Check for chart referenced by metric or category mention
        # e.g., "sales chart", "profit chart", "region chart"
        matching_by_title_keyword = []
        for chart in charts:
            # Check if chart's y_col or x_col or words in title are mentioned
            keywords = []
            if chart.y_col:
                keywords.append(chart.y_col.lower())
            if chart.x_col:
                keywords.append(chart.x_col.lower())
            if chart.chart_type:
                keywords.append(chart.chart_type.lower())

            for kw in keywords:
                if len(kw) > 3 and kw in text_lower:
                    matching_by_title_keyword.append(chart)
                    break

        if len(matching_by_title_keyword) == 1:
            return matching_by_title_keyword[0], True
        elif len(matching_by_title_keyword) > 1:
            # Multiple charts match the keyword (e.g. both are sales charts)
            # Check if active/selected matches
            if session.selected_chart_id:
                for c in matching_by_title_keyword:
                    if c.id == session.selected_chart_id:
                        return c, True
            return None, True  # Ambiguous!

        # 3. Check for pronoun reference ("it", "that chart", "use", "tyala", etc.)
        has_pronoun = any(re.search(r'\b' + re.escape(p) + r'\b', text_lower) for p in cls.PRONOUN_TOKENS)
        
        # Or words like "change to pie chart", "modify to line chart" without naming a chart
        is_implicit_reference = has_pronoun or any(w in text_lower for w in ["change to", "badla", "badlo", "convert to", "switch to"])

        if is_implicit_reference:
            # If user currently clicked/selected a chart
            if session.selected_chart_id:
                for c in charts:
                    if c.id == session.selected_chart_id:
                        return c, True

            # If a chart was recently modified or created
            if session.last_modified_chart_id:
                for c in charts:
                    if c.id == session.last_modified_chart_id:
                        return c, True

            # If only 1 chart exists on the entire dashboard, it MUST be that one!
            if len(charts) == 1:
                return charts[0], True

            # If multiple charts exist, the most recent one is the natural antecedent
            return charts[-1], True

        # If user didn't specify and there is only 1 chart, return it
        if len(charts) == 1:
            return charts[0], False

        return None, False

    @classmethod
    def record_turn(cls, session: SessionData, user_command: str, system_response: str, intent: str, affected_id: Optional[str] = None):
        session.command_history.append({
            "user_command": user_command,
            "system_response": system_response,
            "intent": intent,
            "affected_id": affected_id,
            "charts_count": len(session.charts),
            "kpis_count": len(session.kpis)
        })
        if affected_id:
            session.last_modified_chart_id = affected_id

context_service = ContextService()
