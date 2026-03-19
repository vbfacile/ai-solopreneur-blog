#!/bin/bash
# ============================================================
# Auto-generate thumbnails for all articles missing images
# Run after seo-article-writer, before site-publisher
# ============================================================

BLOG_DIR="$HOME/blog"
SCRIPT="$BLOG_DIR/scripts/generate-thumbnail.py"
IMG_DIR="$BLOG_DIR/assets/img/posts"
POSTS_DIR="$BLOG_DIR/content/posts"

mkdir -p "$IMG_DIR"

COUNT=0
SKIPPED=0

for post in "$POSTS_DIR"/*.md; do
  [ -f "$post" ] || continue

  # Skip if already has image in front matter
  if grep -q '^image:' "$post" 2>/dev/null; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Extract slug from filename (remove date prefix and .md)
  FILENAME=$(basename "$post" .md)
  # Handle both "2026-03-19-my-slug.md" and "my-slug.md"
  SLUG=$(echo "$FILENAME" | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//')

  # Extract title from front matter
  TITLE=$(grep '^title:' "$post" | head -1 | sed 's/^title: *"*//;s/"*$//')
  [ -z "$TITLE" ] && continue

  # Extract category if present
  CATEGORY=$(grep '^categories:' "$post" | head -1 | sed 's/^categories: *\["\{0,1\}//;s/"\{0,1\}\].*$//')

  # Generate thumbnail
  OUTPUT="$IMG_DIR/${SLUG}.jpg"
  
  if [ -n "$CATEGORY" ]; then
    python3 "$SCRIPT" --title "$TITLE" --slug "$SLUG" --category "$CATEGORY" --output "$OUTPUT"
  else
    python3 "$SCRIPT" --title "$TITLE" --slug "$SLUG" --output "$OUTPUT"
  fi

  # Verify image was created
  if [ -s "$OUTPUT" ] && [ $(stat -c%s "$OUTPUT" 2>/dev/null || echo 0) -gt 5000 ]; then
    # Inject image field into front matter (after title line)
    sed -i "/^title:/a image: \"img/posts/${SLUG}.jpg\"" "$post"
    COUNT=$((COUNT + 1))
    echo "  ✅ $SLUG"
  else
    echo "  ⚠️ Failed: $SLUG"
    rm -f "$OUTPUT"
  fi
done

echo ""
echo "Generated: $COUNT thumbnails"
echo "Skipped: $SKIPPED (already had images)"
