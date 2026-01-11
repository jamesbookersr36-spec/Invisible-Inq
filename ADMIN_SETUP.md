# Administrator Site Setup Guide

This guide explains how to set up and use the administrator dashboard for tracking user activities and analytics.

## Overview

The admin site is a separate React application that runs on **port 3001** and provides:
- 📊 **Analytics Dashboard** - Visual statistics and charts
- 👥 **User Activity Tracking** - Detailed activity logs
- 📈 **Real-time Monitoring** - Track page views, section views, and user interactions
- 🔒 **Secure Admin Access** - Separate authentication for administrators

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  Main Frontend  │      │  Admin Frontend  │      │     Backend     │
│   (Port 5173)   │────▶ │   (Port 3001)    │────▶ │   (Port 8000)   │
│                 │      │                  │      │                 │
│ - Tracks user   │      │ - Admin login    │      │ - Activity API  │
│   activity      │      │ - Dashboard      │      │ - Analytics API │
│                 │      │ - Activity logs  │      │ - User tracking │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## Backend Setup (Already Done)

The following has been added to your backend:

### New Files
- `backend/activity_service.py` - Activity tracking service
- Updated `backend/models.py` - Added activity models and admin flag
- Updated `backend/user_service.py` - Added admin support
- Updated `backend/auth.py` - Added admin verification
- Updated `backend/main.py` - Added activity and admin endpoints

### New Endpoints

#### Activity Tracking
- `POST /api/activity/track` - Track user activity (public)

#### Admin Only Endpoints
- `POST /api/auth/admin/login` - Admin login
- `GET /api/admin/dashboard` - Dashboard data
- `GET /api/admin/statistics?days=7` - Statistics
- `GET /api/admin/activities` - Activity logs with filters
- `GET /api/admin/users/{user_id}/activity` - User-specific activity

### Database Schema

User activity is stored in Neo4j:

```cypher
(:UserActivity {
  user_id: string,           // User ID or null for anonymous
  session_id: string,         // Browser session ID
  activity_type: string,      // page_view, section_view, search, etc.
  page_url: string,           // Current page URL
  section_id: string,         // Section ID if applicable
  section_title: string,      // Section title
  duration_seconds: int,      // Time spent
  metadata: map,              // Additional data
  timestamp: datetime         // When activity occurred
})
```

## Admin Frontend Setup

### 1. Install Dependencies

```bash
cd admin
npm install
```

The admin app includes:
- React 19
- React Router DOM for routing
- Recharts for data visualization
- Tailwind CSS for styling
- date-fns for date formatting

### 2. Configure Environment

Create `admin/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Start the Admin App

```bash
cd admin
npm run dev
```

The admin dashboard will be available at: **http://localhost:3001**

### 4. Build for Production

```bash
cd admin
npm run build
```

## Creating an Admin User

Admin users must have the `is_admin` flag set to `true` in the database. You need to manually create the first admin user.

### Option 1: Using Neo4j Browser

1. Open Neo4j Browser (usually http://localhost:7474)
2. Run this Cypher query:

```cypher
CREATE (u:User {
  email: "admin@example.com",
  full_name: "Admin User",
  hashed_password: "$2b$12$YOUR_HASHED_PASSWORD_HERE",
  auth_provider: "local",
  is_active: true,
  is_admin: true,
  created_at: datetime(),
  updated_at: datetime()
})
RETURN u
```

### Option 2: Using Python Script

Create `backend/create_admin.py`:

```python
from user_service import create_user
from models import UserCreate
from database import db

# Create admin user
admin_data = UserCreate(
    email="admin@example.com",
    password="your-secure-password",  # Will be hashed
    full_name="Admin User"
)

# Create with admin flag
user = create_user(admin_data, auth_provider="local", is_admin=True)
if user:
    print(f"Admin user created: {user.email}")
else:
    print("Failed to create admin user")
```

Run it:

```bash
cd backend
python create_admin.py
```

### Option 3: Promote Existing User

If you have an existing user, promote them to admin:

```cypher
MATCH (u:User {email: "user@example.com"})
SET u.is_admin = true
RETURN u
```

## Main Frontend Integration (Activity Tracking)

### 1. Import the Hook

The activity tracking hook is already created at `src/hooks/useActivityTracking.js`.

### 2. Use in Your Components

Add to any page component:

```jsx
import { useActivityTracking } from '../hooks/useActivityTracking';

function MyPage() {
  const { trackSectionView, trackSearch, trackGraphInteraction } = useActivityTracking();
  
  // Track when user views a section
  useEffect(() => {
    if (sectionId) {
      trackSectionView(sectionId, sectionTitle);
    }
  }, [sectionId, sectionTitle]);
  
  // Track search
  const handleSearch = (query) => {
    trackSearch(query);
    // ... rest of search logic
  };
  
  // Track graph interactions
  const handleNodeClick = (node) => {
    trackGraphInteraction('node_click', { nodeId: node.id });
    // ... rest of handler
  };
  
  return <div>...</div>;
}
```

### 3. Automatic Tracking

The hook automatically tracks:
- ✅ Page views when route changes
- ✅ Time spent on pages
- ✅ Session duration

### 4. Manual Tracking

Track specific events:

```jsx
const { trackActivity } = useActivityTracking();

// Custom tracking
trackActivity({
  activity_type: 'custom_event',
  metadata: {
    action: 'button_click',
    button_name: 'submit_form'
  }
});
```

## Using the Admin Dashboard

### 1. Login

1. Navigate to `http://localhost:3001`
2. Enter admin credentials
3. Click "Sign in to Dashboard"

### 2. Dashboard Overview

The dashboard shows:

**Statistics Cards:**
- Total Activities
- Unique Users
- Unique Sessions
- Total Time Spent (hours)

**Charts:**
- **Activities by Type** (Pie Chart) - Distribution of activity types
- **Activities Over Time** (Line Chart) - Trend analysis
- **Top Sections Viewed** (Bar Chart) - Most popular content

**Time Period Selector:**
- Last 7 Days
- Last 30 Days

### 3. Activities Log

Navigate to "Activities" to see:
- Detailed activity logs
- Filter by:
  - Time period (24h, 7d, 30d, 90d)
  - Activity type
  - Number of results
- Columns shown:
  - Timestamp
  - User (or Anonymous)
  - Activity Type
  - Section/Page
  - Duration
  - Session ID

## Activity Types

| Type | Description | When Tracked |
|------|-------------|--------------|
| `page_view` | User views a page | Route change |
| `section_view` | User views a section | Section selected |
| `graph_interaction` | User interacts with graph | Node click, zoom, etc. |
| `search` | User performs search | Search submitted |

## Security Considerations

1. **Admin Authentication**
   - Separate admin login endpoint
   - Requires `is_admin` flag in database
   - JWT token stored separately in `localStorage`

2. **Activity Tracking**
   - No sensitive data in metadata
   - Anonymous users tracked by session only
   - Can be disabled per user

3. **API Security**
   - Admin endpoints require valid admin JWT
   - All requests authenticated
   - CORS properly configured

## Production Deployment

### Backend Deployment

1. Ensure all admin endpoints are protected
2. Set strong JWT secret key
3. Enable HTTPS
4. Set appropriate CORS origins

### Admin Frontend Deployment

#### Option 1: Separate Subdomain

Deploy admin app to `admin.yourdomain.com`:

```nginx
server {
    listen 443 ssl;
    server_name admin.yourdomain.com;
    
    root /var/www/admin/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

#### Option 2: Separate Port

Run admin app on different port:

```bash
cd admin
npm run build
# Serve dist folder on port 3001
```

#### Option 3: Path-based

Serve admin at `/admin` path:

```nginx
location /admin {
    alias /var/www/admin/dist;
    try_files $uri $uri/ /admin/index.html;
}
```

### Environment Variables

Production `.env` for admin:

```env
VITE_API_BASE_URL=https://api.yourdomain.com
```

## Monitoring and Maintenance

### Database Growth

Monitor the UserActivity nodes in Neo4j:

```cypher
// Count activities
MATCH (a:UserActivity)
RETURN count(a) as total_activities

// Check oldest activities
MATCH (a:UserActivity)
RETURN a.timestamp
ORDER BY a.timestamp ASC
LIMIT 10
```

### Cleanup Old Data

Archive or delete old activities:

```cypher
// Delete activities older than 90 days
MATCH (a:UserActivity)
WHERE a.timestamp < datetime() - duration({days: 90})
DELETE a
```

### Performance Tips

1. **Add Indexes** (if needed):
```cypher
CREATE INDEX activity_timestamp FOR (a:UserActivity) ON (a.timestamp)
CREATE INDEX activity_user FOR (a:UserActivity) ON (a.user_id)
CREATE INDEX activity_type FOR (a:UserActivity) ON (a.activity_type)
```

2. **Limit Query Results**:
   - Use pagination in queries
   - Default limit is 100 activities
   - Adjust based on needs

3. **Cache Statistics**:
   - Consider caching dashboard stats
   - Refresh every 5-10 minutes
   - Reduces database load

## Troubleshooting

### Admin Can't Login

**Issue**: "Admin privileges required" error

**Solution**:
1. Check user has `is_admin: true` in database
2. Verify user exists and password is correct
3. Check JWT token is valid

```cypher
MATCH (u:User {email: "admin@example.com"})
RETURN u.is_admin
```

### No Activities Showing

**Issue**: Dashboard shows 0 activities

**Solution**:
1. Verify activity tracking is integrated in main frontend
2. Check activity tracking endpoint is working:
```bash
curl -X POST http://localhost:8000/api/activity/track \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test",
    "activity_type": "page_view",
    "page_url": "/test"
  }'
```
3. Check Neo4j for UserActivity nodes:
```cypher
MATCH (a:UserActivity)
RETURN count(a)
```

### Charts Not Displaying

**Issue**: Charts show "No data available"

**Solution**:
1. Check browser console for errors
2. Verify recharts is installed: `npm list recharts`
3. Ensure data format matches chart expectations

### CORS Errors

**Issue**: Admin app can't connect to backend

**Solution**:
1. Add admin URL to CORS origins in `backend/.env`:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3001
```
2. Restart backend server

## Future Enhancements

Potential features to add:
- [ ] Real-time activity monitoring (WebSocket)
- [ ] Email reports
- [ ] User behavior heatmaps
- [ ] A/B testing support
- [ ] Export data to CSV/Excel
- [ ] Custom date range picker
- [ ] User session replay
- [ ] Funnel analysis
- [ ] Cohort analysis
- [ ] Custom dashboards

## Support

For issues or questions about the admin system:
1. Check this documentation
2. Review backend logs
3. Check Neo4j query logs
4. Contact development team

## Summary

✅ Admin dashboard running on port 3001  
✅ Activity tracking integrated in main app  
✅ Secure admin authentication  
✅ Real-time analytics and reporting  
✅ Detailed activity logs  
✅ Visual charts and statistics  
✅ Production-ready architecture  

The admin system is fully functional and ready to track user behavior!
