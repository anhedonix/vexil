import { defineConfig } from 'astro/config';
import icon from 'astro-icon';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';
import netlify from '@astrojs/netlify';

const isNetlify = process.env.DEPLOY_TARGET === 'netlify';

export default defineConfig({
  output: 'static',
  adapter: isNetlify ? netlify() : vercel(),
  site: process.env.SITE_URL || 'https://vexil.dev',
  integrations: [icon()],
  vite: { plugins: [tailwindcss()] },
});
