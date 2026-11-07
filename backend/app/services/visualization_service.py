import json
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

# Professional modern color palettes
PALETTE = [
    "#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", 
    "#8b5cf6", "#ec4899", "#14b8a6", "#f97316", "#6366f1"
]

class VisualizationService:
    @staticmethod
    def get_base_layout(title: str, x_title: str = "", y_title: str = "") -> Dict[str, Any]:
        return {
            "title": {
                "text": title,
                "font": {"family": "Inter, system-ui, sans-serif", "size": 16, "color": "#1e293b"},
                "x": 0.05,
                "xanchor": "left"
            },
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "autosize": True,
            "margin": {"l": 50, "r": 30, "t": 60, "b": 50},
            "xaxis": {
                "title": {"text": x_title, "font": {"size": 12, "color": "#64748b"}},
                "gridcolor": "#f1f5f9",
                "zerolinecolor": "#e2e8f0",
                "tickfont": {"size": 11, "color": "#64748b"}
            },
            "yaxis": {
                "title": {"text": y_title, "font": {"size": 12, "color": "#64748b"}},
                "gridcolor": "#f1f5f9",
                "zerolinecolor": "#e2e8f0",
                "tickfont": {"size": 11, "color": "#64748b"}
            },
            "hoverlabel": {
                "bgcolor": "#1e293b",
                "font": {"family": "Inter, sans-serif", "color": "#ffffff"}
            },
            "legend": {
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
                "font": {"size": 11, "color": "#475569"}
            }
        }

    @classmethod
    def generate_chart_spec(cls,
                            df: pd.DataFrame,
                            chart_type: str,
                            x_col: Optional[str],
                            y_col: Optional[str],
                            color_col: Optional[str] = None,
                            agg: str = "sum",
                            top_n: Optional[int] = None,
                            sort_order: Optional[str] = "desc",
                            time_group: Optional[str] = None,
                            title: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes data transformation and outputs complete Plotly JSON spec.
        """
        if df.empty:
            return {
                "data": [],
                "layout": cls.get_base_layout(title or "No Data Available")
            }

        chart_type = chart_type.lower()
        if not title:
            title = f"{y_col or 'Count'} by {x_col or 'Category'}"

        # 1. Handle Time Grouping if specified on x_col
        work_df = df.copy()
        if time_group and x_col and x_col in work_df.columns:
            work_df[x_col] = pd.to_datetime(work_df[x_col], errors="coerce", format="mixed")
            work_df = work_df.dropna(subset=[x_col])
            if time_group == "month":
                work_df["_time_period"] = work_df[x_col].dt.strftime("%Y-%m")
            elif time_group == "year":
                work_df["_time_period"] = work_df[x_col].dt.strftime("%Y")
            elif time_group == "quarter":
                work_df["_time_period"] = work_df[x_col].dt.to_period("Q").astype(str)
            else:
                work_df["_time_period"] = work_df[x_col].dt.strftime("%Y-%m-%d")
            plot_x = "_time_period"
        else:
            plot_x = x_col

        # 2. Aggregations & Slicing
        # Map agg string to pandas agg
        agg_func = "sum" if agg == "sum" else ("mean" if agg == "avg" else ("count" if agg == "count" else ("min" if agg == "min" else "max")))

        # --- A. BAR / HORIZONTAL BAR CHART ---
        if chart_type in ["bar", "horizontal_bar"]:
            if plot_x and y_col and y_col in work_df.columns:
                grouped = work_df.groupby(plot_x)[y_col].agg(agg_func).reset_index()
                if sort_order == "desc":
                    grouped = grouped.sort_values(by=y_col, ascending=False)
                elif sort_order == "asc":
                    grouped = grouped.sort_values(by=y_col, ascending=True)
                
                if top_n and top_n > 0:
                    grouped = grouped.head(top_n)

                if chart_type == "horizontal_bar":
                    grouped = grouped.sort_values(by=y_col, ascending=True)  # horizontal bars look natural bottom-to-top
                    trace = {
                        "type": "bar",
                        "x": grouped[y_col].round(2).tolist(),
                        "y": grouped[plot_x].astype(str).tolist(),
                        "orientation": "h",
                        "marker": {"color": PALETTE[0], "line": {"width": 0}},
                        "hovertemplate": f"{plot_x}: %{{y}}<br>{y_col}: %{{x:,.2f}}<extra></extra>"
                    }
                    layout = cls.get_base_layout(title, x_title=f"{agg.title()} of {y_col}", y_title=plot_x)
                else:
                    trace = {
                        "type": "bar",
                        "x": grouped[plot_x].astype(str).tolist(),
                        "y": grouped[y_col].round(2).tolist(),
                        "marker": {"color": PALETTE[0], "line": {"width": 0}},
                        "hovertemplate": f"{plot_x}: %{{x}}<br>{y_col}: %{{y:,.2f}}<extra></extra>"
                    }
                    layout = cls.get_base_layout(title, x_title=plot_x, y_title=f"{agg.title()} of {y_col}")
            else:
                # Count by category
                grouped = work_df[plot_x].value_counts().reset_index()
                grouped.columns = [plot_x, "Count"]
                if top_n:
                    grouped = grouped.head(top_n)
                trace = {
                    "type": "bar",
                    "x": grouped[plot_x].astype(str).tolist(),
                    "y": grouped["Count"].tolist(),
                    "marker": {"color": PALETTE[0]},
                    "hovertemplate": f"{plot_x}: %{{x}}<br>Count: %{{y}}<extra></extra>"
                }
                layout = cls.get_base_layout(title, x_title=plot_x, y_title="Count")

            return {"data": [trace], "layout": layout}

        # --- B. LINE / AREA CHART ---
        elif chart_type in ["line", "area"]:
            if plot_x and y_col and y_col in work_df.columns:
                grouped = work_df.groupby(plot_x)[y_col].agg(agg_func).reset_index()
                grouped = grouped.sort_values(by=plot_x)
                trace = {
                    "type": "scatter",
                    "mode": "lines+markers",
                    "x": grouped[plot_x].astype(str).tolist(),
                    "y": grouped[y_col].round(2).tolist(),
                    "line": {"color": PALETTE[0], "width": 3, "shape": "spline"},
                    "marker": {"size": 6, "color": PALETTE[0]},
                    "hovertemplate": f"{plot_x}: %{{x}}<br>{y_col}: %{{y:,.2f}}<extra></extra>"
                }
                if chart_type == "area":
                    trace["fill"] = "tozeroy"
                    trace["fillcolor"] = "rgba(79, 70, 229, 0.15)"
                
                layout = cls.get_base_layout(title, x_title=plot_x, y_title=f"{agg.title()} of {y_col}")
                return {"data": [trace], "layout": layout}

        # --- C. PIE / DONUT CHART ---
        elif chart_type in ["pie", "donut"]:
            if plot_x:
                if y_col and y_col in work_df.columns:
                    grouped = work_df.groupby(plot_x)[y_col].agg(agg_func).reset_index()
                    if top_n:
                        grouped = grouped.sort_values(by=y_col, ascending=False).head(top_n)
                    labels = grouped[plot_x].astype(str).tolist()
                    values = grouped[y_col].round(2).tolist()
                else:
                    counts = work_df[plot_x].value_counts()
                    if top_n:
                        counts = counts.head(top_n)
                    labels = counts.index.astype(str).tolist()
                    values = counts.values.tolist()

                trace = {
                    "type": "pie",
                    "labels": labels,
                    "values": values,
                    "hole": 0.55 if chart_type == "donut" else 0.0,
                    "marker": {"colors": PALETTE},
                    "textinfo": "label+percent",
                    "textposition": "inside",
                    "hovertemplate": "<b>%{label}</b><br>Value: %{value:,.2f}<br>Share: %{percent}<extra></extra>"
                }
                layout = cls.get_base_layout(title)
                layout["showlegend"] = True
                return {"data": [trace], "layout": layout}

        # --- D. SCATTER PLOT ---
        elif chart_type == "scatter":
            if x_col and y_col and x_col in work_df.columns and y_col in work_df.columns:
                traces = []
                if color_col and color_col in work_df.columns:
                    for idx, (cat, group) in enumerate(work_df.groupby(color_col)):
                        traces.append({
                            "type": "scatter",
                            "mode": "markers",
                            "name": str(cat),
                            "x": group[x_col].tolist(),
                            "y": group[y_col].tolist(),
                            "marker": {"color": PALETTE[idx % len(PALETTE)], "size": 8, "opacity": 0.8},
                            "hovertemplate": f"<b>{cat}</b><br>{x_col}: %{{x:,.2f}}<br>{y_col}: %{{y:,.2f}}<extra></extra>"
                        })
                else:
                    traces.append({
                        "type": "scatter",
                        "mode": "markers",
                        "x": work_df[x_col].tolist(),
                        "y": work_df[y_col].tolist(),
                        "marker": {"color": PALETTE[0], "size": 8, "opacity": 0.8},
                        "hovertemplate": f"{x_col}: %{{x:,.2f}}<br>{y_col}: %{{y:,.2f}}<extra></extra>"
                    })
                layout = cls.get_base_layout(title, x_title=x_col, y_title=y_col)
                return {"data": traces, "layout": layout}

        # --- E. HISTOGRAM ---
        elif chart_type == "histogram":
            target_col = y_col or x_col
            if target_col and target_col in work_df.columns:
                trace = {
                    "type": "histogram",
                    "x": work_df[target_col].dropna().tolist(),
                    "marker": {"color": PALETTE[1], "line": {"color": "#ffffff", "width": 1}},
                    "hovertemplate": f"{target_col}: %{{x}}<br>Frequency: %{{y}}<extra></extra>"
                }
                layout = cls.get_base_layout(title, x_title=target_col, y_title="Frequency")
                return {"data": [trace], "layout": layout}

        # --- F. BOX PLOT ---
        elif chart_type == "box":
            val_col = y_col or x_col
            group_col = x_col if y_col else None
            traces = []
            if group_col and group_col in work_df.columns and val_col:
                for idx, (grp_name, grp_data) in enumerate(work_df.groupby(group_col)):
                    traces.append({
                        "type": "box",
                        "name": str(grp_name),
                        "y": grp_data[val_col].dropna().tolist(),
                        "marker": {"color": PALETTE[idx % len(PALETTE)]},
                        "boxpoints": "outliers"
                    })
                layout = cls.get_base_layout(title, x_title=group_col, y_title=val_col)
            elif val_col:
                traces.append({
                    "type": "box",
                    "name": val_col,
                    "y": work_df[val_col].dropna().tolist(),
                    "marker": {"color": PALETTE[0]},
                    "boxpoints": "outliers"
                })
                layout = cls.get_base_layout(title, y_title=val_col)
            return {"data": traces, "layout": layout}

        # --- G. STACKED / GROUPED BAR ---
        elif chart_type in ["stacked_bar", "grouped_bar"]:
            if plot_x and y_col and color_col and color_col in work_df.columns:
                pivot = work_df.pivot_table(index=plot_x, columns=color_col, values=y_col, aggfunc=agg_func).fillna(0)
                traces = []
                for idx, col_name in enumerate(pivot.columns):
                    traces.append({
                        "type": "bar",
                        "name": str(col_name),
                        "x": pivot.index.astype(str).tolist(),
                        "y": pivot[col_name].round(2).tolist(),
                        "marker": {"color": PALETTE[idx % len(PALETTE)]},
                        "hovertemplate": f"{plot_x}: %{{x}}<br>{col_name}: %{{y:,.2f}}<extra></extra>"
                    })
                layout = cls.get_base_layout(title, x_title=plot_x, y_title=f"{agg.title()} of {y_col}")
                layout["barmode"] = "stack" if chart_type == "stacked_bar" else "group"
                return {"data": traces, "layout": layout}

        # --- H. HEATMAP ---
        elif chart_type == "heatmap":
            if plot_x and color_col and y_col:
                pivot = work_df.pivot_table(index=color_col, columns=plot_x, values=y_col, aggfunc=agg_func).fillna(0)
                trace = {
                    "type": "heatmap",
                    "x": pivot.columns.astype(str).tolist(),
                    "y": pivot.index.astype(str).tolist(),
                    "z": pivot.round(2).values.tolist(),
                    "colorscale": "Viridis",
                    "hovertemplate": f"{plot_x}: %{{x}}<br>{color_col}: %{{y}}<br>{y_col}: %{{z:,.2f}}<extra></extra>"
                }
                layout = cls.get_base_layout(title, x_title=plot_x, y_title=color_col)
                return {"data": [trace], "layout": layout}

        # Fallback to simple bar
        grouped = work_df[plot_x or work_df.columns[0]].value_counts().head(10).reset_index()
        trace = {
            "type": "bar",
            "x": grouped.iloc[:, 0].astype(str).tolist(),
            "y": grouped.iloc[:, 1].tolist(),
            "marker": {"color": PALETTE[0]}
        }
        return {"data": [trace], "layout": cls.get_base_layout(title)}

    @classmethod
    def compute_kpi_value(cls, df: pd.DataFrame, metric_col: str, agg: str = "sum") -> Dict[str, Any]:
        """Calculates KPI scalar value, formatted label, and currency/unit symbol."""
        if df.empty or metric_col not in df.columns:
            return {"value": 0.0, "formatted_value": "0", "prefix": "", "suffix": ""}

        series = df[metric_col].dropna()
        agg_lower = agg.lower()

        if agg_lower in ["sum", "total"]:
            val = float(series.sum())
        elif agg_lower in ["avg", "average", "mean"]:
            val = float(series.mean())
        elif agg_lower in ["min", "minimum"]:
            val = float(series.min())
        elif agg_lower in ["max", "maximum"]:
            val = float(series.max())
        elif agg_lower in ["distinct_count", "unique"]:
            val = float(series.nunique())
        else:  # count
            val = float(len(series))

        # Formatting
        prefix = "₹" if any(w in metric_col.lower() for w in ["sales", "profit", "revenue", "price", "cost"]) else ""
        
        if abs(val) >= 1_000_000:
            formatted = f"{val / 1_000_000:.2f}M"
        elif abs(val) >= 1_000:
            formatted = f"{val / 1_000:.2f}K"
        elif float(val).is_integer():
            formatted = f"{int(val):,}"
        else:
            formatted = f"{val:.2f}"

        return {
            "value": round(val, 2),
            "formatted_value": formatted,
            "prefix": prefix,
            "suffix": ""
        }

visualization_service = VisualizationService()
