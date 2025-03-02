# iBackupper Frontend

This is the frontend for the iBackupper application, built with Svelte, TypeScript, Vite, and Tailwind CSS.

## Development

To run the development server:

```bash
# Install dependencies
npm install

# Start the development server
./run_dev.sh
# or
npm run dev
```

The development server will run on http://localhost:5173 and proxy API requests to the backend server running on http://localhost:8001.

## Building for Production

To build the application for production:

```bash
# Install dependencies
npm install

# Build the application
./build.sh
# or
npm run build
```

The built files will be in the `dist` directory.

## Project Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── components/     # Svelte components
│   │   ├── icons/          # Icon components
│   │   ├── stores/         # Svelte stores for state management
│   │   ├── types/          # TypeScript interfaces
│   │   └── api.ts          # API client functions
│   ├── App.svelte          # Main application component
│   ├── app.css             # Global styles
│   └── main.ts             # Application entry point
├── public/                 # Static assets
├── index.html              # HTML template
├── vite.config.ts          # Vite configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## Features

- View connected iOS devices
- Create and manage backups
- Schedule automatic backups
- Monitor backup tasks
