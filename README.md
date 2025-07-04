# The Monospace Blog

A Python-powered Markdown blog based on [my Python replication](https://github.com/chriscarrollsmith/monospace-web-python) of [The Monospace Web](https://github.com/owickstrom/the-monospace-web) by Oskar Wickström.

![Monospace Blog Screenshot](screenshot.png)

## Using the Monospace Blog

A Github workflow is configured to automatically build the site in the `docs` folder and commit and push the built files to the remote whenever you push source file changes to `main`.

To get started, you will need to:

1. Fork the repository

2. Edit `templates/base.html` and `templates/index.html` to customize the landing page

3. Enable GitHub Pages for your repository and configure Github Pages to serve the site from the `docs` folder on `main`. You can find these settings in your fork's `Settings > Pages > Build and deployment` section.

4. Add or edit markdown files in the `posts/` folder to publish blog posts to Github Pages

## Compatibility with Reprose

This blog generator is designed to work seamlessly with [Reprose](https://repose.pp.ua), an online markdown editor that integrates with GitHub. You can:

1. Write and edit posts directly in Reprose's online editor
2. Push changes to your repository with a button-click
3. Watch as GitHub Actions automatically builds and deploys your blog
4. The frontmatter format is fully compatible with Reprose's standard fields (title, description, date) and supports any additional custom fields you want to add.

## SEO Frontmatter Fields

This blog generator includes comprehensive SEO support through YAML frontmatter fields. You provide the title, description, date, and tags in a frontmatter section at the top of your Markdown post, and the build script will automatically generate HTML page metadata, social graph tags, and a sitemap.

### Example Frontmatter

```yaml
---
title: My Awesome Blog Post
description: A detailed guide to writing great content with SEO optimization
date: 2024-01-15
author: Your Name
tags: [blogging, seo, markdown]
image: https://example.com/featured-image.jpg
caption: A caption for the featured image
---
```

### Supported fields:

#### Required Fields

- **`title`** - Post title (used for page title, Open Graph title, Twitter title)
- **`description`** - Brief post description (used for meta description, Open Graph description, Twitter description)
- **`date`** - Publication date in YYYY-MM-DD format (used for article:published_time meta tag)

#### Optional SEO Fields

- **`author`** - Author name (used for meta author and article:author tags)
- **`image`** - Featured image URL (used for Open Graph image and Twitter Card image)
- **`tags`** - Array of tags (e.g., `[tag1, tag2, tag3]`) (used for article:tag meta tags)
- **`draft`** - Set to `true` to exclude post from build

#### Auto-generated Fields

The build script automatically generates:

- **`slug`** - URL-friendly version of the filename
- **`url`** - Final HTML filename (`{slug}.html`)

## A note on Markdown style

This project's markdown renderer uses the [CommonMark specification](https://commonmark.org/). CommonMark offers a helpful 60-second [tutorial](https://commonmark.org/help/) that you may find helpful if you're new to Markdown.

## Configuration

The blog generator supports configuration through environment variables, which can be set in a `.env` file or passed as command-line arguments.

### Environment Variables

Copy `.env.example` to `.env` to customize your configuration:

```bash
cp .env.example .env
```

Available variables:

- **`SHOW_DEBUG`** - Controls whether debug grid toggle interface is displayed on pages
  - Default: `true` (debug toggle interface shown)
  - Note: This controls the checkbox visibility; the actual debug grid is toggled by users clicking the checkbox

### Command Line Options

You can also control debug grid toggle using command-line arguments:

```bash
# Hide debug toggle
uv run scripts/build.py --no-debug

# Show debug toggle
uv run scripts/build.py --debug
```

Command-line arguments take precedence over environment variables.

## Development

1. Clone this repository:

   ```bash
   git clone https://github.com/chriscarrollsmith/monospace-blog.git
   ```

2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/):

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install Python 3.13+ and other dependencies with uv:
   ```bash
   uv sync
   ```

4. Edit templates in `templates/`

5. Edit blog posts in `posts/`

6. Build the site:
   ```bash
   uv run scripts/build.py
   ```

7. Open `docs/index.html` in a web browser to preview the site.

## License

MIT License - see [LICENSE](LICENSE) for details.
