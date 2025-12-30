from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from .. import models, database
from ..deps.roles import require_role
from datetime import datetime, timedelta

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
    dependencies=[Depends(require_role("admin"))]
)

@router.get("/overview")
def get_overview_stats(db: Session = Depends(database.get_db)):
    total_reports = db.query(func.count(models.Report.report_id)).scalar()
    resolved_count = db.query(func.count(models.Report.report_id)).filter(models.Report.status == "resolved").scalar()
    
    # Calculate Average Resolution Time
    avg_resolution_hours = 0.0
    
    # Query: AVG(updated_at - created_at) for resolved reports
    # Note: This assumes updated_at is when it was resolved. 
    result = db.query(
        func.avg(
            func.extract('epoch', models.Report.updated_at - models.Report.created_at)
        )
    ).filter(models.Report.status == "resolved").scalar()
    
    if result:
        avg_resolution_hours = round(float(result) / 3600.0, 1) # Convert seconds to hours
        
    return {
        "total_reports": total_reports,
        "resolved_count": resolved_count,
        "avg_resolution_hours": avg_resolution_hours
    }

@router.get("/time-series")
def get_time_series(db: Session = Depends(database.get_db)):
    # Last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    # Group by date
    results = db.query(
        func.date(models.Report.created_at).label('date'),
        func.count(models.Report.report_id).label('count')
    ).filter(
        models.Report.created_at >= thirty_days_ago
    ).group_by(
        func.date(models.Report.created_at)
    ).order_by(
        func.date(models.Report.created_at)
    ).all()
    
    return [{"date": str(r.date), "count": r.count} for r in results]

@router.get("/categories")
def get_category_distribution(db: Session = Depends(database.get_db)):
    results = db.query(
        models.Report.category,
        func.count(models.Report.report_id).label('count')
    ).group_by(
        models.Report.category
    ).all()
    
    return [{"name": r.category, "value": r.count} for r in results]
