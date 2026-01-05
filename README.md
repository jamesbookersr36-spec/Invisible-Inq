# MVP Graph Visualization App

## Project Overview
This is an interactive graph visualization web application that allows users to explore relationships between entities in various stories.

## Features
- Interactive 3D graph visualization using Three.js and ForceGraph3D
- Multiple story selection with entity highlighting
- Responsive layout with collapsible sidebars
- Detailed node and edge information display
- Customizable graph parameters

## Installation
```bash
# Clone the repository
git clone [repository URL]

# Navigate to the project directory
cd [project directory]

# Install dependencies
npm install
```

## Usage
```bash
# Run the development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment on Vercel
This project is configured for easy deployment on Vercel:

1. Push your code to a GitHub repository
2. Connect the repository to Vercel
3. Vercel will automatically detect the Vite configuration
4. The deployment will handle client-side routing correctly

Alternatively, you can deploy directly from the command line:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy to Vercel
vercel
```

## Project Structure
- `/public/data` - Contains story data in JSON format
- `/src/components` - React components organized by feature
- `/src/pages` - Page components for different routes
- `/src/hooks` - Custom React hooks
- `/src/utils` - Utility functions

## License
[License information]
"# Invisible-Inq" 
