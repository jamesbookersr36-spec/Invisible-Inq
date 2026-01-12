"""
User service for managing user data in PostgreSQL (Neon) database
"""
from typing import Optional, Dict
from datetime import datetime
import logging
from neon_database import neon_db
from auth import get_password_hash, verify_password
from models import UserCreate, UserResponse

logger = logging.getLogger(__name__)

def create_user(user_data: UserCreate, auth_provider: str = "local", is_admin: bool = False) -> Optional[UserResponse]:
    """
    Create a new user in PostgreSQL database
    
    Args:
        user_data: User creation data
        auth_provider: Authentication provider (local, google)
        is_admin: Whether user should have admin privileges
    
    Returns:
        UserResponse if successful, None otherwise
    """
    try:
        # Hash password if provided
        hashed_password = None
        if user_data.password:
            hashed_password = get_password_hash(user_data.password)
        
        # Insert user into PostgreSQL
        query = """
        INSERT INTO users (email, full_name, hashed_password, auth_provider, is_active, is_admin, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id, email, full_name, profile_picture, auth_provider, is_active, is_admin, created_at, updated_at
        """
        
        params = (
            user_data.email,
            user_data.full_name,
            hashed_password,
            auth_provider,
            True,  # is_active
            is_admin
        )
        
        result = neon_db.execute_write_query(query, params)
        
        if result and len(result) > 0:
            user_row = result[0]
            
            return UserResponse(
                id=str(user_row['id']),
                email=user_row['email'],
                full_name=user_row['full_name'],
                profile_picture=user_row.get('profile_picture'),
                is_active=user_row.get('is_active', True),
                is_admin=user_row.get('is_admin', False),
                created_at=user_row.get('created_at'),
                auth_provider=user_row.get('auth_provider', 'local')
            )
        
        return None
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error creating user: {error_msg}")
        # Check if it's a unique constraint violation (user already exists)
        if "unique" in error_msg.lower() or "duplicate" in error_msg.lower():
            logger.warning(f"User with email {user_data.email} already exists")
            # Re-raise with a clearer message
            raise ValueError(f"User with email {user_data.email} already exists") from e
        # Check if table doesn't exist
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            logger.error("PostgreSQL 'users' table does not exist. Please run migration script.")
            raise RuntimeError("Database tables not initialized. Please run: python migrate_admin_to_postgres.py") from e
        # Re-raise other exceptions
        raise

def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Get user by email from PostgreSQL database
    
    Args:
        email: User's email address
    
    Returns:
        User data dict if found, None otherwise
    """
    try:
        query = """
        SELECT id, email, full_name, hashed_password, profile_picture, 
               is_active, is_admin, created_at, updated_at, auth_provider
        FROM users
        WHERE email = %s
        """
        
        result = neon_db.execute_query(query, (email,))
        
        if result and len(result) > 0:
            user_row = result[0]
            
            return {
                "id": str(user_row['id']),
                "email": user_row['email'],
                "full_name": user_row.get('full_name'),
                "hashed_password": user_row.get('hashed_password'),
                "profile_picture": user_row.get('profile_picture'),
                "is_active": user_row.get('is_active', True),
                "is_admin": user_row.get('is_admin', False),
                "created_at": user_row.get('created_at'),
                "auth_provider": user_row.get('auth_provider', 'local')
            }
        
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Get user by ID from PostgreSQL database
    
    Args:
        user_id: User's ID
    
    Returns:
        User data dict if found, None otherwise
    """
    try:
        query = """
        SELECT id, email, full_name, hashed_password, profile_picture, 
               is_active, is_admin, created_at, updated_at, auth_provider
        FROM users
        WHERE id = %s
        """
        
        result = neon_db.execute_query(query, (int(user_id),))
        
        if result and len(result) > 0:
            user_row = result[0]
            
            return {
                "id": str(user_row['id']),
                "email": user_row['email'],
                "full_name": user_row.get('full_name'),
                "hashed_password": user_row.get('hashed_password'),
                "profile_picture": user_row.get('profile_picture'),
                "is_active": user_row.get('is_active', True),
                "is_admin": user_row.get('is_admin', False),
                "created_at": user_row.get('created_at'),
                "auth_provider": user_row.get('auth_provider', 'local')
            }
        
        return None
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

def authenticate_user(email: str, password: str) -> Optional[Dict]:
    """
    Authenticate a user with email and password
    
    Args:
        email: User's email
        password: User's plain text password
    
    Returns:
        User data dict if authentication successful, None otherwise
    """
    try:
        user = get_user_by_email(email)
        
        if not user:
            logger.debug(f"User not found: {email}")
            return None
        
        # Check if user uses local authentication
        if user.get('auth_provider') != 'local':
            logger.warning(f"User {email} attempted password login but uses {user.get('auth_provider')} auth")
            return None
        
        # Check if user is active
        if not user.get('is_active', True):
            logger.warning(f"Inactive user attempted login: {email}")
            return None
        
        # Verify password
        hashed_password = user.get('hashed_password')
        if not hashed_password:
            logger.warning(f"User {email} has no password set")
            return None
        
        if not verify_password(password, hashed_password):
            logger.warning(f"Invalid password for user: {email}")
            return None
        
        # Remove password from returned user data
        user.pop('hashed_password', None)
        return user
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error authenticating user {email}: {error_msg}")
        # Check if table doesn't exist
        if "relation" in error_msg.lower() and "does not exist" in error_msg.lower():
            logger.error("PostgreSQL 'users' table does not exist. Please run migration script.")
        return None

def create_or_update_google_user(google_user_info: Dict) -> Optional[UserResponse]:
    """
    Create or update user from Google OAuth
    
    Args:
        google_user_info: User info from Google OAuth
    
    Returns:
        UserResponse if successful, None otherwise
    """
    try:
        email = google_user_info.get('email')
        
        # Check if user exists
        existing_user = get_user_by_email(email)
        
        if existing_user:
            # Update existing user with Google info
            query = """
            UPDATE users
            SET full_name = COALESCE(%s, full_name),
                profile_picture = COALESCE(%s, profile_picture),
                auth_provider = 'google',
                updated_at = CURRENT_TIMESTAMP
            WHERE email = %s
            RETURNING id, email, full_name, profile_picture, auth_provider, is_active, is_admin, created_at, updated_at
            """
            
            params = (
                google_user_info.get('full_name'),
                google_user_info.get('profile_picture'),
                email
            )
            
            result = neon_db.execute_write_query(query, params)
        else:
            # Create new user from Google info
            query = """
            INSERT INTO users (email, full_name, profile_picture, auth_provider, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, 'google', TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, email, full_name, profile_picture, auth_provider, is_active, is_admin, created_at, updated_at
            """
            
            params = (
                email,
                google_user_info.get('full_name'),
                google_user_info.get('profile_picture')
            )
            
            result = neon_db.execute_write_query(query, params)
        
        if result and len(result) > 0:
            user_row = result[0]
            
            return UserResponse(
                id=str(user_row['id']),
                email=user_row['email'],
                full_name=user_row.get('full_name'),
                profile_picture=user_row.get('profile_picture'),
                is_active=user_row.get('is_active', True),
                is_admin=user_row.get('is_admin', False),
                created_at=user_row.get('created_at'),
                auth_provider='google'
            )
        
        return None
    except Exception as e:
        logger.error(f"Error creating/updating Google user: {e}")
        return None

def update_user_profile(user_id: str, updates: Dict) -> Optional[UserResponse]:
    """
    Update user profile
    
    Args:
        user_id: User's ID
        updates: Dict of fields to update
    
    Returns:
        Updated UserResponse if successful, None otherwise
    """
    try:
        # Build SET clause dynamically
        set_clauses = []
        params = []
        
        allowed_fields = ['full_name', 'profile_picture']
        for field in allowed_fields:
            if field in updates and updates[field] is not None:
                set_clauses.append(f"{field} = %s")
                params.append(updates[field])
        
        if not set_clauses:
            # No fields to update
            return None
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        set_clause = ", ".join(set_clauses)
        params.append(int(user_id))
        
        query = f"""
        UPDATE users
        SET {set_clause}
        WHERE id = %s
        RETURNING id, email, full_name, profile_picture, auth_provider, is_active, is_admin, created_at, updated_at
        """
        
        result = neon_db.execute_write_query(query, tuple(params))
        
        if result and len(result) > 0:
            user_row = result[0]
            
            return UserResponse(
                id=str(user_row['id']),
                email=user_row['email'],
                full_name=user_row.get('full_name'),
                profile_picture=user_row.get('profile_picture'),
                is_active=user_row.get('is_active', True),
                is_admin=user_row.get('is_admin', False),
                created_at=user_row.get('created_at'),
                auth_provider=user_row.get('auth_provider', 'local')
            )
        
        return None
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return None

def get_all_users(limit: int = 100, offset: int = 0) -> list:
    """
    Get all users from PostgreSQL database (for admin)
    Includes both regular users and admin users
    
    Args:
        limit: Maximum number of users to return
        offset: Number of users to skip
    
    Returns:
        List of user dictionaries with subscription info
    """
    try:
        # Get regular users
        query = """
        SELECT id, email, full_name, profile_picture, auth_provider, is_active, is_admin,
               subscription_tier, subscription_status, subscription_start_date, subscription_end_date,
               created_at, updated_at
        FROM users
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
        """
        
        result = neon_db.execute_query(query, (limit, offset))
        
        users = []
        for row in result:
            users.append({
                "id": str(row['id']),
                "email": row['email'],
                "full_name": row.get('full_name'),
                "profile_picture": row.get('profile_picture'),
                "auth_provider": row.get('auth_provider', 'local'),
                "is_active": row.get('is_active', True),
                "is_admin": row.get('is_admin', False),
                "subscription_tier": row.get('subscription_tier', 'free'),
                "subscription_status": row.get('subscription_status', 'active'),
                "subscription_start_date": row.get('subscription_start_date'),
                "subscription_end_date": row.get('subscription_end_date'),
                "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
                "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None
            })
        
        # Also get admin users (from admin_users table)
        try:
            admin_query = """
            SELECT id, email, full_name, profile_picture, auth_provider, is_active, is_admin,
                   created_at, updated_at
            FROM admin_users
            ORDER BY created_at DESC
            """
            admin_result = neon_db.execute_query(admin_query)
            
            for row in admin_result:
                users.append({
                    "id": f"admin_{row['id']}",  # Prefix to avoid ID conflicts
                    "email": row['email'],
                    "full_name": row.get('full_name'),
                    "profile_picture": row.get('profile_picture'),
                    "auth_provider": row.get('auth_provider', 'local'),
                    "is_active": row.get('is_active', True),
                    "is_admin": True,  # Admin users are always admins
                    "subscription_tier": None,
                    "subscription_status": None,
                    "subscription_start_date": None,
                    "subscription_end_date": None,
                    "created_at": row.get('created_at').isoformat() if row.get('created_at') else None,
                    "updated_at": row.get('updated_at').isoformat() if row.get('updated_at') else None
                })
        except Exception as admin_err:
            logger.warning(f"Could not fetch admin users: {admin_err}")
            # Continue without admin users if table doesn't exist
        
        # Sort all users by created_at descending
        users.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []
