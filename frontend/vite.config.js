import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const frontendPort = Number(env.VITE_PORT || env.TRUEMARK_FRONTEND_PORT || 3300);

  return {
    plugins: [react()],
    server: {
      host: "0.0.0.0",
      port: frontendPort,
      strictPort: true,
    },
    preview: {
      host: "0.0.0.0",
      port: frontendPort,
      strictPort: true,
    },
  };
});
