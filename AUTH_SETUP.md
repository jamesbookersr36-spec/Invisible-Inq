# Authentication Setup Guide

This guide explains how to set up and configure the authentication system including user registration, login, and Google Sign-in.

## Features

- ✅ User registration with email and password
- ✅ User login with email and password
- ✅ Google OAuth Sign-in
- ✅ JWT-based authentication
- ✅ Protected routes
- ✅ User profile management
- ✅ Secure password hashing with bcrypt
- ✅ Persistent authentication (stored in localStorage)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

The following new packages have been added:
- `passlib[bcrypt]` - Password hashing
- `python-jose[cryptography]` - JWT token management
- `google-auth` - Google OAuth verification
- `google-auth-oauthlib` - Google OAuth flows
- `pydantic-settings` - Settings management

### 2. Configure Environment Variables

Update your `.env` file (or create one from `env.example`):

```env
# Authentication Configuration
JWT_SECRET_KEY=your-secret-key-change-this-in-production-use-openssl-rand-hex-32
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

**Important:** Generate a secure JWT secret key:
```bash
openssl rand -hex 32
```

### 3. Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "OAuth 2.0 Client ID"
6. Configure OAuth consent screen
7. Add authorized JavaScript origins:
   - `http://localhost:5173` (for development)
   - Your production domain
8. Add authorized redirect URIs:
   - `http://localhost:5173` (for development)
   - Your production domain
9. Copy the Client ID and Client Secret to your `.env` file

### 4. Database Setup

The authentication system uses Neo4j to store user data. User nodes are created with the following structure:

```cypher
(:User {
  email: string,
  full_name: string,
  hashed_password: string (nullable for Google users),
  profile_picture: string (nullable),
  auth_provider: "local" | "google",
  is_active: boolean,
  created_at: datetime,
  updated_at: datetime
})
```

No manual database setup is required - user nodes are created automatically during registration.

### 5. API Endpoints

The following authentication endpoints are available:

#### Register
- **POST** `/api/auth/register`
- Body: `{ email, password, full_name }`
- Returns: `{ access_token, token_type, user }`

#### Login
- **POST** `/api/auth/login`
- Body: `{ email, password }`
- Returns: `{ access_token, token_type, user }`

#### Google OAuth
- **POST** `/api/auth/google`
- Body: `{ credential }` (Google ID token)
- Returns: `{ access_token, token_type, user }`

#### Get Current User
- **GET** `/api/auth/me`
- Headers: `Authorization: Bearer <token>`
- Returns: User object

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

The following new packages have been added:
- `@react-oauth/google` - Google OAuth integration
- `jwt-decode` - JWT token decoding

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000

# Google OAuth Client ID (same as backend)
VITE_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
```

### 3. Project Structure

New files added:
- `src/contexts/AuthContext.jsx` - Authentication context and hooks
- `src/pages/LoginPage.jsx` - Login page
- `src/pages/RegisterPage.jsx` - Registration page
- `src/components/common/ProtectedRoute.jsx` - Protected route wrapper

Updated files:
- `src/App.jsx` - Added auth providers and routes
- `src/components/layout/Header.jsx` - Added user menu

### 4. Usage

#### Using Authentication in Components

```jsx
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();

  // Check if user is authenticated
  if (isAuthenticated()) {
    return <div>Welcome {user.full_name}!</div>;
  }

  return <div>Please log in</div>;
}
```

#### Creating Protected Routes

```jsx
import ProtectedRoute from './components/common/ProtectedRoute';

// In your routes:
<Route path="/dashboard" element={
  <ProtectedRoute>
    <DashboardPage />
  </ProtectedRoute>
} />
```

#### Making Authenticated API Requests

```jsx
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { getToken } = useAuth();

  const fetchData = async () => {
    const token = getToken();
    const response = await fetch('http://localhost:8000/api/protected-endpoint', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const data = await response.json();
    return data;
  };
}
```

## Testing

### Backend Testing

1. Start the backend server:
```bash
cd backend
python main.py
```

2. Test registration:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "full_name": "Test User"}'
```

3. Test login:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Frontend Testing

1. Start the frontend:
```bash
npm run dev
```

2. Navigate to `http://localhost:5173`
3. Try the following:
   - Register a new account at `/register`
   - Log in at `/login`
   - Try Google Sign-in
   - Check user menu in header
   - Log out

## Security Considerations

1. **JWT Secret Key**: Always use a strong, randomly generated secret key in production
2. **HTTPS**: Use HTTPS in production for secure token transmission
3. **Token Expiration**: Tokens expire after 30 days by default (configurable)
4. **Password Requirements**: Minimum 6 characters (can be increased)
5. **CORS**: Configure proper CORS origins for production
6. **Environment Variables**: Never commit `.env` files to version control

## Troubleshooting

### Backend Issues

**"GOOGLE_CLIENT_ID not configured"**
- Make sure you've added `GOOGLE_CLIENT_ID` to your `.env` file

**"Database connection failed"**
- Verify Neo4j is running and credentials are correct

**"JWT decode error"**
- Check that `JWT_SECRET_KEY` is set and consistent

### Frontend Issues

**Google Sign-in button not showing**
- Verify `VITE_GOOGLE_CLIENT_ID` is set in `.env`
- Make sure the domain is authorized in Google Cloud Console
- Check browser console for errors

**"Network error during login"**
- Verify backend is running on `http://localhost:8000`
- Check `VITE_API_BASE_URL` in `.env`
- Check browser console for CORS errors

**User not persisting after refresh**
- Check if token is stored in localStorage
- Verify token hasn't expired
- Check for JWT decode errors in console

## Production Deployment

1. Generate a strong JWT secret key
2. Set up HTTPS
3. Configure proper CORS origins
4. Update Google OAuth authorized domains
5. Set appropriate token expiration times
6. Enable rate limiting on auth endpoints
7. Set up proper logging and monitoring
8. Consider adding email verification
9. Consider adding password reset functionality
10. Consider adding 2FA (Two-Factor Authentication)

## Future Enhancements

- [ ] Email verification
- [ ] Password reset functionality
- [ ] Two-factor authentication (2FA)
- [ ] Social login with other providers (Facebook, Twitter, etc.)
- [ ] Session management (logout from all devices)
- [ ] User profile editing
- [ ] Account deletion
- [ ] Role-based access control (RBAC)

## Support

For issues or questions, please contact the development team or create an issue in the project repository.
