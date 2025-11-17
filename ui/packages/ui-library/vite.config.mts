import { resolve } from 'path'
import vue from '@vitejs/plugin-vue'
import { UserConfig, defineConfig } from 'vite'
import svgLoader from 'vite-svg-loader'

// eslint-disable-next-line import/no-default-export
export default defineConfig(() => {
  const baseConfig = {
    resolve: {
      alias: [
        {
          find: '@',
          replacement: resolve(__dirname, 'src'),
        },
      ],
    },
    plugins: [vue(), svgLoader()],
    test: {
      globals: true,
      environment: 'jsdom',
    },
    build: {
      emptyOutDir: true,
      outDir: 'dist',
      sourcemap: true,
      lib: {
        entry: 'src/index.ts',
        name: 'ui-library',
      },
      rollupOptions: {
        external: [
          'vue',
          'vue-router',
          'vee-validate',
          '@syncmatrix/vue-compositions',
          '@syncmatrix/design',
          '@syncmatrix/vue-charts',
        ],
        output: {
          exports: 'named',
          // Provide vue as a global variable to use in the UMD build
          globals: {
            vue: 'Vue',
          },
        },
      },
    },
  } satisfies UserConfig

  return baseConfig
})