import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: ['react-plotly.js', 'plotly.js-dist-min', 'ml-pca', 'ml-matrix']
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    fs: {
      strict: false
    },
    hmr: {
      overlay: true
    }
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          'chakra': ['@chakra-ui/react', '@chakra-ui/icons'],
          'plotly': ['plotly.js-dist-min', 'react-plotly.js'],
          'ml': ['ml-pca', 'ml-matrix']
        }
      }
    }
  }
}); 