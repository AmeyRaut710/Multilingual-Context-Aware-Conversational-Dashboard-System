import uuid
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
from app.models.schemas import (
    ChartConfig, KPIConfig, FilterItem, CommandResponse, 
    ClarificationQuestion, DashboardState
)
from app.services.session_service import SessionData, session_manager
from app.services.intent_service import intent_service
from app.services.validation_service import validation_service
from app.services.visualization_service import visualization_service
from app.services.context_service import context_service

class DashboardService:
    @classmethod
    def recompute_all(cls, session: SessionData):
        """
        Recomputes all charts and KPIs using the currently filtered DataFrame.
        """
        filtered_df = session.get_filtered_df()

        # Recompute KPIs
        for kpi in session.kpis:
            res = visualization_service.compute_kpi_value(filtered_df, kpi.metric_col, kpi.agg)
            kpi.value = res["value"]
            kpi.formatted_value = res["formatted_value"]
            kpi.prefix = res["prefix"]

        # Recompute Charts
        for chart in session.charts:
            chart.plotly_spec = visualization_service.generate_chart_spec(
                df=filtered_df,
                chart_type=chart.chart_type,
                x_col=chart.x_col,
                y_col=chart.y_col,
                color_col=chart.color_col,
                agg=chart.agg or "sum",
                top_n=chart.top_n,
                sort_order=chart.sort_order or "desc",
                time_group=chart.time_group,
                title=chart.title
            )

    @classmethod
    def create_chart(cls, session: SessionData, chart_type: str, x_col: Optional[str], y_col: Optional[str],
                     agg: str = "sum", top_n: Optional[int] = None, sort_order: str = "desc", 
                     time_group: Optional[str] = None, title: Optional[str] = None) -> Tuple[bool, str, Optional[ChartConfig]]:
        
        cols = session.dataset_meta.columns if session.dataset_meta else []
        valid, err = validation_service.validate_chart_request(x_col, y_col, chart_type, agg, cols)
        if not valid:
            return False, err or "Invalid chart request.", None

        chart_id = f"chart_{uuid.uuid4().hex[:6]}"
        
        # Build natural title if not provided
        if not title:
            top_str = f"Top {top_n} " if top_n else ""
            if time_group and x_col:
                title = f"{top_str}{agg.title()} of {y_col or 'Data'} by {time_group.title()}"
            elif x_col and y_col:
                title = f"{top_str}{agg.title()} of {y_col} by {x_col}"
            elif x_col:
                title = f"Distribution of {x_col}"
            elif y_col:
                title = f"Distribution of {y_col}"
            else:
                title = f"{chart_type.title()} Chart"

        filtered_df = session.get_filtered_df()
        plotly_spec = visualization_service.generate_chart_spec(
            df=filtered_df,
            chart_type=chart_type,
            x_col=x_col,
            y_col=y_col,
            agg=agg,
            top_n=top_n,
            sort_order=sort_order,
            time_group=time_group,
            title=title
        )

        new_chart = ChartConfig(
            id=chart_id,
            title=title,
            chart_type=chart_type,
            x_col=x_col,
            y_col=y_col,
            agg=agg,
            top_n=top_n,
            sort_order=sort_order,
            time_group=time_group,
            plotly_spec=plotly_spec
        )

        session.charts.append(new_chart)
        session.last_modified_chart_id = chart_id
        session.selected_chart_id = chart_id
        return True, f"Successfully created {chart_type} chart: '{title}'.", new_chart

    @classmethod
    def create_kpi(cls, session: SessionData, metric_col: str, agg: str = "sum", title: Optional[str] = None) -> Tuple[bool, str, Optional[KPIConfig]]:
        cols = session.dataset_meta.columns if session.dataset_meta else []
        valid, err = validation_service.validate_kpi_request(metric_col, agg, cols)
        if not valid:
            return False, err or "Invalid KPI request.", None

        kpi_id = f"kpi_{uuid.uuid4().hex[:6]}"
        if not title:
            title = f"{agg.title()} {metric_col}"

        filtered_df = session.get_filtered_df()
        calc = visualization_service.compute_kpi_value(filtered_df, metric_col, agg)

        kpi = KPIConfig(
            id=kpi_id,
            title=title,
            metric_col=metric_col,
            agg=agg,
            value=calc["value"],
            formatted_value=calc["formatted_value"],
            prefix=calc["prefix"],
            suffix=calc["suffix"]
        )
        session.kpis.append(kpi)
        return True, f"Created KPI card for {title}: {kpi.prefix}{kpi.formatted_value}", kpi

    @classmethod
    def update_chart(cls, session: SessionData, chart_id: str, new_type: Optional[str] = None, 
                     new_title: Optional[str] = None, new_agg: Optional[str] = None,
                     new_top_n: Optional[int] = None) -> Tuple[bool, str]:
        chart = next((c for c in session.charts if c.id == chart_id), None)
        if not chart:
            return False, f"Chart with ID '{chart_id}' was not found."

        if new_type:
            chart.chart_type = new_type
        if new_title:
            chart.title = new_title
        if new_agg:
            chart.agg = new_agg
        if new_top_n is not None:
            chart.top_n = new_top_n

        filtered_df = session.get_filtered_df()
        chart.plotly_spec = visualization_service.generate_chart_spec(
            df=filtered_df,
            chart_type=chart.chart_type,
            x_col=chart.x_col,
            y_col=chart.y_col,
            color_col=chart.color_col,
            agg=chart.agg or "sum",
            top_n=chart.top_n,
            sort_order=chart.sort_order or "desc",
            time_group=chart.time_group,
            title=chart.title
        )
        session.last_modified_chart_id = chart_id
        return True, f"Updated chart '{chart.title}' to {chart.chart_type}."

    @classmethod
    def delete_chart(cls, session: SessionData, chart_id: str) -> Tuple[bool, str]:
        chart = next((c for c in session.charts if c.id == chart_id), None)
        if not chart:
            return False, f"Chart '{chart_id}' not found."
        
        session.charts = [c for c in session.charts if c.id != chart_id]
        if session.last_modified_chart_id == chart_id:
            session.last_modified_chart_id = session.charts[-1].id if session.charts else None
        if session.selected_chart_id == chart_id:
            session.selected_chart_id = None
        return True, f"Chart '{chart.title}' was deleted."

    @classmethod
    def apply_filter(cls, session: SessionData, column: str, value: Any) -> Tuple[bool, str]:
        if session.df_working is None or column not in session.df_working.columns:
            return False, f"Column '{column}' does not exist for filtering."

        session.active_filters[column] = value
        
        # Ensure FilterItem exists in session.filters
        existing_item = next((f for f in session.filters if f.column == column), None)
        col_series = session.df_working[column]
        
        if not existing_item:
            filter_type = "dropdown"
            options = [str(x) for x in col_series.dropna().unique()[:30]]
            session.filters.append(FilterItem(
                id=f"flt_{uuid.uuid4().hex[:6]}",
                column=column,
                filter_type=filter_type,
                options=options,
                current_value=value
            ))
        else:
            existing_item.current_value = value

        cls.recompute_all(session)
        return True, f"Applied filter on '{column}': {value}."

    @classmethod
    def clear_filter(cls, session: SessionData, column: Optional[str] = None) -> Tuple[bool, str]:
        if column:
            if column in session.active_filters:
                del session.active_filters[column]
            for f in session.filters:
                if f.column == column:
                    f.current_value = None
            msg = f"Cleared filter on '{column}'."
        else:
            session.active_filters = {}
            for f in session.filters:
                f.current_value = None
            msg = "Cleared all dashboard filters."

        cls.recompute_all(session)
        return True, msg

    @classmethod
    def process_command(cls, session: SessionData, command: str) -> CommandResponse:
        """
        Main entry point for conversational commands.
        """
        if not session.df_working is not None and not session.excel_sheets:
            return CommandResponse(
                success=False,
                detected_language="English",
                intent="ERROR",
                message="Please upload a dataset before giving dashboard commands.",
                error_details="No active dataset in session."
            )

        parse_result = intent_service.parse_command(command, session)
        intent = parse_result["intent"]
        lang = parse_result.get("language", "English")

        # 1. Ambiguity handling
        if intent == "AMBIGUOUS":
            clarification = parse_result["clarification"]
            context_service.record_turn(session, command, clarification.question, intent)
            return CommandResponse(
                success=True,
                detected_language=lang,
                intent=intent,
                message=clarification.question,
                requires_clarification=True,
                clarification=clarification,
                updated_state=session.to_dashboard_state()
            )

        entities = parse_result.get("entities", {})
        affected_id = None
        success = True
        msg = ""

        # 2. Execute intent
        if intent in ["CREATE_CHART", "SHOW_TOP_N", "COMPARE_VALUES"]:
            chart_type = entities.get("chart_type", "horizontal_bar" if intent == "SHOW_TOP_N" else "bar")
            x_col = entities.get("x_col")
            y_col = entities.get("y_col") or entities.get("metric_col")
            agg = entities.get("agg", "sum")
            top_n = entities.get("top_n")
            sort_order = entities.get("sort_order", "desc")
            time_group = entities.get("time_group")

            # Default sensible picks if user just said e.g. "banao chart" or answered clarification
            if not x_col and not y_col:
                cats = validation_service.get_categorical_columns(session.dataset_meta.columns)
                nums = validation_service.get_numeric_columns(session.dataset_meta.columns)
                x_col = cats[0].name if cats else session.df_working.columns[0]
                y_col = nums[0].name if nums else None
            elif not x_col and y_col:
                # Pick a categorical column for dimension
                cats = validation_service.get_categorical_columns(session.dataset_meta.columns)
                x_col = cats[0].name if cats else session.df_working.columns[0]
            elif x_col and not y_col:
                nums = validation_service.get_numeric_columns(session.dataset_meta.columns)
                y_col = nums[0].name if nums else None

            success, msg, chart_obj = cls.create_chart(
                session, chart_type, x_col, y_col, agg, top_n, sort_order, time_group
            )
            if success and chart_obj:
                affected_id = chart_obj.id

        elif intent == "CHANGE_CHART_TYPE":
            target_id = entities.get("target_chart_id")
            new_type = entities.get("chart_type")
            if not target_id:
                success = False
                msg = "No existing chart was found to modify. Create a chart first."
            else:
                success, msg = cls.update_chart(session, target_id, new_type=new_type)
                affected_id = target_id

        elif intent == "DELETE_CHART":
            target_id = entities.get("target_chart_id")
            if not target_id:
                success = False
                msg = "Could not identify which chart to delete. Please select or specify the chart."
            else:
                success, msg = cls.delete_chart(session, target_id)
                affected_id = target_id

        elif intent == "CREATE_KPI":
            metric_col = entities.get("metric_col")
            agg = entities.get("agg", "sum")
            success, msg, kpi_obj = cls.create_kpi(session, metric_col, agg)
            if success and kpi_obj:
                affected_id = kpi_obj.id

        elif intent == "APPLY_FILTER":
            col = entities.get("column")
            top_n = entities.get("top_n")
            target_chart_id = entities.get("target_chart_id")

            if target_chart_id and top_n:
                # Apply top_n specifically to target chart
                success, msg = cls.update_chart(session, target_chart_id, new_top_n=top_n)
                affected_id = target_chart_id
            elif col:
                # User wants a filter control
                success, msg = cls.apply_filter(session, col, entities.get("value", "All"))
            else:
                success = False
                msg = "Please specify which category or column to filter."

        elif intent == "REMOVE_FILTER":
            success, msg = cls.clear_filter(session)

        elif intent == "CLEAR_WORKSPACE":
            session.charts = []
            session.kpis = []
            session.filters = []
            session.active_filters = {}
            session.selected_chart_id = None
            session.last_modified_chart_id = None
            success = True
            msg = "Workspace cleared. All charts, KPIs, and filters have been reset."

        elif intent == "EXPORT_DASHBOARD":
            fmt = entities.get("format", "zip")
            success = True
            msg = f"Ready to export dashboard in {fmt.upper()} format. Please click the Export button or use the download link."

        elif intent == "ASK_QUESTION":
            success = True
            total_rows = len(session.df_working)
            total_cols = len(session.df_working.columns)
            msg = (
                f"The active dataset has {total_rows} rows and {total_cols} columns: "
                f"{', '.join(session.df_working.columns[:6])}... "
                f"You can ask me to create charts, add KPIs, apply filters, or compare metrics in English, Hindi, or Marathi."
            )

        context_service.record_turn(session, command, msg, intent, affected_id)

        return CommandResponse(
            success=success,
            detected_language=lang,
            intent=intent,
            message=msg,
            entities=entities,
            updated_state=session.to_dashboard_state(),
            error_details=None if success else msg
        )

dashboard_service = DashboardService()
