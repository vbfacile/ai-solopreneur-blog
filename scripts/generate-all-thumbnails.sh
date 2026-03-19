#!/bin/bash
# ============================================================
# Auto-generate thumbnails for all articles missing featured images
# Supports BOTH page bundles and flat posts
# ============================================================

BLOG_DIR="$HOME/blog"
SCRIPT="$BLOG_DIR/scripts/generate-thumbnail.py"
POSTS_DIR="$BLOG_DIR/content/posts"

COUNT=0
SKIPPED=0

# ── Page bundles: content/posts/my-slug/index.md ─────────────
for post in "$POSTS_DIR"/*/index.md; do
  [ -f "$post" ] || continue
  DIR=$(dirname "$post")
  SLUG=$(basename "$DIR")

  # Skip if featured image already exists
  if ls "$DIR"/featured.* 1>/dev/null 2>&1; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Extract category if present
  CATEGORY=$(grep '^categories:' "$post" | head -1 | sed 's/^categories: *\["\{0,1\}//;s/"\{0,1\}\].*$//')

  OUTPUT="$DIR/featured.jpg"

  if [ -n "$CATEGORY" ]; then
    python3 "$SCRIPT" --slug "$SLUG" --category "$CATEGORY" --output "$OUTPUT"
  else
    python3 "$SCRIPT" --slug "$SLUG" --output "$OUTPUT"
  fi

  if [ -s "$OUTPUT" ] && [ $(stat -c%s "$OUTPUT" 2>/dev/null || echo 0) -gt 5000 ]; then
    # Remove old image: front matter if present (page bundles don't need it)
    sed -i '/^image:/d' "$post"
    COUNT=$((COUNT + 1))
    echo "  ✅ $SLUG (page bundle)"
  else
    echo "  ⚠️ Failed: $SLUG"
    rm -f "$OUTPUT"
  fi
done

# ── Flat posts: content/posts/my-slug.md ─────────────────────
for post in "$POSTS_DIR"/*.md; do
  [ -f "$post" ] || continue
  FILENAME=$(basename "$post" .md)
  [ "$FILENAME" = "_index" ] && continue

  SLUG=$(echo "$FILENAME" | sed 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}-//')

  # Skip if already has image in front matter
  if grep -q '^image:' "$post" 2>/dev/null; then
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  CATEGORY=$(grep '^categories:' "$post" | head -1 | sed 's/^categories: *\["\{0,1\}//;s/"\{0,1\}\].*$//')

  mkdir -p "$BLOG_DIR/assets/img/posts"
  OUTPUT="$BLOG_DIR/assets/img/posts/${SLUG}.jpg"

  if [ -n "$CATEGORY" ]; then
    python3 "$SCRIPT" --slug "$SLUG" --category "$CATEGORY" --output "$OUTPUT"
  else
    python3 "$SCRIPT" --slug "$SLUG" --output "$OUTPUT"
  fi

  if [ -s "$OUTPUT" ] && [ $(stat -c%s "$OUTPUT" 2>/dev/null || echo 0) -gt 5000 ]; then
    sed -i "/^title:/a image: \"img/posts/${SLUG}.jpg\"" "$post"
    COUNT=$((COUNT + 1))
    echo "  ✅ $SLUG (flat post)"
  else
    echo "  ⚠️ Failed: $SLUG"
    rm -f "$OUTPUT"
  fi
done

echo ""
echo "Generated: $COUNT thumbnails"
echo "Skipped: $SKIPPED (already had images)"
