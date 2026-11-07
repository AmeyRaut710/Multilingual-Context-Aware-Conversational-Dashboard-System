from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Response
from fastapi.responses import JSONResponse, Response
from typing import Optional, List, Any
import json
from app.models.schemas import (
    DashboardState, CommandRequest, CommandResponse, NewProjectRequest,
    SelectSheetRequest, FilterUpdateRequest, ClearFilterRequest,
    ChartUpdateRequest, ChartDeleteRequest, KPIDeleteRequest,
    DataTableRequest, DataTableResponse
)
from app.services.session_service import session_manager
from app.services.dataset_service import dataset_service
from app.services.dashboard_service import dashboard_service
from app.services.export_service import export_service
from app.services.speech_service import speech_service

router = APIRouter(prefix="/api")

@router.get("/health")
def health_check():
    return {"status": "healthy", "service": "Multilingual Dashboard System", "version": "1.0.0"}

@router.get("/speech/status")
def speech_status():
    return speech_service.get_status()

@router.post("/project/new")
def new_project(req: NewProjectRequest):
    session = session_manager.create_session(req.project_name)
    return {
        "success": True,
        "session_id": session.session_id,
        "project_name": session.project_name,
        "state": session.to_dashboard_state()
    }

@router.post("/project/upload")
async def upload_project_zip(file: UploadFile = File(...)):
    """Uploads and restores a previously exported ZIP project."""
    session = session_manager.create_session("Restoring Project...")
    contents = await file.read()
    
    success, msg = export_service.restore_from_zip(contents, session)
    if not success:
        session_manager.clear_session(session.session_id)
        raise HTTPException(status_code=400, detail=msg)

    return {
        "success": True,
        "message": msg,
        "session_id": session.session_id,
        "state": session.to_dashboard_state()
    }

@router.post("/dataset/upload")
async def upload_dataset(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired.")

    file_bytes = await file.read()
    filename = file.filename or "dataset.csv"

    try:
        meta = dataset_service.process_file_bytes(file_bytes, filename, session)
        # Clear previous charts/kpis when a brand new dataset is loaded
        session.charts = []
        session.kpis = []
        session.filters = []
        session.active_filters = {}
        session.selected_chart_id = None
        session.last_modified_chart_id = None

        return {
            "success": True,
            "message": f"Successfully loaded dataset '{filename}' with {meta.total_rows} rows and {meta.total_columns} columns.",
            "metadata": meta,
            "state": session.to_dashboard_state()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")

@router.post("/dataset/sheet")
def select_sheet(req: SelectSheetRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    try:
        meta = dataset_service.switch_sheet(session, req.sheet_name)
        return {
            "success": True,
            "message": f"Switched to worksheet '{req.sheet_name}'.",
            "metadata": meta,
            "state": session.to_dashboard_state()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dataset/preview")
def get_preview(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session or not session.dataset_meta:
        raise HTTPException(status_code=404, detail="No dataset uploaded in this session.")
    return session.dataset_meta

@router.get("/dataset/columns")
def get_columns(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session or not session.dataset_meta:
        raise HTTPException(status_code=404, detail="No dataset uploaded.")
    return {"columns": session.dataset_meta.columns}

@router.post("/dataset/table", response_model=DataTableResponse)
def get_dataset_table(req: DataTableRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    try:
        return dataset_service.get_paginated_table(
            session=session,
            page=req.page,
            page_size=req.page_size,
            search=req.search,
            sort_by=req.sort_by,
            sort_order=req.sort_order,
            column_filters=req.column_filters,
            use_dashboard_filters=req.use_dashboard_filters
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/dataset/table", response_model=DataTableResponse)
def get_dataset_table_query(
    session_id: str = Query(...),
    page: int = Query(1),
    page_size: int = Query(100),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: Optional[str] = Query("asc"),
    column_filters: Optional[str] = Query(None),  # JSON string
    use_dashboard_filters: bool = Query(True)
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    parsed_filters = None
    if column_filters:
        try:
            parsed_filters = json.loads(column_filters)
        except Exception:
            pass

    try:
        return dataset_service.get_paginated_table(
            session=session,
            page=page,
            page_size=page_size,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
            column_filters=parsed_filters,
            use_dashboard_filters=use_dashboard_filters
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/command/process", response_model=CommandResponse)
def process_command(req: CommandRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    
    return dashboard_service.process_command(session, req.command)

@router.post("/command/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    contents = await file.read()
    success, text, details = speech_service.transcribe_audio_bytes(contents, file.filename or "audio.wav")
    return {
        "success": success,
        "text": text,
        "details": details
    }

@router.post("/dashboard/chart/create")
def manual_create_chart(
    session_id: str = Form(...),
    chart_type: str = Form("bar"),
    x_col: Optional[str] = Form(None),
    y_col: Optional[str] = Form(None),
    agg: str = Form("sum"),
    top_n: Optional[int] = Form(None),
    title: Optional[str] = Form(None)
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    success, msg, chart = dashboard_service.create_chart(
        session, chart_type, x_col, y_col, agg=agg, top_n=top_n, title=title
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.post("/dashboard/chart/update")
def manual_update_chart(req: ChartUpdateRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    success, msg = dashboard_service.update_chart(
        session, req.chart_id, new_type=req.chart_type, new_title=req.title,
        new_agg=req.agg, new_top_n=req.top_n
    )
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.post("/dashboard/chart/delete")
def manual_delete_chart(req: ChartDeleteRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    success, msg = dashboard_service.delete_chart(session, req.chart_id)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.post("/dashboard/kpi/create")
def manual_create_kpi(
    session_id: str = Form(...),
    metric_col: str = Form(...),
    agg: str = Form("sum"),
    title: Optional[str] = Form(None)
):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    success, msg, kpi = dashboard_service.create_kpi(session, metric_col, agg, title)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.post("/dashboard/kpi/delete")
def manual_delete_kpi(req: KPIDeleteRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    session.kpis = [k for k in session.kpis if k.id != req.kpi_id]
    return {"success": True, "message": "KPI deleted.", "state": session.to_dashboard_state()}

@router.post("/dashboard/filter")
def update_filter(req: FilterUpdateRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    success, msg = dashboard_service.apply_filter(session, req.column, req.value)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.post("/dashboard/filter/clear")
def clear_filter(req: ClearFilterRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    success, msg = dashboard_service.clear_filter(session, req.column)
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.post("/dashboard/filter/remove")
def remove_slicer(req: ClearFilterRequest):
    session = session_manager.get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    if req.column:
        success, msg = dashboard_service.remove_slicer(session, req.column)
    else:
        success, msg = dashboard_service.clear_filter(session)
    return {"success": True, "message": msg, "state": session.to_dashboard_state()}

@router.get("/dashboard/state")
def get_state(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return session.to_dashboard_state()

@router.get("/project/export/zip")
def export_zip(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    zip_bytes = export_service.generate_zip_export(session)
    safe_name = session.project_name.lower().replace(" ", "_")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_export.zip"'}
    )

@router.get("/project/export/html")
def export_html(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    html_content = export_service.generate_standalone_html(session)
    safe_name = session.project_name.lower().replace(" ", "_")
    return Response(
        content=html_content,
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_dashboard.html"'}
    )

@router.get("/project/export/pdf")
def export_pdf(session_id: str = Query(...)):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    pdf_bytes = export_service.generate_pdf_report(session)
    safe_name = session.project_name.lower().replace(" ", "_")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_report.pdf"'}
    )

@router.delete("/session/clear")
def clear_workspace(session_id: str = Query(...)):
    success = session_manager.clear_session(session_id)
    return {"success": success, "message": "Session and temporary workspace cleared."}

