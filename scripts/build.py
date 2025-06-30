"""
Markdown Blog Generator
Converts markdown files with YAML frontmatter to HTML using Jinja2 templates.
"""

import os
import shutil
import frontmatter
import mistletoe
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import re
import json


class BlogGenerator:
    def __init__(self, posts_dir='posts', templates_dir='templates', output_dir='docs', static_dir='static'):
        self.posts_dir = posts_dir
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.static_dir = static_dir
        
        # Setup Jinja2 environment
        self.env = Environment(loader=FileSystemLoader(templates_dir))
    
    def clean_output_dir(self):
        """Clean the output directory."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def copy_static_files(self):
        """Copy static files to output directory."""
        if os.path.exists(self.static_dir):
            static_output = os.path.join(self.output_dir, 'static')
            if os.path.exists(static_output):
                shutil.rmtree(static_output)
            shutil.copytree(self.static_dir, static_output)
        
        # Also copy any CSS/JS files from docs/static if they exist (from monospace styling)
        docs_static = os.path.join(self.output_dir, 'static')
        if os.path.exists(docs_static):
            # Copy additional files that might be in docs/static
            for filename in ['reset.css', 'index.js']:
                src_path = os.path.join(docs_static, filename)
                if os.path.exists(src_path):
                    print(f"Found existing {filename} in output directory")
    
    def parse_post(self, filepath):
        """Parse a markdown post with frontmatter."""
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        
        # Convert markdown content to HTML (tables supported out of the box)
        html_content = mistletoe.markdown(post.content)
        
        # Extract metadata
        metadata = post.metadata.copy()
        
        # Ensure required fields
        if 'title' not in metadata:
            metadata['title'] = os.path.splitext(os.path.basename(filepath))[0]
        if 'date' not in metadata:
            metadata['date'] = datetime.now().strftime('%Y-%m-%d')
        if 'description' not in metadata:
            # Try to extract first paragraph as description
            first_para = re.search(r'<p>(.*?)</p>', html_content)
            if first_para:
                metadata['description'] = re.sub(r'<[^>]+>', '', first_para.group(1))[:150] + '...'
            else:
                metadata['description'] = metadata['title']
        
        # Parse date
        if isinstance(metadata['date'], str):
            try:
                metadata['date'] = datetime.strptime(metadata['date'], '%Y-%m-%d')
            except ValueError:
                metadata['date'] = datetime.now()
        
        # Generate slug from filename
        slug = os.path.splitext(os.path.basename(filepath))[0]
        metadata['slug'] = slug
        metadata['url'] = f"{slug}.html"
        
        return {
            'content': html_content,
            'metadata': metadata,
            'filepath': filepath
        }
    
    def get_all_posts(self):
        """Get all posts, sorted by date (newest first)."""
        posts = []
        
        if not os.path.exists(self.posts_dir):
            print(f"Posts directory '{self.posts_dir}' not found. Creating it...")
            os.makedirs(self.posts_dir, exist_ok=True)
            return posts
        
        for filename in os.listdir(self.posts_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(self.posts_dir, filename)
                try:
                    post = self.parse_post(filepath)
                    
                    # Skip drafts
                    if post['metadata'].get('draft', False):
                        continue
                    
                    posts.append(post)
                except Exception as e:
                    print(f"Error parsing {filename}: {e}")
        
        # Sort by date (newest first)
        posts.sort(key=lambda x: x['metadata']['date'], reverse=True)
        return posts
    
    def generate_post_html(self, post):
        """Generate HTML for a single post."""
        template = self.env.get_template('post.html')
        
        html = template.render(
            title=post['metadata']['title'],
            content=post['content'],
            metadata=post['metadata'],
            post=post
        )
        
        output_path = os.path.join(self.output_dir, post['metadata']['url'])
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Generated: {post['metadata']['url']}")
    
    def generate_posts_json(self, posts):
        """Generate a JSON file with all posts data for client-side pagination and filtering."""
        posts_data = []
        
        for post in posts:
            # Convert datetime to string for JSON serialization
            post_data = {
                'title': post['metadata']['title'],
                'description': post['metadata']['description'],
                'date': post['metadata']['date'].strftime('%Y-%m-%d'),
                'author': post['metadata'].get('author', ''),
                'tags': post['metadata'].get('tags', []),
                'url': post['metadata']['url'],
                'image': post['metadata'].get('image', ''),
                'caption': post['metadata'].get('caption', '')
            }
            posts_data.append(post_data)
        
        output_path = os.path.join(self.output_dir, 'static', 'posts.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(posts_data, f, indent=2)
        
        print("Generated: static/posts.json")
    
    def generate_index_html(self, posts):
        """Generate the homepage with post previews and pagination."""
        template = self.env.get_template('index.html')
        
        # Only show first 20 posts for initial render
        posts_per_page = 20
        initial_posts = posts[:posts_per_page]
        
        # Get all unique tags for filtering
        all_tags = set()
        for post in posts:
            if post['metadata'].get('tags'):
                all_tags.update(post['metadata']['tags'])
        
        # Calculate pagination info
        total_posts = len(posts)
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page
        
        html = template.render(
            posts=initial_posts,
            total_posts=total_posts,
            total_pages=total_pages,
            posts_per_page=posts_per_page,
            current_page=1,
            all_tags=sorted(list(all_tags)),
            site_title="My Blog",
            site_description="A blog generated from markdown files"
        )
        
        output_path = os.path.join(self.output_dir, 'index.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print("Generated: index.html")
    
    def generate_sitemap(self, posts):
        """Generate a sitemap.xml file."""
        base_url = "https://yourusername.github.io/your-repo-name"  # Update this
        
        sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        # Add homepage
        sitemap_content.append('  <url>')
        sitemap_content.append(f'    <loc>{base_url}/</loc>')
        sitemap_content.append('    <changefreq>daily</changefreq>')
        sitemap_content.append('    <priority>1.0</priority>')
        sitemap_content.append('  </url>')
        
        # Add posts
        for post in posts:
            sitemap_content.append('  <url>')
            sitemap_content.append(f'    <loc>{base_url}/{post["metadata"]["url"]}</loc>')
            sitemap_content.append(f'    <lastmod>{post["metadata"]["date"].strftime("%Y-%m-%d")}</lastmod>')
            sitemap_content.append('    <changefreq>monthly</changefreq>')
            sitemap_content.append('    <priority>0.8</priority>')
            sitemap_content.append('  </url>')
        
        sitemap_content.append('</urlset>')
        
        output_path = os.path.join(self.output_dir, 'sitemap.xml')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(sitemap_content))
        
        print("Generated: sitemap.xml")
    
    def build(self):
        """Build the entire blog."""
        print("Starting blog build...")
        
        # Clean and setup output directory
        self.clean_output_dir()
        
        # Copy static files
        self.copy_static_files()
        
        # Get all posts
        posts = self.get_all_posts()
        print(f"Found {len(posts)} posts")
        
        # Generate individual post pages
        for post in posts:
            self.generate_post_html(post)
        
        # Generate posts JSON for client-side functionality
        self.generate_posts_json(posts)
        
        # Generate homepage
        self.generate_index_html(posts)
        
        # Generate sitemap
        self.generate_sitemap(posts)
        
        print(f"Blog build complete! Generated {len(posts)} posts + homepage")

if __name__ == '__main__':
    generator = BlogGenerator()
    generator.build() 
