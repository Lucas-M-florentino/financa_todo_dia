import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,  // ou qualquer outra porta que esteja usando
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:3001',  // Porta onde seu NestJS está rodando
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),  // Remove '/api' do caminho da requisição
      }
    }
  },
  plugins: [
    vue(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
})
