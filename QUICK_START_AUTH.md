# Quick Start Guide - Authentication

This is a quick guide to get the authentication system up and running.

## Step 1: Backend Setup

### Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Configure Backend Environment

Create or update `backend/.env`:

```bash
# Minimum required for local auth (without Google)
JWT_SECRET_KEY=$(openssl rand -hex 32)  # Generate a random key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# For Google Sign-in (optional)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### Start Backend

```bash
cd backend
python main.py
```

Backend should be running on `http://localhost:8000`

## Step 2: Frontend Setup

### Install Frontend Dependencies

```bash
npm install
```

This will install the new packages:
- `@react-oauth/google@^0.12.1`
- `jwt-decode@^4.0.0`

### Configure Frontend Environment

Create `.env` in the root directory:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

**Note:** If you don't need Google Sign-in, you can leave `VITE_GOOGLE_CLIENT_ID` empty. The app will still work with email/password authentication.

### Start Frontend

```bash
npm run dev
```

Frontend should be running on `http://localhost:5173`

## Step 3: Test the Authentication

1. Open `http://localhost:5173` in your browser
2. Click "Sign up" in the header
3. Register a new account with:
   - Full Name: Test User
   - Email: test@example.com
   - Password: password123
4. You should be automatically logged in and redirected to the home page
5. Check the header - you should see your user avatar/name
6. Click on your avatar to see the user menu
7. Click "Sign out" to logout

## Google Sign-in Setup (Optional)

If you want to enable Google Sign-in:

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Go to "APIs & Services" > "Credentials"
4. Click "Create Credentials" > "OAuth 2.0 Client ID"
5. Select "Web application"
6. Add Authorized JavaScript origins:
   - `http://localhost:5173`
7. Click "Create"
8. Copy the Client ID

### 2. Update Environment Variables

Backend `.env`:
```env
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
```

Frontend `.env`:
```env
VITE_GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
```

### 3. Restart Both Services

```bash
# Backend
cd backend
python main.py

# Frontend (in another terminal)
npm run dev
```

Now the Google Sign-in button should appear on the login and register pages!

## Verify Installation

Check that these endpoints work:

```bash
# Health check
curl http://localhost:8000/health

# Register a user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

## What's New?

### Backend
- ✅ New auth endpoints: `/api/auth/register`, `/api/auth/login`, `/api/auth/google`, `/api/auth/me`
- ✅ User model stored in Neo4j
- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ Google OAuth support

### Frontend
- ✅ Login page at `/login`
- ✅ Register page at `/register`
- ✅ User authentication context
- ✅ Protected routes component
- ✅ User menu in header with logout
- ✅ Google Sign-in integration

## Next Steps

1. **Protect Your Routes**: Wrap any pages that require authentication with `<ProtectedRoute>`:
   ```jsx
   <Route path="/dashboard" element={
     <ProtectedRoute>
       <DashboardPage />
     </ProtectedRoute>
   } />
   ```

2. **Use Auth in Components**: Access user data and auth functions:
   ```jsx
   import { useAuth } from '../contexts/AuthContext';
   
   function MyComponent() {
     const { user, isAuthenticated } = useAuth();
     // Your component logic
   }
   ```

3. **Make Authenticated Requests**: Include JWT token in API calls:
   ```jsx
   const { getToken } = useAuth();
   const token = getToken();
   
   fetch('/api/protected-endpoint', {
     headers: {
       'Authorization': `Bearer ${token}`
     }
   });
   ```

## Troubleshooting

**Backend won't start:**
- Make sure Neo4j is running
- Check that all environment variables are set
- Verify Python dependencies are installed

**Frontend won't start:**
- Run `npm install` to ensure all dependencies are installed
- Check that `.env` file exists with `VITE_API_BASE_URL`

**Can't register/login:**
- Check backend is running on port 8000
- Check browser console for errors
- Verify Neo4j connection is working

**Google Sign-in not working:**
- Verify `VITE_GOOGLE_CLIENT_ID` is set correctly
- Check domain is authorized in Google Cloud Console
- Make sure both backend and frontend have the same Client ID

For more details, see [AUTH_SETUP.md](./AUTH_SETUP.md)
