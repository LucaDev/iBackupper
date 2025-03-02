# iBackupper

A complete solution for managing iPhone backups using pymobiledevice3, with a modern Svelte frontend.

## Project Structure

The project is divided into two main parts:

```
ibackupper/
├── backend/             # Python FastAPI backend
│   ├── api/             # API routes and endpoints
│   ├── core/            # Core functionality
│   ├── ui/              # Legacy UI (HTML templates)
│   └── utils/           # Utility functions
└── frontend/            # Svelte frontend
    ├── src/             # Source code
    │   ├── lib/         # Components, stores, and utilities
    │   ├── App.svelte   # Main application component
    │   └── main.ts      # Application entry point
    └── public/          # Static assets
```

## Features

- List all connected devices (USB and WiFi)
- Create, restore, and delete backups using mobilebackup2
- Support for both incremental and full backups
- Schedule backups with cron expressions
- Modern, responsive UI built with Svelte and Tailwind CSS
- No database required - all data stored in the filesystem

## Backend

The backend is built with Python and FastAPI, providing a REST API for managing iPhone backups.

### Installation

1. Ensure you have Python 3.10+ installed
2. Install the required packages:

```bash
cd backend
pip install -r requirements.txt
```

### Running the Backend

```bash
cd backend
./run_dev.sh
```

The API will be available at http://localhost:8001

## Frontend

The frontend is built with Svelte, TypeScript, Vite, and Tailwind CSS.

### Installation

1. Ensure you have Node.js and npm installed
2. Install the required packages:

```bash
cd frontend
npm install
```

### Running the Frontend

```bash
cd frontend
./run_dev.sh
```

The frontend will be available at http://localhost:5173

## Development

For development, you'll need to run both the backend and frontend servers:

1. Start the backend server:

```bash
cd backend
./run_dev.sh
```

2. In a separate terminal, start the frontend server:

```bash
cd frontend
./run_dev.sh
```

## Building for Production

To build the frontend for production:

```bash
cd frontend
./build.sh
```

The built files will be in the `frontend/dist` directory.

## API Documentation

Once the backend is running, you can access the auto-generated API documentation at:

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
