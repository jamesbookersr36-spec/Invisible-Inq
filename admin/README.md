# Admin Dashboard

This is the administrator dashboard for the Invisible Injury project. It provides real-time analytics and user activity tracking.

## Features

- 📊 **Analytics Dashboard** - Visual statistics with charts
- 👥 **User Activity Logs** - Detailed activity tracking
- 📈 **Real-time Monitoring** - Track user behavior
- 🔒 **Secure Access** - Admin-only authentication

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

Create a `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The admin dashboard will be available at: **http://localhost:3001**

### 4. Build for Production

```bash
npm run build
```

## Project Structure

```
admin/
├── src/
│   ├── components/
│   │   ├── Layout.jsx          # Main layout with sidebar
│   │   └── ProtectedRoute.jsx  # Route protection
│   ├── contexts/
│   │   └── AuthContext.jsx     # Admin authentication
│   ├── pages/
│   │   ├── LoginPage.jsx       # Admin login
│   │   ├── DashboardPage.jsx   # Analytics dashboard
│   │   └── ActivitiesPage.jsx  # Activity logs
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## First Time Setup

Before you can use the admin dashboard, you need to create an admin user. See the main [ADMIN_SETUP.md](../ADMIN_SETUP.md) for instructions.

## Dashboard Features

### Analytics Dashboard
- Total activities count
- Unique users count
- Unique sessions count
- Total time spent
- Activities by type (pie chart)
- Activities over time (line chart)
- Top sections viewed (bar chart)
- Time period selector (7 days / 30 days)

### Activities Log
- Real-time activity tracking
- Filter by time period
- Filter by activity type
- Filter by results limit
- Detailed activity information:
  - Timestamp
  - User info (or Anonymous)
  - Activity type
  - Section/Page
  - Duration
  - Session ID

## Technology Stack

- **React 19** - UI library
- **React Router DOM** - Routing
- **Recharts** - Data visualization
- **Tailwind CSS** - Styling
- **date-fns** - Date formatting
- **Vite** - Build tool

## API Endpoints Used

- `POST /api/auth/admin/login` - Admin login
- `GET /api/admin/statistics` - Dashboard statistics
- `GET /api/admin/activities` - Activity logs

## Development

### Running Tests

```bash
npm run test
```

### Linting

```bash
npm run lint
```

### Build Optimization

The production build is optimized for:
- Code splitting
- Tree shaking
- Minification
- Asset optimization

## Deployment

### Option 1: Static Hosting

Build and deploy the `dist` folder to any static hosting service:

```bash
npm run build
# Deploy the dist folder
```

### Option 2: Docker

Create `Dockerfile`:

```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:

```bash
docker build -t admin-dashboard .
docker run -p 3001:80 admin-dashboard
```

### Option 3: Nginx

Serve with nginx:

```nginx
server {
    listen 3001;
    server_name admin.yourdomain.com;
    
    root /path/to/admin/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## Troubleshooting

### Can't Login

1. Ensure backend is running
2. Check admin user exists with `is_admin: true`
3. Verify API URL in `.env`

### Charts Not Showing

1. Check browser console for errors
2. Verify data is being returned from API
3. Ensure recharts is installed

### Build Errors

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

## Support

For more information, see the main [ADMIN_SETUP.md](../ADMIN_SETUP.md) documentation.

## License

Same as the main project.
