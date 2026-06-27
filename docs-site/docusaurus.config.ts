import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'pan-scm-sdk',
  tagline: 'Python SDK for Palo Alto Networks Strata Cloud Manager',
  favicon: 'img/logo.png',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Production url of the site (GitHub Pages).
  url: 'https://cdot65.github.io',
  // The /<baseUrl>/ pathname under which the site is served.
  baseUrl: '/pan-scm-sdk/',

  // GitHub pages deployment config.
  organizationName: 'cdot65',
  projectName: 'pan-scm-sdk',

  onBrokenLinks: 'throw',

  // Parse `.md` files as CommonMark (not MDX) so Python type hints like
  // `List[str]`, brace placeholders like `{folder}`, and raw HTML in the
  // landing page pass through untouched. `.mdx` files still use full MDX.
  markdown: {
    format: 'detect',
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // Docs serve at the site root (mirrors the old MkDocs URLs).
          routeBasePath: '/',
          editUrl: 'https://github.com/cdot65/pan-scm-sdk/tree/main/docs-site/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/logo.png',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'pan-scm-sdk',
      logo: {
        alt: 'pan-scm-sdk',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docs',
          position: 'left',
          label: 'Documentation',
        },
        {
          href: 'https://pypi.org/project/pan-scm-sdk/',
          label: 'PyPI',
          position: 'right',
        },
        {
          href: 'https://github.com/cdot65/pan-scm-sdk',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Services', to: '/sdk/'},
            {label: 'Data Models', to: '/sdk/models/'},
            {label: 'User Guide', to: '/about/introduction'},
          ],
        },
        {
          title: 'Project',
          items: [
            {label: 'GitHub', href: 'https://github.com/cdot65/pan-scm-sdk'},
            {label: 'PyPI', href: 'https://pypi.org/project/pan-scm-sdk/'},
            {label: 'Issues', href: 'https://github.com/cdot65/pan-scm-sdk/issues'},
          ],
        },
      ],
      copyright: `Copyright © 2023-2025 Calvin Remsburg. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['python', 'bash', 'json', 'yaml', 'toml', 'diff'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
