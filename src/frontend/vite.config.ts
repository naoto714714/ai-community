import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './tests/frontend/setup.ts',
    css: true,
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
});
