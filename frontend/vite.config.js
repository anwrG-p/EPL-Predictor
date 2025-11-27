import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// Expose only non-sensitive environment variables to the frontend
const env = loadEnv('', process.cwd(), 'VITE_');

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true, // Needed for Docker
  },
  define: {
    // Only expose a small set of env vars starting with VITE_ to the React code
    'settings.VITE_MODEL_TYPE': JSON.stringify(env.VITE_MODEL_TYPE),
    'settings.VITE_ADMIN_EMAIL': JSON.stringify(env.VITE_ADMIN_EMAIL),
  }
})
