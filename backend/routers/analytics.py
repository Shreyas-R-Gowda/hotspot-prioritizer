from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func
from sqlalchemy.future import select
from database import get_db
from models import User, UserRole, Report, ReportStatus, ReportPriority
from routers.auth import get_current_user
from typing import List, Dict, Optional
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/status-distribution")
async def get_status_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of reports by status"""
    query = select(
        Report.status,
        func.count(Report.id).label('count')
    ).group_by(Report.status)
    
    result = await db.execute(query)
    rows = result.all()
    
    distribution = {row.status.value: row.count for row in rows}
    
    return {"status_distribution": distribution}

@router.get("/priority-distribution")
async def get_priority_distribution(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get count of reports by priority"""
    query = select(
        Report.priority,
        func.count(Report.id).label('count')
    ).group_by(Report.priority)
    
    result = await db.execute(query)
    rows = result.all()
    
    distribution = {row.priority.value: row.count for row in rows}
    
    return {"priority_distribution": distribution}

@router.get("/time-bound-stats")
async def get_time_bound_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get resolution statistics within time bounds
    Categories: < 24h, < 7d, < 30d, > 30d
    """
    # Query for resolved/closed reports with resolution time
    query = text("""
        SELECT 
            CASE
                WHEN updated_at - created_at < INTERVAL '1 day' THEN 'under_24h'
                WHEN updated_at - created_at < INTERVAL '7 days' THEN 'under_7d'
                WHEN updated_at - created_at < INTERVAL '30 days' THEN 'under_30d'
                ELSE 'over_30d'
            END as time_category,
            COUNT(*) as count
        FROM reports
        WHERE status IN ('resolved', 'closed')
        AND updated_at IS NOT NULL
        GROUP BY time_category
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    stats = {row.time_category: row.count for row in rows}
    
    # Ensure all categories exist
    for category in ['under_24h', 'under_7d', 'under_30d', 'over_30d']:
        if category not in stats:
            stats[category] = 0
    
    return {"time_bound_stats": stats}

@router.get("/heatmap-data")
async def get_heatmap_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None,
    priority: Optional[str] = None
):
    """
    Get geographic data for heatmap visualization
    Returns lat/lon coordinates with intensity (report count)
    """
    # Build query with optional filters
    conditions = []
    if status:
        conditions.append(f"status = '{status}'")
    if priority:
        conditions.append(f"priority = '{priority}'")
    
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    query = text(f"""
        SELECT 
            ST_Y(location::geometry) as latitude,
            ST_X(location::geometry) as longitude,
            COUNT(*) as intensity,
            priority,
            status
        FROM reports
        {where_clause}
        GROUP BY ST_Y(location::geometry), ST_X(location::geometry), priority, status
        ORDER BY intensity DESC
        LIMIT 500
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    heatmap_points = [
        {
            "latitude": row.latitude,
            "longitude": row.longitude,
            "intensity": row.intensity,
            "priority": row.priority,
            "status": row.status
        }
        for row in rows
    ]
    
    return {"heatmap_data": heatmap_points}

@router.get("/trend-analysis")
async def get_trend_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    days: int = Query(30, description="Number of days to analyze")
):
    """Get report trends over time"""
    query = text(f"""
        SELECT 
            DATE(created_at) as date,
            COUNT(*) as count,
            status
        FROM reports
        WHERE created_at >= NOW() - INTERVAL '{days} days'
        GROUP BY DATE(created_at), status
        ORDER BY date DESC
    """)
    
    result = await db.execute(query)
    rows = result.all()
    
    # Group by date
    trends = {}
    for row in rows:
        date_str = row.date.isoformat()
        if date_str not in trends:
            trends[date_str] = {}
        trends[date_str][row.status] = row.count
    
    return {"trend_data": trends, "days": days}

@router.get("/predictive-maintenance")
async def predictive_maintenance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Identify hotspots for predictive maintenance.
    Aggregates reports by location and category to find recurring issues.
    """
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Query to find clusters of reports
    query = text("""
        SELECT 
            category,
            COUNT(*) as count,
            AVG(ST_X(location::geometry)) as avg_lon,
            AVG(ST_Y(location::geometry)) as avg_lat,
            priority
        FROM reports
        WHERE created_at > NOW() - INTERVAL '30 days'
        GROUP BY category, priority
        HAVING COUNT(*) > 2
        ORDER BY count DESC, priority DESC
    """)
    
    result = await db.execute(query)
    hotspots = []
    for row in result:
        hotspots.append({
            "category": row.category,
            "report_count": row.count,
            "location": {"lat": row.avg_lat, "lon": row.avg_lon},
            "priority": row.priority,
            "recommendation": f"Schedule maintenance for {row.category} in this area."
        })
        
    return {"hotspots": hotspots}

@router.get("/summary")
async def get_summary_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get overall summary statistics"""
    # Total reports
    total_query = select(func.count(Report.id))
    total_result = await db.execute(total_query)
    total_reports = total_result.scalar()
    
    # Pending reports
    pending_query = select(func.count(Report.id)).where(Report.status == ReportStatus.pending)
    pending_result = await db.execute(pending_query)
    pending_reports = pending_result.scalar()
    
    # Resolved reports
    resolved_query = select(func.count(Report.id)).where(Report.status.in_([ReportStatus.resolved, ReportStatus.closed]))
    resolved_result = await db.execute(resolved_query)
    resolved_reports = resolved_result.scalar()
    
    # Critical priority reports
    critical_query = select(func.count(Report.id)).where(Report.priority == ReportPriority.critical)
    critical_result = await db.execute(critical_query)
    critical_reports = critical_result.scalar()
    
    return {
        "total_reports": total_reports,
        "pending_reports": pending_reports,
        "resolved_reports": resolved_reports,
        "critical_reports": critical_reports,
        "resolution_rate": (resolved_reports / total_reports * 100) if total_reports > 0 else 0
    }
