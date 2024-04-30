import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  build: {
    outDir: '../../app/static/data-search-svelte',
     rollupOptions: {
       output: {
         entryFileNames: `[name].js`,
         chunkFileNames: `[name].js`,
         assetFileNames: `[name].[ext]`
       }
     },
    //sourcemap: (process.env.NODE_ENV === 'development') ? 'inline' : false,
  }
})
