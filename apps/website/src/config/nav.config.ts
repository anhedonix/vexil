/**
 * Navigation Configuration
 *
 * Defines navigation menus for the site. Astro handles routing via the
 * filesystem — this only controls which links appear in nav menus.
 *
 * - `navItems`       → main (header) navigation
 * - `footerNavItems` → footer navigation, configured independently from
 *                      the header so you can show different links in the
 *                      footer (e.g. add a Privacy link, drop About, etc.)
 * - `legalLinks`     → small legal-style links (Privacy, Terms, Imprint…)
 *                      shown in the footer's bottom row when supported
 *                      by the active footer layout.
 */

export interface NavItem {
  label: string;
  href: string;
  order: number;
  external?: boolean;
}

export interface LegalLink {
  label: string;
  href: string;
}

export const navItems: NavItem[] = [
  // { label: 'Blog', href: '/blog', order: 1 },
  // { label: 'Projects', href: '/projects', order: 2 },
  // { label: 'About', href: '/about', order: 3 },
  // { label: 'Contact', href: '/contact', order: 1 },
];

export const footerNavItems: NavItem[] = [
  // { label: 'Blog', href: '/blog', order: 1 },
  // { label: 'Projects', href: '/projects', order: 2 },
  // { label: 'About', href: '/about', order: 3 },
  // { label: 'Contact', href: '/contact', order: 1 },
];

export const legalLinks: LegalLink[] = [];

/**
 * Get header navigation items sorted by order
 */
export function getNavItems(): NavItem[] {
  return [...navItems].sort((a, b) => a.order - b.order);
}

/**
 * Get footer navigation items sorted by order.
 * Configured independently from the header — edit `footerNavItems`
 * above to add/remove links in the footer only.
 */
export function getFooterNavItems(): NavItem[] {
  return [...footerNavItems].sort((a, b) => a.order - b.order);
}

/**
 * Get configured legal links (Privacy, Terms, etc.).
 * Returned as-is — order matches declaration order.
 */
export function getLegalLinks(): LegalLink[] {
  return [...legalLinks];
}
