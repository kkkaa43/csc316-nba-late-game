import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// GitHub Pages serves the site from /<repo-name>/. The deploy workflow sets
// BASE_PATH=/csc316-nba-late-game; local `npm run dev` leaves it empty.
const base = process.env.BASE_PATH ?? '';

export default {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({ fallback: '404.html' }),
    paths: { base }
  }
};
