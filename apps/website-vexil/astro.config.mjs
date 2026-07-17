import { defineConfig, envField } from 'astro/config';
import icon from 'astro-icon';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';
import netlify from '@astrojs/netlify';

import favicons from 'astro-favicons';

const isNetlify = process.env.DEPLOY_TARGET === 'netlify';

export default defineConfig({
  output: 'server',
  adapter: isNetlify ? netlify() : vercel(),
  site: process.env.SITE_URL || 'https://vexil.dev',
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