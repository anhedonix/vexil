# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.3.0] — 2026-05-11

### Added

- **Native opt-in i18n** — internationalization is now built into the theme itself, no upstream CLI required. Locale-prefixed routes, a `LanguageSwitcher` dropdown in the header and mobile menu, `hreflang` alternates emitted from the SEO component, and a `t()` translation helper backed by JSON dictionaries (`src/i18n/<locale>.json`). English and Dutch ship out of the box; add more locales by editing `src/config/i18n.config.ts` and creating `src/i18n/<code>.json`. Resolves [#207](https://github.com/hansmartens68/Astro-Rocket/issues/207).
- **`src/i18n/` module** with `t()`, `localizedPath()`, `swapLocaleInPath()`, `stripLocaleFromPath()`, `getLocaleFromPath()`, `isEnabled()`, and locale helpers. `t()` supports `{name}` placeholder interpolation and falls back to the default locale, then to the key itself, so partial translations are visible but non-fatal.
- **`src/config/i18n.config.ts`** — new config file with master switch (`enabled`), `defaultLocale`, `locales[]`, `localeNames`, and `detectBrowserLocale`. Lives separately from `site.config.ts` so the i18n module can be unit-tested without pulling in `astro:env/server`.
- **`LanguageSwitcher.astro`** — accessible pill dropdown with a globe icon, BCP 47 locale code, and full locale names. Pure HTML `<a hreflang lang>` links built via `swapLocaleInPath()` — no framework hydration, ~1 KB of inline JS for open/close. Renders nothing when i18n is disabled.
- 10 new unit tests covering `t()` lookup, fallback, interpolation, locale validation, and `localizedPath()`.

### Changed

- `Header` now shows `LanguageSwitcher` by default when i18n is enabled (the existing `showLanguageSwitcher` prop now defaults to `i18nIsEnabled()` instead of `undefined`, so it auto-shows on multi-locale sites).
- `MarketingLayout` drops the hardcoded `showLanguageSwitcher={false}` override so it inherits the new smart default.
- `astro.config.mjs` conditionally enables Astro's native `i18n` option only when the flag is on and at least two locales are configured. Default routing matches existing behavior (`prefixDefaultLocale: false`).
- README's i18n section rewritten: the Velocity CLI is no longer the recommended path. The warning that it overwrites existing directories remains, as a footnote for anyone who still wants to try it.

### Performance

Verified zero output-size delta with i18n disabled (the default):

|                | i18n off (1.3.0)  | i18n off (1.2.1)  |
|----------------|-------------------|-------------------|
| `dist/` size   | 12 M              | 12 M              |
| Files          | 80                | 80                |
| `hreflang`     | 0                 | 0 (didn't exist)  |
| LanguageSwitcher | 0 instances     | n/a               |

The new code paths are gated on `i18nIsEnabled()`, which returns `false` whenever the flag is off OR `locales.length === 1`. When that returns false, the LanguageSwitcher wrapping `<div>` is skipped, the `hreflang` block compiles to an empty fragment, and `astro.config.mjs` omits the `i18n` option entirely.

---

## [1.2.1] — 2026-05-10

### Fixed

Six rounds of mobile Lighthouse forced-reflow fixes. The 1.2.0 release introduced the table-of-contents sidebar layout, but mobile performance dropped from 100 to 90-95 due to several layout-read sources surfacing under throttled mobile CPU. Each of the following sources was identified by Lighthouse Insights and addressed:

- **TOC scroll-spy** — replaced `entry.target.getBoundingClientRect()` inside the `IntersectionObserver` callback with the cached `entry.boundingClientRect`, which the entry already exposes. Eliminated ~200ms of forced reflow on blog post pages. (#258)
- **Hero H1 font-swap CLS** — added explicit `@font-face` declarations after the `@fontsource-variable` imports overriding `font-display` to `optional`. With the existing `<link rel="preload">` in `BaseLayout` the font usually arrives in the 100ms block window; otherwise the fallback stays for the page lifetime, eliminating the swap-induced shift. Reduced CLS from 0.197 → near zero on the homepage H1. (#258)
- **Back-to-top progress ring** — cached `docMaxScrollY` instead of reading `document.documentElement.scrollHeight` on every scroll frame. (#258, #259)
- **LetterGlitch CTA** — cached canvas width/height in a ref instead of calling `getBoundingClientRect()` on every animation frame. Removed ~215ms of per-frame reflow. (#260)
- **`docMaxScrollY` cache strategy** — initial round wrapped the `ResizeObserver`-driven read in `requestAnimationFrame` (#261), then dropped the `ResizeObserver` entirely (#262) once it became clear that other scripts queue layout writes between the observer firing and rAF execution. resize + load events are sufficient.
- **Initial `scrollHeight` read at script init** — deferred to `DOMContentLoaded` instead of running during HTML parsing, when the document hasn't been fully laid out and the read forces a synchronous layout for the partial DOM. (#263)

After all six fixes the mobile Lighthouse score returns to **100** (with normal 92-100 run-to-run variance from CPU throttling); desktop stays at a steady **100/100/100/100**.

---

## [1.2.0] — 2026-05-09

### Added

- **Table of contents layout option** — `articleFeatures.toc.layout` accepts `'inline'` (current default — card at top of article), `'sidebar'` (sticky sidebar to the right on `xl+` viewports, hidden below), or `'auto'` (sidebar on `xl+`, inline card below `xl`). The article column stays at `max-w-4xl` in every layout, so reading width never changes when the sidebar appears or disappears. Per-post `toc: false` override and `IntersectionObserver` scroll-spy work identically across all three layouts. Default stays `'inline'` so existing sites are unchanged on upgrade. See [Table of Contents — Reading Anchors for Long Posts](src/content/blog/en/table-of-contents.mdx) for setup. The Astro Rocket demo site uses `'auto'`.
- Conditional `<link rel="preconnect" href="https://giscus.app">` in `BaseLayout` when `articleFeatures.comments.enabled` is `true` — warms the DNS+TLS handshake before the lazy-loaded Giscus iframe fires.

### Changed

- **Brand accent shifted from `brand-700` to `brand-600` in light mode** for the blog SVG hero background and the mobile hamburger / close icon — completes the 1.1.0 brand-color refresh that previously covered header + footer site name, hero H1, and primary button. Dark mode unchanged.
- Header scroll behaviour and scroll-progress bar are now driven by a single `requestAnimationFrame` callback. All layout reads (`window.scrollY`, etc.) happen before any DOM writes, and `docMaxScrollY` is cached via `ResizeObserver` so the scroll path never reads `scrollHeight` after attribute writes.

### Fixed

- **Forced reflow (~537 ms)** in `Header.astro` flagged by Lighthouse Insights. Two scroll scripts (header scroll-watcher + scroll-progress bar) were running on the same frame: the first wrote attributes, the second then read `scrollHeight` and forced a synchronous layout recompute. Merging the scripts and caching `docMaxScrollY` eliminates the reflow. After the fix the live demo scores 100/100/100/100 on both mobile and desktop.
- **TOC scroll-spy + duplicate `id` in `'auto'` layout** — when both the inline and sidebar TOC are mounted (one hidden via CSS per breakpoint), the scroll-spy script previously bound to the first instance only, leaving the visible TOC without active-section highlighting on desktop. The script now iterates all `[data-toc]` instances and each instance gets a unique `aria-labelledby` heading id.

### Removed

- **Dead `morphToBar` code path.** The prop on `<Header>` and `<LandingLayout>` defaulted to `false` everywhere and was never set to `true`; the entire `initNavMorph` script (~30 lines) ran on every page load only to bail on a failing `querySelector`. Removed the prop from both components, the `data-morph-to-bar` attribute, the `initNavMorph` script + `astro:transitions/client` import, and two associated CSS rules. After removal the Header script bundle is small enough that Astro inlines it directly into the HTML, eliminating the 1.3 s critical-path fetch Lighthouse previously flagged for `Header.astro_ast_…js`.

### Upgrade notes

`articleFeatures.toc.layout` is an additive setting — existing sites pick up the default (`'inline'`) and render exactly as before. To try the new sidebar mode, set `layout: 'sidebar'` (desktop only) or `layout: 'auto'` (sidebar on `xl+`, inline card on phones/tablets) in `site.config.ts`. The brand-color tweaks are visible in light mode on blog index / post pages and the mobile menu — review the diff if you've customized either area.

---

## [1.1.0] — 2026-05-09

### Added

- **Table of contents** on blog posts — auto-generated from MDX headings, with scroll-spy that highlights the active section. Off by default; enable via `articleFeatures.toc.enabled` in `site.config.ts`. Per-post override with `toc: false` in frontmatter. See [Table of Contents — Reading Anchors for Long Posts](src/content/blog/en/table-of-contents.mdx)
- **Comments on blog posts** powered by [Giscus](https://giscus.app) and GitHub Discussions. Off by default; enable via `articleFeatures.comments.enabled` plus four IDs from giscus.app. Lazy-loaded with an IntersectionObserver — readers who don't scroll to the comments pay zero network cost. Per-post override with `comments: false` in frontmatter. See [Comments on Blog Posts — Giscus, Lazy-Loaded](src/content/blog/en/giscus-comments.mdx)
- **Independent footer menu** — `nav.config.ts` now exports `footerNavItems` and `legalLinks` separately from the header `navItems`, so the footer can show different links (Privacy, Imprint, etc.) without touching the main nav. Defaults mirror the existing nav, so existing sites are unchanged. See [Independent Footer Menu — Different Links in Header and Footer](src/content/blog/en/independent-footer-menu.mdx)
- "View all projects" outline button below the project cards on the homepage
- Arrow-right icon on the "More about me" button (homepage about section)

### Changed

- **Brand accent shifted from `brand-700` to `brand-600` in light mode** across header site name, footer site name, hero H1, and the primary button. Header and footer logo backgrounds now use `bg-brand-600` in both light and dark mode. Primary button hover shifted from `brand-800` to `brand-700` to keep the one-step-darker progression.
- Floating header (homepage) nav links now render at full opacity instead of `opacity-80` with a hover bump.
- Homepage Blog section header is now centered (matching Services, Testimonials, etc.); the inline desktop "View all posts" link was removed and replaced with a single always-visible "View all posts" outline button below the blog cards.
- "Read the full story" button on the About page is now an outline button.

### Removed

- "My Stack" section on the homepage. The `TechStack` component itself is still available for users who want to drop it into their own pages. The four sections that followed (Lighthouse, About Teaser, Blog, CTA) had their backgrounds flipped so the alternating zebra pattern continues unbroken.

### Upgrade notes

The brand-color refresh and homepage layout changes are visible after upgrading. If you've customized either, review the diff before merging — the new opt-in features (TOC, comments, footer config) are all off by default and won't change anything until you flip the switch in `site.config.ts`.

---

## [1.0.0] — 2026-04-04

Initial public release of Astro Rocket.

### Added

- Production-ready Astro 6 starter theme built on Tailwind CSS v4 and TypeScript
- 57 UI and pattern components (buttons, forms, cards, badges, inputs, selects, etc.)
- 12 live colour themes (Orange, Amber, Lime, Emerald, Teal, Cyan, Sky, Blue, Indigo, Violet, Purple, Magenta) switchable at runtime without a rebuild
- Full blog with MDX support, syntax highlighting (Shiki), and RSS feed
- Auto-generated SVG favicon and monogram logo badge from `site.config.ts`
- Unified `Icon` component via Iconify (350+ Lucide icons + 3000+ Simple Icons)
- Animated typing effect in hero section
- Contact form with Zod validation, honeypot bot detection, and Resend integration
- Newsletter signup form with Resend Audiences integration
- Cookie consent banner with Google Consent Mode v2 support
- Google Analytics 4 and Google Tag Manager integration (consent-aware)
- Built-in SEO layer: JSON-LD structured data, Open Graph, sitemap, robots.txt
- Dark mode via `sessionStorage` (resets to dark on each new session)
- Search powered by Pagefind
- Multiple deployment targets: Vercel, Netlify, Cloudflare Pages
- Security headers configured for all deployment targets
- GitHub Actions CI/CD workflow (lint, type-check, build)
- Vitest unit tests for API endpoint validation schemas

### Changed (from Velocity)

- Forked and extended [Velocity](https://github.com/southwellmedia/velocity) by Southwell Media
- Added theme switching, 12 colour themes, typed logo badge, auto favicon
- Replaced localStorage with sessionStorage for dark mode preference
- Added blog image gradients that update with the active theme
- Upgraded icon system to Iconify
- Targeted at complete, ready-to-launch sites rather than a bare boilerplate
