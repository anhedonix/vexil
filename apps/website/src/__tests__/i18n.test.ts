import { describe, it, expect } from 'vitest';
import { t, localizedPath, resolveLocale, isValidLocale, getLocaleName } from '../i18n';

describe('i18n t() helper', () => {
  it('returns a translation for a valid dotted key', () => {
    expect(t('common.readMore', 'en')).toBe('Read more');
  });

  it('returns the Dutch translation when locale is nl', () => {
    expect(t('common.readMore', 'nl')).toBe('Lees meer');
  });

  it('falls back to the default-locale string when the locale has no entry', () => {
    // 'de' has no dictionary loaded yet — should fall back to English
    expect(t('common.readMore', 'de')).toBe('Read more');
  });

  it('returns the key itself when no translation exists in any dictionary', () => {
    expect(t('some.missing.key', 'en')).toBe('some.missing.key');
  });

  it('interpolates {placeholder} variables', () => {
    expect(t('blog.readingTime', 'en', { minutes: 5 })).toBe('5 min read');
    expect(t('blog.readingTime', 'nl', { minutes: 5 })).toBe('5 min leestijd');
  });

  it('leaves unknown placeholders untouched', () => {
    expect(t('blog.readingTime', 'en', {})).toBe('{minutes} min read');
  });
});

describe('i18n localizedPath()', () => {
  it('returns the path unchanged when i18n is disabled (single locale)', () => {
    // With default config (locales: ['en']), i18n is effectively off
    expect(localizedPath('/about')).toBe('/about');
    expect(localizedPath('/')).toBe('/');
    expect(localizedPath('blog/hello')).toBe('/blog/hello');
  });
});

describe('i18n locale helpers', () => {
  it('resolves an unknown locale to the default', () => {
    expect(resolveLocale('xx')).toBe('en');
    expect(resolveLocale(undefined)).toBe('en');
  });

  it('validates a configured locale', () => {
    expect(isValidLocale('en')).toBe(true);
    expect(isValidLocale('xx')).toBe(false);
    expect(isValidLocale(undefined)).toBe(false);
  });

  it('returns the display name when configured, otherwise the code', () => {
    expect(getLocaleName('en')).toBe('English');
    // 'nl' is in localeNames even though it's not in the active locales list
    expect(getLocaleName('nl')).toBe('Nederlands');
    expect(getLocaleName('xx')).toBe('xx');
  });
});
