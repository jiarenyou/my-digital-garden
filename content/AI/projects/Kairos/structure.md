# Project Structure & Organization

## Root Level
```
Kairos/
├── src/                    # Frontend React application
├── backend/               # Backend Express API server
├── public/                # Static assets served by Vite
├── assets/                # Project assets (icons, images)
├── docs/                  # Documentation and research
├── .kiro/                 # Kiro AI assistant configuration
├── package.json           # Frontend dependencies and scripts
├── vite.config.js         # Vite build configuration
├── index.html             # Main HTML template
└── start-demo.js          # Demo startup script
```

## Frontend Structure (`src/`)
```
src/
├── App.jsx               # Main application component with routing
├── main.jsx              # React application entry point
├── components/           # Reusable React components
├── pages/                # Page-level components (HomePage, HeatmapPage, RecordPage)
├── services/             # API service functions and HTTP clients
├── styles/               #