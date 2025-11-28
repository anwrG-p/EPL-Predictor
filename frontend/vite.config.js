import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import { builtinModules } from 'module'; // Needed to fix Node module resolution errors

// Expose only non-sensitive environment variables to the frontend
const env = loadEnv('', process.cwd(), 'VITE_');

export default defineConfig({
  // Base path for asset loading (use "/" for Docker, "/EPL-Predictor/" for GitHub Pages)
  base: "/", 
  
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Needed for Docker
  },
  
  // Define environment variables to be accessed in React components (e.g., import.meta.env)
  define: {
    'settings.VITE_MODEL_TYPE': JSON.stringify(env.VITE_MODEL_TYPE),
    'settings.VITE_ADMIN_EMAIL': JSON.stringify(env.VITE_ADMIN_EMAIL),
  },

  // Fixes the "basename is not exported" and "fsevents" errors
  build: {
    rollupOptions: {
      external: [
        'fsevents', 
        ...builtinModules, 
        ...builtinModules.map(m => `node:${m}`)
      ], 
    },
  },

  // Optional: Helps with cache issues during development
  optimizeDeps: {
    force: true,
  }
});
