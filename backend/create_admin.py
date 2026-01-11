"""
Script to create an admin user
Run this once to create your first admin user
"""
from user_service import create_user
from models import UserCreate
import sys

def create_admin():
    """Create an admin user"""
    print("=" * 60)
    print("CREATE ADMIN USER")
    print("=" * 60)
    
    # Get admin details
    email = input("Enter admin email: ").strip()
    if not email:
        print("Error: Email is required")
        sys.exit(1)
    
    password = input("Enter admin password (min 6 characters): ").strip()
    if len(password) < 6:
        print("Error: Password must be at least 6 characters")
        sys.exit(1)
    
    full_name = input("Enter admin full name: ").strip()
    if not full_name:
        full_name = "Administrator"
    
    # Create admin user
    print(f"\nCreating admin user: {email}...")
    
    admin_data = UserCreate(
        email=email,
        password=password,
        full_name=full_name
    )
    
    try:
        user = create_user(admin_data, auth_provider="local", is_admin=True)
        
        if user:
            print("\n" + "=" * 60)
            print("✅ SUCCESS! Admin user created:")
            print("=" * 60)
            print(f"Email: {user.email}")
            print(f"Name: {user.full_name}")
            print(f"Admin: {user.is_admin}")
            print(f"ID: {user.id}")
            print("=" * 60)
            print("\nYou can now log in to the admin dashboard at:")
            print("http://localhost:3001")
            print("=" * 60)
        else:
            print("\n❌ ERROR: Failed to create admin user")
            print("The user might already exist or there was a database error")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_admin()
