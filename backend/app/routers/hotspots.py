from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.shape import from_shape
from .. import models, database
import csv
from fastapi.responses import StreamingResponse
import io

router = APIRouter(
    prefix="/hotspots",
    tags=["hotspots"]
)

from typing import Union, List, Dict, Any

@router.get("/", response_model=Union[List[Dict[str, Any]], Dict[str, Any]])
def get_hotspots(
    method: str = "kmeans",
    k: int = 5,
    grid_size_deg: float = 0.001, # Approx 100m
    db: Session = Depends(database.get_db)
):
    results = []
    
    if method == "kmeans":
        # Check count first to avoid K > N error
        count = db.query(func.count(models.Report.report_id)).scalar()
        if count == 0:
            return []
        
        actual_k = min(k, count)
        
        # ST_ClusterKMeans requires a window function
        # Priority Score Formula: (Severity * 0.4) + (Upvotes * 0.3) + (Recency * 0.3)
        # Severity: High=10, Medium=5, Low=2
        # Recency: 10 / (1 + days_old)
        stmt = text("""
            WITH clusters AS (
                SELECT
                    report_id,
                    ST_ClusterKMeans(location, :k) OVER () AS cid,
                    location as geom,
                    (
                        (CASE 
                            WHEN severity = 'High' THEN 10 
                            WHEN severity = 'Medium' THEN 5 
                            ELSE 2 
                         END) * 0.35 +
                        (upvote_count * 0.25) +
                        (10.0 / (1.0 + EXTRACT(EPOCH FROM (now() - created_at)) / 86400.0)) * 0.2 +
                        (road_importance * 0.2)
                    ) as report_score
                FROM reports
            )
            SELECT
                cid,
                ST_Y(ST_Centroid(ST_Collect(geom))) AS lat,
                ST_X(ST_Centroid(ST_Collect(geom))) AS lon,
                COUNT(*) AS report_count,
                SUM(report_score) AS score,
                (ARRAY_AGG(title ORDER BY report_score DESC))[1] as top_title,
                (ARRAY_AGG(description ORDER BY report_score DESC))[1] as top_description,
                (ARRAY_AGG(r.report_id ORDER BY report_score DESC))[1] as top_report_id
            FROM clusters c
            JOIN reports r ON c.report_id = r.report_id
            WHERE cid IS NOT NULL
            GROUP BY cid
            ORDER BY score DESC
        """)
        
        try:
            rows = db.execute(stmt, {"k": actual_k}).fetchall()
            
            for i, row in enumerate(rows):
                # Fetch image for the top report
                image_url = None
                top_report_image = db.query(models.ReportImage).filter(models.ReportImage.report_id == row.top_report_id).first()
                if top_report_image:
                    image_url = top_report_image.file_path

                results.append({
                    "hotspot_id": row.cid if row.cid is not None else i,
                    "center": {"lat": row.lat, "lon": row.lon},
                    "report_count": row.report_count,
                    "score": row.score,
                    "title": row.top_title,
                    "description": row.top_description,
                    "image": image_url
                })
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    elif method == "grid":
        # Grid aggregation using ST_SnapToGrid and ST_MakeEnvelope for polygons
        # grid_size_deg is roughly the size of the cell in degrees
        stmt = text("""
            WITH grid AS (
                SELECT
                    ST_SnapToGrid(location, :grid_size) AS cell_center,
                    COUNT(*) AS report_count
                FROM reports
                GROUP BY cell_center
            )
            SELECT
                ST_X(cell_center) AS lon,
                ST_Y(cell_center) AS lat,
                report_count,
                ST_AsGeoJSON(ST_MakeEnvelope(
                    ST_X(cell_center) - :grid_size / 2,
                    ST_Y(cell_center) - :grid_size / 2,
                    ST_X(cell_center) + :grid_size / 2,
                    ST_Y(cell_center) + :grid_size / 2,
                    4326
                )) AS geometry
            FROM grid
            ORDER BY report_count DESC
        """)
        
        rows = db.execute(stmt, {"grid_size": grid_size_deg}).fetchall()
        
        # Return GeoJSON FeatureCollection
        features = []
        for i, row in enumerate(rows):
            import json
            geometry = json.loads(row.geometry)
            features.append({
                "type": "Feature",
                "id": i,
                "geometry": geometry,
                "properties": {
                    "count": row.report_count,
                    "center": {"lat": row.lat, "lon": row.lon}
                }
            })
            
        return {
            "type": "FeatureCollection",
            "features": features
        }
            
    return results

@router.get("/export")
def export_hotspots(
    method: str = "kmeans",
    k: int = 5,
    db: Session = Depends(database.get_db)
):
    # Reuse logic or call internal function
    # For simplicity, let's just run the kmeans query again
    stmt = text("""
        WITH clusters AS (
            SELECT
                report_id,
                ST_ClusterKMeans(location, :k) OVER () AS cid,
                location as geom
            FROM reports
        )
        SELECT
            cid,
            ST_Y(ST_Centroid(ST_Collect(geom))) AS lat,
            ST_X(ST_Centroid(ST_Collect(geom))) AS lon,
            COUNT(*) AS report_count
        FROM clusters
        WHERE cid IS NOT NULL
        GROUP BY cid
        ORDER BY report_count DESC
    """)
    
    rows = db.execute(stmt, {"k": k}).fetchall()
    
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["HOTSPOT_ID", "LATITUDE", "LONGITUDE", "REPORT_COUNT"])
    
    for row in rows:
        writer.writerow([row.cid, row.lat, row.lon, row.report_count])
        
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=hotspots.csv"
    return response
