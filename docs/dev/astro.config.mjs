// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://dev-docs.vexil.tools',
	integrations: [
		starlight({
			title: 'Dev Docs | VEXiL',
			logo: {
				src: './src/assets/vexil-logo.png',
				alt: 'VEXiL',
				replacesTitle: true,
			},
			social: [
				{
					icon: 'github',
					label: 'GitHub',
					href: 'https://github.com/anhedonix/vexil',
				},
			],
			customCss: ['./src/styles/custom.css'],
			sidebar: [
				{
					label: 'Guides',
					items: [
						{ label: 'Getting Started', slug: 'guides/getting-started' },
						{ label: 'Repository Structure', slug: 'guides/repository-structure' },
						{ label: 'Contributing', slug: 'guides/contributing' },
					],
				},
				{
					label: 'Reference',
					items: [
						{ label: 'Local services & ports', slug: 'reference/local-services' },
					],
				},
			],
		}),
	],
});
