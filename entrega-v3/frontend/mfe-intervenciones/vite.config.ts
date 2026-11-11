import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Cada remote se publica como UN módulo ES que registra un custom element (Web Component).
export default defineConfig(({ command }) => ({
  plugins: [react()],
  define: command === 'build' ? { 'process.env.NODE_ENV': '"production"' } : {},
  build: { lib: { entry: 'src/main.tsx', formats: ['es'], fileName: () => 'mfe-intervenciones.js' }, cssCodeSplit: false },
  test: { environment: 'jsdom', globals: true, setupFiles: ['./src/setup-tests.ts'] },
}));
