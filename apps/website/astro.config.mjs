import { defineConfig, envField } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import react from '@astrojs/react';
import icon from 'astro-icon';
import tailwindcss from '@tailwindcss/vite';
import vercel from '@astrojs/vercel';
import netlify from '@astrojs/netlify';
import i18nConfig from './src/config/i18n.config.ts';

const isNetlify = process.env.DEPLOY_TARGET === 'netlify';

/**
 * Native Astro i18n is only wired up when the user opts in *and* has
 * more than one locale configured. With i18n off (the default) this
 * block is undefined and the build emits the exact same routes as
 * before — no /en/ prefix, no extra pages.
 */
const i18nEnabled = i18nConfig.enabled === true && i18nConfig.locales.length > 1;
const astroI18nOptions = i18nEnabled
  ? {
      defaultLocale: i18nConfig.defaultLocale,
      locales: i18nConfig.locales,
      routing: {
        prefixDefaultLocale: false,
        redirectToDefaultLocale: false,
      },
    }
  : undefined;

export default defineConfig({
  output: 'static',
  adapter: isNetlify ? netlify() : vercel(),
  site: process.env.SITE_URL || 'https://example.com',
  ...(astroI18nOptions ? { i18n: astroI18nOptions } : {}),

  build: {
    inlineStylesheets: 'always',
  },

  env: {
    schema: {
      SITE_URL: envField.string({ context: 'server', access: 'public', optional: true }),
      PUBLIC_GA_MEASUREMENT_ID: envField.string({ context: 'client', access: 'public', optional: true }),
      PUBLIC_GTM_ID: envField.string({ context: 'client', access: 'public', optional: true }),
      RESEND_API_KEY: envField.string({ context: 'server', access: 'secret', optional: true }),
      RESEND_FROM_EMAIL: envField.string({ context: 'server', access: 'secret', optional: true }),
      NEWSLETTER_API_KEY: envField.string({ context: 'server', access: 'secret', optional: true }),
      GOOGLE_SITE_VERIFICATION: envField.string({ context: 'server', access: 'public', optional: true }),
      BING_SITE_VERIFICATION: envField.string({ context: 'server', access: 'public', optional: true }),
      PUBLIC_GOOGLE_MAPS_API_KEY: envField.string({ context: 'client', access: 'public', optional: true, default: '' }),
      PUBLIC_CONSENT_ENABLED: envField.boolean({ context: 'client', access: 'public', optional: true, default: false }),
      PUBLIC_PRIVACY_POLICY_URL: envField.string({ context: 'client', access: 'public', optional: true, default: '' }),
    },
  },

  image: {
    layout: 'constrained',
  },

  integrations: [
    react(),
    mdx(),
    sitemap(),
    icon(),
  ],

  vite: {
    plugins: [tailwindcss()],
  },

  security: {
    checkOrigin: true,
  },

  markdown: {
    shikiConfig: {
      theme: 'github-dark',
      wrap: true,
    },
  },

});
