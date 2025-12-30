from sqlalchemy.orm import Session
from .. import models
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_duplicate(db: Session, description: str, threshold: float = 0.5) -> list[dict]:
    """
    Duplicate detection using TF-IDF and Cosine Similarity.
    Smartly identifies reports with similar semantic content.
    """
    if not description:
        return []
        
    duplicates = []
    
    # Check last 100 reports for efficiency context
    recent_reports = db.query(models.Report).filter(models.Report.description != None).order_by(models.Report.created_at.desc()).limit(100).all()
    
    if not recent_reports:
        return []

    # Prepare corpus: [current_desc] + [all_recent_descs]
    corpus = [description] + [r.description for r in recent_reports]
    
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Calculate cosine similarity of the first item (current) against all others
        # cosine_similarity returns a matrix; we want the first row, excluding the first item itself
        # shape: (1, len(corpus))
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # Flatten result
        scores = cosine_sim[0]
        
        for idx, score in enumerate(scores):
            if score >= threshold:
                report = recent_reports[idx]
                duplicates.append({
                    "report_id": report.report_id,
                    "title": report.title,
                    "similarity": round(float(score), 2)
                })
        
        # Sort by similarity descending
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        
    except Exception as e:
        print(f"Error in duplicate detection: {e}")
        # Fallback? Or just return empty
        
    return duplicates
