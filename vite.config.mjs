import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://raspberry:5001',
        changeOrigin: true,
        secure: false, // This allows for self-signed certificates or localhost
        logLevel: 'debug'
      }
    }
  }
});