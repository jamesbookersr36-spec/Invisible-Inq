# Admin Dashboard - Quick Start Guide

Get the administrator dashboard up and running in 5 minutes!

## 🎯 What You're Getting

A complete admin dashboard with:
- ✅ User activity tracking
- ✅ Real-time analytics  
- ✅ Visual charts and statistics
- ✅ Hosted on **port 3001** (separate from main app)

## ⚡ Quick Setup (5 Steps)

### Step 1: Install Admin Dependencies

```bash
cd admin
npm install
```

### Step 2: Configure Admin App

Create `admin/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3: Create Your First Admin User

```bash
cd backend
python create_admin.py
```

Follow the prompts:
- Enter email: `admin@example.com`
- Enter password: `admin123` (use a strong password!)
- Enter name: `Admin User`

You should see: ✅ SUCCESS! Admin user created

### Step 4: Start Backend (if not already running)

```bash
cd backend
python main.py
```

Backend runs on **http://localhost:8000**

### Step 5: Start Admin Dashboard

```bash
cd admin
npm run dev
```

Admin dashboard runs on **http://localhost:3001**

## 🔐 Login to Admin Dashboard

1. Open **http://localhost:3001** in your browser
2. Enter your admin credentials
3. Click "Sign in to Dashboard"

You should see the Analytics Dashboard! 🎉

## 📊 What You Can Do

### Dashboard Tab
- View total activities, users, and sessions
- See activity charts (pie, line, bar charts)
- Toggle between 7-day and 30-day periods

### Activities Tab
- View detailed activity logs
- Filter by time period and activity type
- See which users viewed which sections

## 🔧 Integrate Activity Tracking in Main App

To start tracking user activity in your main application:

### Option 1: Add to Existing Pages

```jsx
import { useActivityTracking } from '../hooks/useActivityTracking';

function MyPage() {
  const { trackSectionView } = useActivityTracking();
  
  useEffect(() => {
    // Track when user views this section
    trackSectionView('section-id', 'Section Title');
  }, []);
  
  return <div>Your page content</div>;
}
```

### Option 2: Automatic Tracking

The hook automatically tracks:
- Page views (on every route change)
- Time spent on pages
- Session information

Just import it in your main pages!

## 🧪 Test It Out

1. **Open main app**: http://localhost:5173
2. **Navigate around** the site
3. **Go to admin dashboard**: http://localhost:3001
4. **Check Activities tab** - You should see your activities!

## 📁 Project Structure

```
Invisible-Inq/
├── admin/                    # Admin dashboard (NEW!)
│   ├── src/
│   │   ├── pages/
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ActivitiesPage.jsx
│   │   │   └── LoginPage.jsx
│   │   └── contexts/
│   │       └── AuthContext.jsx
│   └── package.json
│
├── backend/
│   ├── activity_service.py   # NEW! Activity tracking
│   ├── create_admin.py       # NEW! Create admin user
│   └── main.py              # Updated with admin endpoints
│
└── src/
    └── hooks/
        └── useActivityTracking.js  # NEW! Activity tracking hook
```

## 🚀 Next Steps

1. **Create more admin users** - Run `create_admin.py` again
2. **Add tracking to more pages** - Use `useActivityTracking` hook
3. **Customize dashboard** - Edit `DashboardPage.jsx`
4. **Set up production** - See [ADMIN_SETUP.md](ADMIN_SETUP.md)

## ⚠️ Common Issues

### "Admin privileges required"

**Solution**: Make sure you created an admin user with `create_admin.py`

### Admin dashboard won't start

**Solution**: 
```bash
cd admin
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### No activities showing

**Solution**: 
1. Make sure main app is using the activity tracking hook
2. Navigate around the main app first
3. Refresh the admin dashboard

### Can't connect to backend

**Solution**: Check that:
- Backend is running on port 8000
- `VITE_API_BASE_URL` in `admin/.env` is correct
- CORS allows localhost:3001

## 📖 Full Documentation

For detailed information, see:
- [ADMIN_SETUP.md](ADMIN_SETUP.md) - Complete setup guide
- [admin/README.md](admin/README.md) - Admin app documentation

## 💡 Tips

1. **Use Chrome DevTools** to monitor network requests
2. **Check Neo4j Browser** to see UserActivity nodes
3. **Test with multiple browser sessions** to see different users
4. **Use incognito mode** to test anonymous tracking

## 🎨 Customization

Want to customize the admin dashboard?

**Change colors:**
Edit `admin/tailwind.config.js`

**Add new charts:**
Install recharts components and add to `DashboardPage.jsx`

**Add new activity types:**
Define in `backend/models.py` and track in your app

## 📞 Need Help?

1. Check [ADMIN_SETUP.md](ADMIN_SETUP.md) for detailed docs
2. Review backend logs for errors
3. Check browser console for frontend errors
4. Verify Neo4j is running and connected

---

**That's it! Your admin dashboard is ready to use! 🎉**

Access it at: **http://localhost:3001**
