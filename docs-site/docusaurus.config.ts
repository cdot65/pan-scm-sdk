import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import type {PrismTheme} from 'prism-react-renderer';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

// Gruvbox dark (hard contrast) Prism theme — mirrors the design system's
// syntax tokens. prism-react-renderer applies inline styles, so the syntax
// palette lives here rather than in custom.css.
const gruvboxDark: PrismTheme = {
  plain: {color: '#ebdbb2', backgroundColor: '#282828'},
  styles: [
    {types: ['comment', 'prolog', 'cdata'], style: {color: '#928374', fontStyle: 'italic'}},
    {types: ['punctuation'], style: {color: '#bdae93'}},
    {types: ['keyword', 'tag', 'selector', 'important', 'atrule'], style: {color: '#fb4934'}},
    {types: ['string', 'char', 'attr-value', 'regex'], style: {color: '#b8bb26'}},
    {types: ['function', 'function-variable', 'method'], style: {color: '#b8bb26'}},
    {types: ['number', 'boolean', 'constant', 'symbol'], style: {color: '#d3869b'}},
    {types: ['operator', 'entity', 'url'], style: {color: '#fe8019'}},
    {types: ['class-name', 'maybe-class-name'], style: {color: '#fabd2f'}},
    {types: ['builtin', 'namespace'], style: {color: '#8ec07c'}},
    {types: ['variable', 'attr-name', 'property'], style: {color: '#83a598'}},
    {types: ['deleted'], style: {color: '#fb4934'}},
    {types: ['inserted'], style: {color: '#b8bb26'}},
    {types: ['changed'], style: {color: '#fabd2f'}},
  ],
};

const config: Config = {
  title: 'pan-scm-sdk',
  tagline: 'Python SDK for Palo Alto Networks Strata Cloud Manager',
  favicon: 'img/logo.svg',

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
    // The Gruvbox design system is dark, hard-contrast only.
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: true,
      respectPrefersColorScheme: false,
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
      theme: gruvboxDark,
      darkTheme: gruvboxDark,
      additionalLanguages: ['python', 'bash', 'json', 'yaml', 'toml', 'diff'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
