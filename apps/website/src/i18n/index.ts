import en from './en.json';
import nl from './nl.json';
import i18nConfig from '../config/i18n.config';

export { i18nConfig };
export type { I18nConfig } from '../config/i18n.config';

export type Locale = string;

export type Dictionary = typeof en;

const dictionaries: Record<string, Dictionary> = {
  en: en as Dictionary,
  nl: nl as Dictionary,
};

export const defaultLocale: Locale = i18nConfig.defaultLocale;

export function isEnabled(): boolean {
  return i18nConfig.enabled === true && i18nConfig.locales.length > 1;
}

export function getLocales(): Locale[] {
  return i18nConfig.locales;
}

export function getLocaleName(locale: Locale): string {
  return i18nConfig.localeNames?.[locale] ?? locale;
}

export function isValidLocale(locale: string | undefined): locale is Locale {
  if (!locale) return false;
  return i18nConfig.locales.includes(locale);
}

export function resolveLocale(locale: string | undefined): Locale {
  return isValidLocale(locale) ? locale : defaultLocale;
}

function getNested(dict: Dictionary, key: string): string | undefined {
  const parts = key.split('.');
  let value: unknown = dict;
  for (const part of parts) {
    if (value && typeof value === 'object' && part in (value as Record<string, unknown>)) {
      value = (value as Record<string, unknown>)[part];
    } else {
      return undefined;
    }
  }
  return typeof value === 'string' ? value : undefined;
}

function interpolate(template: string, vars?: Record<string, string | number>): string {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (match, name) => {
    const value = vars[name];
    return value !== undefined ? String(value) : match;
  });
}

/**
 * Look up a translation by dotted key. Falls back to the default locale's
 * value, then to the key itself, so missing translations are visible but
 * non-fatal. Supports `{name}` placeholders via `vars`.
 */
export function t(key: string, locale: Locale = defaultLocale, vars?: Record<string, string | number>): string {
  const dict = dictionaries[locale] ?? dictionaries[defaultLocale];
  const fallback = dictionaries[defaultLocale];
  const value = (dict && getNested(dict, key)) ?? (fallback && getNested(fallback, key)) ?? key;
  return interpolate(value, vars);
}

/**
 * Build a locale-prefixed URL. The default locale stays at the root
 * (no prefix) when `prefixDefaultLocale` is false, matching Astro's
 * native i18n routing behavior.
 */
export function localizedPath(path: string, locale: Locale = defaultLocale): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  if (!isEnabled()) return normalized;
  if (locale === defaultLocale) return normalized;
  return `/${locale}${normalized === '/' ? '' : normalized}`;
}

/**
 * Strip a leading `/<locale>` segment from a path if present. Returns
 * the path unchanged when the first segment is not a configured
 * locale. Always returns a path starting with `/`.
 *
 * `/nl/about` → `/about`, `/en` → `/`, `/about` → `/about`.
 */
export function stripLocaleFromPath(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  const match = normalized.match(/^\/([^/]+)(\/.*)?$/);
  if (!match) return normalized;
  const [, first, rest] = match;
  if (i18nConfig.locales.includes(first)) {
    return rest && rest.length > 0 ? rest : '/';
  }
  return normalized;
}

/**
 * Replace the locale segment of a path with a different locale.
 * Used by the LanguageSwitcher to build "same page, other language"
 * links. When the target is the default locale, no prefix is added.
 */
export function swapLocaleInPath(path: string, targetLocale: Locale): string {
  const base = stripLocaleFromPath(path);
  return localizedPath(base, targetLocale);
}

/**
 * Detect the active locale from a path's first segment. Returns the
 * default locale if no recognized locale prefix is present.
 */
export function getLocaleFromPath(path: string): Locale {
  const normalized = path.startsWith('/') ? path : `/${path}`;
  const first = normalized.split('/').filter(Boolean)[0];
  return first && i18nConfig.locales.includes(first) ? first : defaultLocale;
}
