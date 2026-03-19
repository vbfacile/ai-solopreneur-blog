#!/bin/bash
echo "🔗 Injecting affiliate links into articles..."

cd ~/blog

# Read affiliate links from JSON
# Replace AFFILIATE_LINK_xxx placeholders with real URLs

declare -A LINKS
LINKS=(
    # Real affiliate links (update as you sign up)
    ["AFFILIATE_LINK_zapier"]="https://zapier.com"
    ["AFFILIATE_LINK_make"]="https://make.com"
    ["AFFILIATE_LINK_notion"]="https://notion.so"
    ["AFFILIATE_LINK_hubspot"]="https://hubspot.com"
    ["AFFILIATE_LINK_canva"]="https://canva.com"
    ["AFFILIATE_LINK_monday"]="https://monday.com"
    ["AFFILIATE_LINK_clickup"]="https://clickup.com"
    ["AFFILIATE_LINK_todoist"]="https://todoist.com"
    ["AFFILIATE_LINK_grammarly"]="https://grammarly.com"
    ["AFFILIATE_LINK_freshbooks"]="https://freshbooks.com"
    ["AFFILIATE_LINK_calendly"]="https://calendly.com"
    ["AFFILIATE_LINK_shopify"]="https://shopify.com"
    ["AFFILIATE_LINK_digitalocean"]="https://digitalocean.com"
    ["AFFILIATE_LINK_typeform"]="https://typeform.com"
    ["AFFILIATE_LINK_asana"]="https://asana.com"
    ["AFFILIATE_LINK_loom"]="https://loom.com"
    ["AFFILIATE_LINK_stripe"]="https://stripe.com"
    ["AFFILIATE_LINK_appsumo"]="https://appsumo.com"
)

REPLACED=0
for placeholder in "${!LINKS[@]}"; do
    url="${LINKS[$placeholder]}"
    # Skip if still has YOUR_CODE
    if [[ "$url" == *"YOUR_CODE"* ]]; then
        continue
    fi
    count=$(grep -rl "$placeholder" content/posts/ 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        sed -i "s|$placeholder|$url|g" content/posts/*.md
        echo "  ✅ $placeholder → $url ($count files)"
        REPLACED=$((REPLACED + count))
    fi
done

# Report remaining placeholders
REMAINING=$(grep -rn 'AFFILIATE_LINK_' content/posts/ 2>/dev/null)
if [ -z "$REMAINING" ]; then
    echo ""
    echo "✅ All placeholders replaced! ($REPLACED substitutions)"
else
    echo ""
    echo "⚠️  Still need affiliate codes for:"
    echo "$REMAINING" | grep -oE 'AFFILIATE_LINK_[a-z_]+' | sort -u
fi

# Report tools with no affiliate program
NO_AFFILIATE=$(grep -rn 'NO_AFFILIATE:' content/posts/ 2>/dev/null)
if [ -n "$NO_AFFILIATE" ]; then
    echo ""
    echo "📋 Tools mentioned with no affiliate program:"
    echo "$NO_AFFILIATE" | grep -oE 'NO_AFFILIATE: [a-z_]+' | sort -u
fi
