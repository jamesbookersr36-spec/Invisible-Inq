"""
User activity tracking service for analytics
"""
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import logging
from database import db
from models import UserActivityCreate, UserActivityResponse

logger = logging.getLogger(__name__)

def create_activity(activity_data: UserActivityCreate) -> Optional[UserActivityResponse]:
    """
    Create a new activity record in Neo4j database
    
    Args:
        activity_data: Activity data to record
    
    Returns:
        UserActivityResponse if successful, None otherwise
    """
    try:
        # Create activity node in Neo4j
        query = """
        CREATE (a:UserActivity {
            user_id: $user_id,
            session_id: $session_id,
            activity_type: $activity_type,
            page_url: $page_url,
            section_id: $section_id,
            section_title: $section_title,
            duration_seconds: $duration_seconds,
            metadata: $metadata,
            timestamp: datetime()
        })
        RETURN a, elementId(a) as activity_id
        """
        
        params = {
            "user_id": activity_data.user_id,
            "session_id": activity_data.session_id,
            "activity_type": activity_data.activity_type,
            "page_url": activity_data.page_url,
            "section_id": activity_data.section_id,
            "section_title": activity_data.section_title,
            "duration_seconds": activity_data.duration_seconds,
            "metadata": activity_data.metadata
        }
        
        result = db.execute_write_query(query, params)
        
        if result and len(result) > 0:
            activity_node = result[0].get('a', {})
            activity_id = result[0].get('activity_id', '')
            
            return UserActivityResponse(
                id=activity_id,
                user_id=activity_node.get('user_id'),
                session_id=activity_node.get('session_id'),
                activity_type=activity_node.get('activity_type'),
                page_url=activity_node.get('page_url'),
                section_id=activity_node.get('section_id'),
                section_title=activity_node.get('section_title'),
                duration_seconds=activity_node.get('duration_seconds'),
                metadata=activity_node.get('metadata'),
                timestamp=activity_node.get('timestamp')
            )
        
        return None
    except Exception as e:
        logger.error(f"Error creating activity: {e}")
        return None

def get_activities(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    skip: int = 0
) -> List[UserActivityResponse]:
    """
    Get activities with optional filters
    
    Args:
        user_id: Filter by user ID
        session_id: Filter by session ID
        activity_type: Filter by activity type
        start_date: Filter by start date
        end_date: Filter by end date
        limit: Maximum number of results
        skip: Number of results to skip
    
    Returns:
        List of UserActivityResponse objects
    """
    try:
        # Build query with filters
        where_clauses = []
        params = {"limit": limit, "skip": skip}
        
        if user_id:
            where_clauses.append("a.user_id = $user_id")
            params["user_id"] = user_id
        
        if session_id:
            where_clauses.append("a.session_id = $session_id")
            params["session_id"] = session_id
        
        if activity_type:
            where_clauses.append("a.activity_type = $activity_type")
            params["activity_type"] = activity_type
        
        if start_date:
            where_clauses.append("a.timestamp >= $start_date")
            params["start_date"] = start_date
        
        if end_date:
            where_clauses.append("a.timestamp <= $end_date")
            params["end_date"] = end_date
        
        where_clause = " AND ".join(where_clauses) if where_clauses else "true"
        
        query = f"""
        MATCH (a:UserActivity)
        WHERE {where_clause}
        OPTIONAL MATCH (u:User)
        WHERE u.email IS NOT NULL AND (elementId(u) = a.user_id OR toString(elementId(u)) = a.user_id)
        RETURN a, elementId(a) as activity_id, u.email as user_email, u.full_name as user_name
        ORDER BY a.timestamp DESC
        SKIP $skip
        LIMIT $limit
        """
        
        result = db.execute_query(query, params)
        
        activities = []
        for record in result:
            activity_node = record.get('a', {})
            activity_id = record.get('activity_id', '')
            user_email = record.get('user_email')
            user_name = record.get('user_name')
            
            activities.append(UserActivityResponse(
                id=activity_id,
                user_id=activity_node.get('user_id'),
                session_id=activity_node.get('session_id'),
                activity_type=activity_node.get('activity_type'),
                page_url=activity_node.get('page_url'),
                section_id=activity_node.get('section_id'),
                section_title=activity_node.get('section_title'),
                duration_seconds=activity_node.get('duration_seconds'),
                metadata=activity_node.get('metadata'),
                timestamp=activity_node.get('timestamp'),
                user_email=user_email,
                user_name=user_name
            ))
        
        return activities
    except Exception as e:
        logger.error(f"Error getting activities: {e}")
        return []

def get_activity_statistics(days: int = 7) -> Dict:
    """
    Get activity statistics for the dashboard
    
    Args:
        days: Number of days to look back
    
    Returns:
        Dictionary with statistics
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total activities
        total_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date
        RETURN count(a) as total
        """
        
        # Unique users
        unique_users_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date AND a.user_id IS NOT NULL
        RETURN count(DISTINCT a.user_id) as unique_users
        """
        
        # Unique sessions
        unique_sessions_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date
        RETURN count(DISTINCT a.session_id) as unique_sessions
        """
        
        # Total duration
        total_duration_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date AND a.duration_seconds IS NOT NULL
        RETURN sum(a.duration_seconds) as total_duration
        """
        
        # Activity by type
        by_type_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date
        RETURN a.activity_type as type, count(a) as count
        ORDER BY count DESC
        """
        
        # Top sections viewed
        top_sections_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date 
          AND a.section_title IS NOT NULL 
          AND a.activity_type IN ['section_view', 'page_view']
        RETURN a.section_title as section, count(a) as views
        ORDER BY views DESC
        LIMIT 10
        """
        
        # Activities by day
        by_day_query = """
        MATCH (a:UserActivity)
        WHERE a.timestamp >= $start_date
        WITH date(a.timestamp) as day, count(a) as count
        RETURN day, count
        ORDER BY day ASC
        """
        
        params = {"start_date": start_date}
        
        total_result = db.execute_query(total_query, params)
        unique_users_result = db.execute_query(unique_users_query, params)
        unique_sessions_result = db.execute_query(unique_sessions_query, params)
        total_duration_result = db.execute_query(total_duration_query, params)
        by_type_result = db.execute_query(by_type_query, params)
        top_sections_result = db.execute_query(top_sections_query, params)
        by_day_result = db.execute_query(by_day_query, params)
        
        return {
            "total_activities": total_result[0].get('total', 0) if total_result else 0,
            "unique_users": unique_users_result[0].get('unique_users', 0) if unique_users_result else 0,
            "unique_sessions": unique_sessions_result[0].get('unique_sessions', 0) if unique_sessions_result else 0,
            "total_duration_seconds": total_duration_result[0].get('total_duration', 0) if total_duration_result else 0,
            "activities_by_type": [{"type": r.get('type'), "count": r.get('count')} for r in by_type_result],
            "top_sections": [{"section": r.get('section'), "views": r.get('views')} for r in top_sections_result],
            "activities_by_day": [{"date": str(r.get('day')), "count": r.get('count')} for r in by_day_result],
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error getting activity statistics: {e}")
        return {
            "total_activities": 0,
            "unique_users": 0,
            "unique_sessions": 0,
            "total_duration_seconds": 0,
            "activities_by_type": [],
            "top_sections": [],
            "activities_by_day": [],
            "period_days": days,
            "error": str(e)
        }

def get_user_activity_summary(user_id: str, days: int = 30) -> Dict:
    """
    Get activity summary for a specific user
    
    Args:
        user_id: User ID
        days: Number of days to look back
    
    Returns:
        Dictionary with user activity summary
    """
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
        MATCH (a:UserActivity)
        WHERE a.user_id = $user_id AND a.timestamp >= $start_date
        WITH a.activity_type as type, 
             count(a) as count,
             sum(CASE WHEN a.duration_seconds IS NOT NULL THEN a.duration_seconds ELSE 0 END) as total_duration
        RETURN type, count, total_duration
        ORDER BY count DESC
        """
        
        params = {"user_id": user_id, "start_date": start_date}
        result = db.execute_query(query, params)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "activities": [
                {
                    "type": r.get('type'),
                    "count": r.get('count'),
                    "total_duration_seconds": r.get('total_duration', 0)
                }
                for r in result
            ]
        }
    except Exception as e:
        logger.error(f"Error getting user activity summary: {e}")
        return {
            "user_id": user_id,
            "period_days": days,
            "activities": [],
            "error": str(e)
        }
