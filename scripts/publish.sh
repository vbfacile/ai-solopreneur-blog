#!/bin/bash
# ============================================================
# SmartWorkStack — Full Publish Pipeline
# Injects affiliates → Builds → Pushes → Pings search engines
# Usage: ~/blog/publish.sh
# ============================================================
set -e

BLOG_DIR="$HOME/blog"
cd "$BLOG_DIR"

echo "🚀 Publishing SmartWorkStack..."
echo ""

# ── Step 1: Inject affiliate links ───────────────────────────
if [ -f "$BLOG_DIR/inject-affiliates.sh" ]; then
  echo "💰 Step 1: Injecting affiliate links..."
  bash "$BLOG_DIR/inject-affiliates.sh"
  echo "✅ Affiliates injected"
else
  echo "⏭  Step 1: No inject-affiliates.sh — skipping"
fi

# ── Step 2: Build site ───────────────────────────────────────
echo ""
echo "🏗️  Step 2: Building Hugo site..."
hugo --gc --minify 2>&1
echo "✅ Build complete"

# ── Step 3: Git commit & push ────────────────────────────────
echo ""
echo "📤 Step 3: Pushing to GitHub..."

# Get list of new/changed posts before committing
NEW_POSTS=$(git diff --name-only HEAD 2>/dev/null | grep "content/posts" || true)
UNTRACKED=$(git ls-files --others --exclude-standard | grep "content/posts" || true)
ALL_CHANGED="$NEW_POSTS
$UNTRACKED"

git add -A

# Build commit message from changed files
POST_COUNT=$(echo "$ALL_CHANGED" | grep -c "content/posts" 2>/dev/null || echo "0")
if [ "$POST_COUNT" -gt 0 ]; then
  COMMIT_MSG="Publish: ${POST_COUNT} article(s) updated"
else
  COMMIT_MSG="Site update $(date +%Y-%m-%d)"
fi

git commit -m "$COMMIT_MSG" 2>/dev/null || { echo "⏭  Nothing to commit"; }
git push origin main 2>/dev/null && echo "✅ Pushed to GitHub" || echo "⚠️  Push failed — check SSH key"

# ── Step 4: Ping Google sitemap ──────────────────────────────
echo ""
echo "📡 Step 4: Pinging search engines..."

curl -s "https://www.google.com/ping?sitemap=https://smartworkstack.com/sitemap.xml" > /dev/null 2>&1
echo "  ✅ Google pinged"

curl -s "https://www.bing.com/ping?sitemap=https://smartworkstack.com/sitemap.xml" > /dev/null 2>&1
echo "  ✅ Bing pinged"

# ── Step 5: IndexNow ping for new URLs ───────────────────────
INDEXNOW_KEY=$(ls "$BLOG_DIR/static/"*.txt 2>/dev/null | head -1 | xargs -r basename | sed 's/.txt//')

if [ -n "$INDEXNOW_KEY" ]; then
  # Build URLs from changed post files
  for file in $ALL_CHANGED; do
    case "$file" in
      content/posts/*/index.md)
        SLUG=$(echo "$file" | sed 's|content/posts/\(.*\)/index.md|\1|')
        URL="https://smartworkstack.com/posts/${SLUG}/"
        ;;
      content/posts/*.md)
        SLUG=$(basename "$file" .md)
        URL="https://smartworkstack.com/posts/${SLUG}/"
        ;;
      *) continue ;;
    esac

    curl -s "https://api.indexnow.org/indexnow?url=${URL}&key=${INDEXNOW_KEY}&keyLocation=https://smartworkstack.com/${INDEXNOW_KEY}.txt" > /dev/null 2>&1
    echo "  ✅ IndexNow: $URL"
    sleep 1
  done
else
  echo "  ⚠️  No IndexNow key found — generate one:"
  echo "     openssl rand -hex 16 | tee ~/blog/static/\$(cat).txt"
fi

# ── Step 6: Ping sitemap URL directly ────────────────────────
curl -s "https://smartworkstack.com/sitemap.xml" > /dev/null 2>&1

# ── Done ─────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "✅ Published! Live in 2-3 minutes."
echo "   Site: https://smartworkstack.com"
echo "   Commit: $COMMIT_MSG"
echo "============================================================"
