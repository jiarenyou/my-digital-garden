# Technology Stack & Build System

## Frontend Stack
- **Framework**: React 18.2.0 with JSX
- **Build Tool**: Vite 4.1.0 with HMR
- **Routing**: React Router DOM 6.8.0
- **HTTP Client**: Axios 1.3.0
- **Date Handling**: date-fns 2.29.0
- **Styling**: CSS3 (no framework, custom styles)

## Backend Stack
- **Runtime**: Node.js
- **Framework**: Express 4.18.0
- **Database**: MongoDB with Mongoose 7.0.0
- **Environment**: dotenv for configuration
- **CORS**: cors 2.8.5 for cross-origin requests

## Development Tools
- **Dev Server**: Vite dev server with proxy
- **Backend Dev**: nodemon for auto-restart
- **Package Manager**: npm

## Common Commands

### Development
```bash
# Start frontend development server (port 3000)
npm run dev

# Start backend server (port 5000)
npm run server

# Start backend with auto-restart
npm run dev:server

# Full development setup
npm run server & npm run dev
```

### Production
```bash
# Build frontend for production
npm run build

# Preview production build
npm run preview

# Start production backend
npm run start
```

### Setup
```bash
# Install all dependencies
npm install && cd backend && npm install && cd ..

# Copy environment template
cp .env.example .env
```

## Configuration
- **Frontend Port**: 3000 (Vite dev server)
- **Backend Port**: 5000 (Express server)
- **API Proxy**: `/api` routes proxied from frontend to backend
- **Database**: MongoDB (local or MongoDB URI from .env)

## Environment Variables
Required in `.env` file:
- `MONGODB_URI`: MongoDB connection string
- `PORT`: Backend server port (defaults to 5000)