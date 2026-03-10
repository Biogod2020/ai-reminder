import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    watch: {
      usePolling: true, // 强制轮询文件系统，防止缓存
    },
    hmr: {
      overlay: true,
    }
  },
  optimizeDeps: {
    force: true, // 强制重新构建依赖缓存
  }
})
