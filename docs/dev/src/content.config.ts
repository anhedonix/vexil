import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

export const collections = {
	docs: defineCollection({
		loader: docsLoader(),
		schema: docsSchema({
			extend: z.object({
				banner: z.object({ content: z.string() }).default({
					content:
						'<strong>Pre-MVP (v0.1.0)</strong> — Expect breaking changes, including complete restructuring based on feasibility. Version stays at <strong>0.1.0</strong> until a working MVP is up.',
				}),
			}),
		}),
	}),
};
