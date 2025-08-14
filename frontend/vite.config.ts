import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': '/src'
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://gateway:8080', // Gateway (Docker service name)
        changeOrigin: true,
        secure: false
      },
      '/health': {
        target: 'http://gateway:8080', // Gateway health (Docker service name)
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})