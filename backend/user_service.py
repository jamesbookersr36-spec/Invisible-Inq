"""
User service for managing user data in Neo4j database
"""
from typing import Optional, Dict
from datetime import datetime
import logging
from database import db
from auth import get_password_hash, verify_password
from models import UserCreate, UserResponse

logger = logging.getLogger(__name__)

def create_user(user_data: UserCreate, auth_provider: str = "local", is_admin: bool = False) -> Optional[UserResponse]:
    """
    Create a new user in Neo4j database
    
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
        
        # Create user node in Neo4j
        query = """
        CREATE (u:User {
            email: $email,
            full_name: $full_name,
            hashed_password: $hashed_password,
            auth_provider: $auth_provider,
            is_active: true,
            is_admin: $is_admin,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN u, elementId(u) as user_id
        """
        
        params = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "auth_provider": auth_provider,
            "is_admin": is_admin
        }
        
        result = db.execute_write_query(query, params)
        
        if result and len(result) > 0:
            user_node = result[0].get('u', {})
            user_id = result[0].get('user_id', '')
            
            return UserResponse(
                id=user_id,
                email=user_node.get('email'),
                full_name=user_node.get('full_name'),
                profile_picture=user_node.get('profile_picture'),
                is_active=user_node.get('is_active', True),
                is_admin=user_node.get('is_admin', False),
                created_at=user_node.get('created_at'),
                auth_provider=user_node.get('auth_provider', 'local')
            )
        
        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None

def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Get user by email from Neo4j database
    
    Args:
        email: User's email address
    
    Returns:
        User data dict if found, None otherwise
    """
    try:
        query = """
        MATCH (u:User {email: $email})
        RETURN u, elementId(u) as user_id
        """
        
        result = db.execute_query(query, {"email": email})
        
        if result and len(result) > 0:
            user_node = result[0].get('u', {})
            user_id = result[0].get('user_id', '')
            
            return {
                "id": user_id,
                "email": user_node.get('email'),
                "full_name": user_node.get('full_name'),
                "hashed_password": user_node.get('hashed_password'),
                "profile_picture": user_node.get('profile_picture'),
                "is_active": user_node.get('is_active', True),
                "created_at": user_node.get('created_at'),
                "auth_provider": user_node.get('auth_provider', 'local')
            }
        
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Get user by ID from Neo4j database
    
    Args:
        user_id: User's unique ID (elementId)
    
    Returns:
        User data dict if found, None otherwise
    """
    try:
        query = """
        MATCH (u:User)
        WHERE elementId(u) = $user_id
        RETURN u, elementId(u) as user_id
        """
        
        result = db.execute_query(query, {"user_id": user_id})
        
        if result and len(result) > 0:
            user_node = result[0].get('u', {})
            user_id = result[0].get('user_id', '')
            
            return {
                "id": user_id,
                "email": user_node.get('email'),
                "full_name": user_node.get('full_name'),
                "hashed_password": user_node.get('hashed_password'),
                "profile_picture": user_node.get('profile_picture'),
                "is_active": user_node.get('is_active', True),
                "is_admin": user_node.get('is_admin', False),
                "created_at": user_node.get('created_at'),
                "auth_provider": user_node.get('auth_provider', 'local')
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
            return None
        
        # Check if user uses local authentication
        if user.get('auth_provider') != 'local':
            logger.warning(f"User {email} attempted password login but uses {user.get('auth_provider')} auth")
            return None
        
        # Verify password
        hashed_password = user.get('hashed_password')
        if not hashed_password or not verify_password(password, hashed_password):
            return None
        
        return user
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
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
            MATCH (u:User {email: $email})
            SET u.full_name = COALESCE($full_name, u.full_name),
                u.profile_picture = COALESCE($profile_picture, u.profile_picture),
                u.auth_provider = 'google',
                u.updated_at = datetime()
            RETURN u, elementId(u) as user_id
            """
            
            params = {
                "email": email,
                "full_name": google_user_info.get('full_name'),
                "profile_picture": google_user_info.get('profile_picture')
            }
            
            result = db.execute_write_query(query, params)
        else:
            # Create new user from Google info
            query = """
            CREATE (u:User {
                email: $email,
                full_name: $full_name,
                profile_picture: $profile_picture,
                auth_provider: 'google',
                is_active: true,
                created_at: datetime(),
                updated_at: datetime()
            })
            RETURN u, elementId(u) as user_id
            """
            
            params = {
                "email": email,
                "full_name": google_user_info.get('full_name'),
                "profile_picture": google_user_info.get('profile_picture')
            }
            
            result = db.execute_write_query(query, params)
        
        if result and len(result) > 0:
            user_node = result[0].get('u', {})
            user_id = result[0].get('user_id', '')
            
            return UserResponse(
                id=user_id,
                email=user_node.get('email'),
                full_name=user_node.get('full_name'),
                profile_picture=user_node.get('profile_picture'),
                is_active=user_node.get('is_active', True),
                is_admin=user_node.get('is_admin', False),
                created_at=user_node.get('created_at'),
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
        params = {"user_id": user_id}
        
        allowed_fields = ['full_name', 'profile_picture']
        for field in allowed_fields:
            if field in updates and updates[field] is not None:
                set_clauses.append(f"u.{field} = ${field}")
                params[field] = updates[field]
        
        if not set_clauses:
            # No fields to update
            return None
        
        set_clauses.append("u.updated_at = datetime()")
        set_clause = ", ".join(set_clauses)
        
        query = f"""
        MATCH (u:User)
        WHERE elementId(u) = $user_id
        SET {set_clause}
        RETURN u, elementId(u) as user_id
        """
        
        result = db.execute_write_query(query, params)
        
        if result and len(result) > 0:
            user_node = result[0].get('u', {})
            user_id = result[0].get('user_id', '')
            
            return UserResponse(
                id=user_id,
                email=user_node.get('email'),
                full_name=user_node.get('full_name'),
                profile_picture=user_node.get('profile_picture'),
                is_active=user_node.get('is_active', True),
                is_admin=user_node.get('is_admin', False),
                created_at=user_node.get('created_at'),
                auth_provider=user_node.get('auth_provider', 'local')
            )
        
        return None
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        return None
