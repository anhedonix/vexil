import { defineConfig, envField } from 'astro/config';
import icon from 'astro-icon';
import tailwindcss from '@tailwindcss/vite';
import favicons from 'astro-favicons';

const isNetlify = process.env.DEPLOY_TARGET === 'netlify';
const { default: adapter } = isNetlify
  ? await import('@astrojs/netlify')
  : await import('@astrojs/vercel');

export default defineConfig({
  output: 'server',
  // Astro 7 defaults to compressHTML: 'jsx', which strips newlines around inline
  // tags and glues words (e.g. "toVector", "aPython"). Use HTML-aware compression.
  compressHTML: true,
  adapter: adapter(),
  site: process.env.SITE_URL || 'https://vexil.tools',
  integrations: [icon(), favicons()],
  vite: { plugins: [tailwindcss()] },
  env: {
    schema: {
      RESEND_API_KEY: envField.string({ context: 'server', access: 'secret', optional: true }),
      RESEND_FROM_EMAIL: envField.string({ context: 'server', access: 'secret', optional: true }),
      RESEND_TO_EMAIL: envField.string({ context: 'server', access: 'secret', optional: true }),
    },
  },
});
