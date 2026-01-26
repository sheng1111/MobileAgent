# outputs/

AI Agent output directory. Screenshots, downloads, summaries go here.

## Structure

```
outputs/
├── README.md
├── 2026-01-21/
│   ├── search_ig_143022.md
│   ├── search_ig_143022_step1.png
│   └── download_pdf_150033.pdf
└── 2026-01-22/
    └── ...
```

## Filename Format

```
{task_name}_{HHMMSS}.md           # Summary
{task_name}_{HHMMSS}_step1.png    # Screenshot
{task_name}_{HHMMSS}.pdf          # Download
```

## Summary Example

```markdown
# search_ig

**Time:** 2026-01-21 14:30:22

---

搜尋「AI 自動化」，找到 5 篇相關文章：

1. 文章標題一 - 摘要...
2. 文章標題二 - 摘要...
```

## When to Output

Only when user explicitly requests: "save", "download", "record", "summarize"

## Language

Summary content should match **user's language** (e.g., 繁體中文 if user speaks Chinese).
