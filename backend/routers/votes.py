from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Vote, Report, User
from routers.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["votes"])

@router.post("/{report_id}/upvote")
async def upvote_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upvote a report. Creates or updates vote."""
    # Check if report exists
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user already voted
    vote_result = await db.execute(
        select(Vote).where(
            Vote.user_id == current_user.id,
            Vote.report_id == report_id
        )
    )
    existing_vote = vote_result.scalars().first()
    
    if existing_vote:
        if existing_vote.value == 1:
            # Already upvoted, remove vote
            await db.delete(existing_vote)
            report.upvotes = max(0, report.upvotes - 1)
        else:
            # Was downvote, change to upvote
            existing_vote.value = 1
            report.upvotes += 1
    else:
        # New upvote
        new_vote = Vote(user_id=current_user.id, report_id=report_id, value=1)
        db.add(new_vote)
        report.upvotes += 1
    
    await db.commit()
    await db.refresh(report)
    
    return {"message": "Vote recorded", "upvotes": report.upvotes}

@router.post("/{report_id}/downvote")
async def downvote_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Downvote a report. Creates or updates vote."""
    # Check if report exists
    result = await db.execute(select(Report).where(Report.id == report_id))
    report = result.scalars().first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user already voted
    vote_result = await db.execute(
        select(Vote).where(
            Vote.user_id == current_user.id,
            Vote.report_id == report_id
        )
    )
    existing_vote = vote_result.scalars().first()
    
    if existing_vote:
        if existing_vote.value == -1:
            # Already downvoted, remove vote
            await db.delete(existing_vote)
        else:
            # Was upvote, change to downvote
            existing_vote.value = -1
            report.upvotes = max(0, report.upvotes - 1)
    else:
        # New downvote (doesn't affect upvote count)
        new_vote = Vote(user_id=current_user.id, report_id=report_id, value=-1)
        db.add(new_vote)
    
    await db.commit()
    await db.refresh(report)
    
    return {"message": "Vote recorded", "upvotes": report.upvotes}
