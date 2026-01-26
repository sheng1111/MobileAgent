---
name: social-media
description: Social media and dating app operations including like, comment, share, send message, follow, and swipe matching. Supports LINE, Facebook, Instagram, Threads, WeChat, X, Telegram, YouTube, Gmail, and dating apps (Tantan, Tinder, Bumble, etc). Adapts to different UI languages and version differences.
---

# Social Media Skill

## Mindset

```
You are EXPLORING, not scripting.

UIs change constantly. Observe → Think → Act → Verify.
When blocked, try alternatives. Trust your judgment.
```

## Tool Priority

1. `mobile_list_elements_on_screen` - Get clickable elements with coordinates
2. `mobile_take_screenshot` - Visual verification when elements unclear
3. MCP tools for actions, Python fallback if needed

## Think Like a User

**What would a human do?**

To like → find heart icon → tap
To comment → find bubble → tap → type → send
To search → find magnifying glass → tap → type → submit
To message → find chat/inbox → select contact → type → send
To follow → go to profile → tap follow button

**Icons are universal:**
- Heart/Thumbs = Like
- Bubble = Comment
- Paper plane/Arrow = Share/Send
- Magnifying glass = Search
- Bookmark = Save
- ≡ = Menu
- ⋮ = More options

## Browsing & Exploration

**One screen is never enough.** When browsing feeds, search results, profiles, or any content list:

1. **Scroll naturally** - Swipe up 3-5 times, let content load
2. **Tap into content** - Open posts/articles to see full text, images, comments
3. **Navigate back** - Return to list and continue browsing
4. **Repeat** - Browse multiple items before concluding

**Applies to:**
- Search results (keywords, hashtags, topics)
- User profiles (viewing someone's posts)
- Feeds and timelines
- Comments and replies
- Product reviews
- News articles
- Any scrollable content list

**Browsing workflow:**
```
Open list/feed → Scroll → Open item 1 → Read → Back
→ Scroll → Open item 2 → Read → Back
→ ... (continue exploring)
→ Report findings or complete task
```

**How much to browse:**
- Quick check: 3-5 items
- Research/summary task: 5-10+ items
- Comprehensive analysis: scroll until content repeats

**Don't be robotic:**
- Skip obvious ads or irrelevant content
- Spend more time on interesting items
- Follow your judgment like a real user would

## Adaptive Approach

**Element not where expected?**
→ Scroll to reveal, wait for loading, try screenshot, find alternative path

**Action failed?**
→ Tap center of bounds, check for overlay, try long-press, retry once

**Unknown app?**
→ Map all elements, find universal patterns, proceed with what exists

**3+ failures?**
→ Stop, reassess, try different approach or report to user

## Dating Apps

```
Right swipe / Heart = Like
Left swipe / X = Pass
Tap buttons if swipe unreliable
Handle match popup → continue or message
```

## Obstacles

| Issue | Action |
|-------|--------|
| Login required | Report to user |
| Ads/Popups | Find X/Skip/Close |
| Permissions | Allow if needed |
| CAPTCHA | Report to user |

## References

Load when needed:
- `references/package-names.md`
- `references/ui-common.md`
- `references/ui-{platform}.md` (instagram, threads, facebook, line, wechat, x-twitter, telegram, tiktok, youtube, dating, etc.)
