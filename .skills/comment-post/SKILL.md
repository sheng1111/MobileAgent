---
name: comment-post
description: Post a pre-composed comment to a post/article and verify publication. Does NOT generate comment content (use comment-draft skill first). Use after user approves a draft comment.
license: MIT
metadata:
  author: MobileAgent
  version: "1.0"
compatibility: Requires mobile-mcp MCP server, connected Android device with target social app installed
---

# Comment Posting Workflow

## Purpose

Execute the actual posting of a pre-composed comment to a specific post or article, then verify the comment appears successfully. Handle platform-specific posting flows, input methods, and verification.

## Scope

### What This Skill Does

- Navigate to comment input field on target post
- Enter the provided comment text (Unicode supported)
- Submit the comment
- Verify comment appears in comment section
- Handle platform-specific posting UI patterns
- Report success with evidence (screenshot)
- Handle posting failures and retry

### What This Skill Does NOT Do

- Generate comment content (use `comment-composition-and-tone-control`)
- Select which post to comment on (input must specify)
- Read or analyze existing comments
- Decide IF to comment (assumes user has decided)

## Inputs

### Required

| Parameter | Type | Description |
|-----------|------|-------------|
| `platform` | string | Platform name |
| `post_identifier` | object | Which post to comment on |
| `comment_text` | string | The comment to post |

### Post Identifier Options

```yaml
# Option 1: Currently viewing (already navigated to post)
post_identifier:
  type: current_screen

# Option 2: Search and navigate
post_identifier:
  type: search_result
  keyword: "AI agents"
  position: 1

# Option 3: By content match
post_identifier:
  type: content_match
  title_contains: "My AI experience"
  author: "@user"
```

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `verify_timeout` | int | 10 | Seconds to wait for comment to appear |
| `retry_on_failure` | boolean | true | Retry posting if first attempt fails |
| `max_retries` | int | 2 | Maximum retry attempts |
| `take_evidence` | boolean | true | Screenshot after posting |

## Outputs

### Posting Result

```yaml
posting_result:
  status: "SUCCESS" | "FAILED" | "PARTIAL" | "NEEDS_VERIFICATION"

  post_info:
    platform: string
    post_title: string
    post_author: string

  comment:
    text: string  # What was posted
    char_count: int
    timestamp: string

  verification:
    verified: boolean
    method: string  # How verification was done
    # "element_found" | "screenshot_match" | "not_verified"
    screenshot: string  # Path to evidence

  attempts:
    count: int
    details:
      - attempt: 1
        action: string
        result: string

  error:  # If failed
    type: string
    message: string
    recoverable: boolean
```

## Primary Workflow

### Phase 1: Navigate to Post (if needed)

```
If post_identifier.type != "current_screen":
  1. Navigate to the specified post
     (Use appropriate navigation based on identifier type)

  2. Verify correct post
     - Check title/author matches expected

  3. Wait for post to fully load
     → smart_wait(timeout=3)
```

### Phase 2: Locate Comment Input

```
Platform-specific patterns:

Threads:
  - Look for comment icon or "Reply" text
  - Click to open comment input
  → find_and_click(text="Reply") OR find_and_click(resource_id="comment_button")

Instagram:
  - Tap comment icon
  - Input field appears at bottom
  → find_and_click(description="Comment")

WeChat:
  - Scroll to comment section
  - Look for input field or "写留言"
  → find_and_click(text="写留言")

X/Twitter:
  - Look for "Reply" or comment icon
  → find_and_click(text="Reply")

YouTube:
  - Look for "Add a comment" field
  → find_and_click(text="Add a comment")
```

### Phase 3: Enter Comment Text

```
1. Ensure input field is focused
   - May need to tap input field first
   → find_and_click(text="Add a comment") OR tap on visible input

2. Wait for keyboard to appear
   → smart_wait(timeout=2)

3. Enter comment text (Unicode supported via DeviceKit)
   → type_and_submit(text=comment_text, submit=false)

4. Verify text was entered correctly
   - Get current input field content
   - Compare with expected text
```

### Phase 4: Submit Comment

```
1. Locate submit button
   Platform patterns:
   - Threads/Instagram: "Post" or arrow icon
   - WeChat: "发送" or checkmark
   - X/Twitter: "Reply" or "Post"
   - YouTube: Paper airplane or "Comment"

2. Submit the comment
   → find_and_click(text="Post") OR find_and_click(text="发送")

3. Wait for submission
   → smart_wait(timeout=5)

4. Check for errors:
   - "Comment failed" messages
   - Network error dialogs
   - Character limit warnings
   - Content policy violations
```

### Phase 5: Verify Comment Posted

```
Verification methods (try in order):

Method 1: Element Search
  - Look for comment text in comment section
  → scroll_and_find(text=comment_text[:30])  # First 30 chars
  - If found: VERIFIED

Method 2: Author Match
  - Look for "You" or user's name near comment
  - Check timestamp shows "just now" or similar

Method 3: Visual Verification
  - Take screenshot
  - Confirm comment visible
  → mobile_save_screenshot(saveTo="outputs/.../evidence.png")

Method 4: Post-Submit UI
  - Some platforms show "Comment posted" toast
  - Input field clears after success
```

### Phase 6: Handle Failures

```
If submission failed:
  1. Identify error type:
     - Network error: retry after wait
     - Content violation: cannot retry, report to user
     - Rate limit: wait longer, then retry
     - Login expired: cannot retry, report to user

  2. If retry_on_failure and retries < max_retries:
     - Wait 2-5 seconds
     - Attempt again from Phase 3

  3. If exhausted retries:
     - Report failure with details
     - Capture screenshot of error state
```

### Phase 7: Report Result

```
Compile posting_result with:
  - Final status
  - Evidence screenshot (if take_evidence=true)
  - Attempt history
  - Any error details
```

## Platform-Specific Patterns

### Threads

```yaml
comment_flow:
  access: Tap comment icon below post
  input_location: Bottom sheet slides up
  submit_button: "Post" on right side
  verification: Comment appears in thread
  special_notes:
    - May need to scroll up to see posted comment
    - Input clears on success
```

### Instagram

```yaml
comment_flow:
  access: Tap speech bubble icon
  input_location: Bottom of screen
  submit_button: "Post" or blue arrow
  verification: Comment appears in comment list
  special_notes:
    - Emoji keyboard may open first
    - Comments may be held for review
```

### WeChat Articles

```yaml
comment_flow:
  access: Scroll to bottom, tap "写留言"
  input_location: Full-screen input view
  submit_button: "发送" top-right
  verification: Comment appears in "精选留言" if approved
  special_notes:
    - Comments often require author approval
    - May not appear immediately
    - Some articles disable comments
```

### X/Twitter

```yaml
comment_flow:
  access: Tap comment/reply icon
  input_location: Compose screen opens
  submit_button: "Reply" or "Post"
  verification: Reply appears in thread
  special_notes:
    - Character limit applies (280)
    - Can include media
```

### YouTube

```yaml
comment_flow:
  access: Scroll to comments, tap "Add a comment"
  input_location: Bottom of screen or modal
  submit_button: Paper airplane icon
  verification: Comment appears in comment section
  special_notes:
    - Comments may be held for review
    - Requires signed-in account
```

## Heuristics

### Comment Input Detection

| Platform | Input Field Identifiers |
|----------|------------------------|
| Threads | "Add a comment", "Write a comment" |
| Instagram | "Add a comment...", placeholder text |
| WeChat | "写留言", "发表留言" |
| Weibo | "说点什么", "写评论" |
| X/Twitter | "Tweet your reply", "Add a comment" |
| YouTube | "Add a comment...", "Add a public comment" |

### Submit Button Detection

| Platform | Submit Button Text/ID |
|----------|----------------------|
| Threads | "Post", send arrow |
| Instagram | "Post", blue arrow |
| WeChat | "发送", checkmark |
| Weibo | "发送", "发布" |
| X/Twitter | "Reply", "Post" |
| YouTube | Send icon (paper airplane) |

### Success Indicators

| Indicator | Confidence |
|-----------|------------|
| Comment visible with your username | High |
| "Comment posted" toast | High |
| Input field cleared | Medium |
| Timestamp shows "now" / "刚刚" | Medium |
| Screen returned to post view | Low (might be success or failure) |

### Failure Indicators

| Indicator | Meaning |
|-----------|---------|
| "Comment failed" / "发送失败" | Submission error |
| "Try again" button | Temporary failure |
| "Content violates..." | Policy rejection |
| "Log in to comment" | Session expired |
| "Comments are turned off" | Post disabled comments |
| "Too many comments" | Rate limited |
| Input field still has text | Submission didn't complete |

## Failure Modes & Recovery

### 1. Input Field Not Found

**Symptom:** Can't locate comment input area.

**Recovery:**
- Try scrolling to reveal comment section
- Check if comments are disabled on this post
- Try alternative input selectors
- Report: "Comment input not found, comments may be disabled"

### 2. Text Input Fails

**Symptom:** Comment text doesn't appear in field.

**Recovery:**
- Ensure input field is focused (tap again)
- Check if keyboard is active
- Try clearing and re-entering
- Verify DeviceKit APK is installed for Unicode

### 3. Submit Button Unresponsive

**Symptom:** Tapping submit does nothing.

**Recovery:**
- Ensure comment field has text
- Check for validation errors (character limit)
- Try keyboard "Enter" key as alternative
- Wait and retry

### 4. Content Policy Rejection

**Symptom:** "Your comment couldn't be posted" or similar.

**Recovery:**
- Cannot retry with same text
- Report specific rejection reason if shown
- Suggest user modify comment content
- Do NOT auto-modify the comment

### 5. Rate Limiting

**Symptom:** "Wait before commenting again" or similar.

**Recovery:**
- Wait 30-60 seconds
- Retry if within retry budget
- Report if still blocked

### 6. Comment Requires Approval

**Symptom:** "Comment submitted for review" or doesn't appear immediately.

**Recovery:**
- Status: "PARTIAL" (posted but not verified)
- Note that approval is pending
- Screenshot confirmation message

### 7. Network Error During Submit

**Symptom:** Timeout or connection error.

**Recovery:**
- Check if comment was partially saved (draft)
- Retry submission
- Verify network connectivity

## Tooling (MCP)

### Primary Tools

| Tool | Use Case |
|------|----------|
| `find_and_click` | Navigate to post, tap comment input, submit |
| `type_and_submit` | Enter comment text |
| `smart_wait` | Wait for UI state changes |
| `navigate_back` | Return after posting |

### Secondary Tools

| Tool | Use Case |
|------|----------|
| `mobile_list_elements_on_screen` | Find input field, submit button |
| `mobile_type_keys` | Direct text input if type_and_submit fails |
| `scroll_and_find` | Locate comment section, verify posted |
| `mobile_save_screenshot` | Capture evidence |
| `dismiss_popup` | Handle unexpected dialogs |

### Unicode Input Requirements

```
For Chinese/Japanese/Korean text:
- DeviceKit APK must be installed
- Use: mobile_type_keys with DeviceKit active

If DeviceKit not available:
- Report limitation
- Suggest user install DeviceKit
- Cannot post Unicode comments via MCP
```

## Examples

### Example 1: Successful Threads Comment

**Input:**
```yaml
platform: threads
post_identifier:
  type: current_screen
comment_text: "Great analysis! I've had similar experiences with AI agents for coding tasks."
```

**Execution:**
```
[1] Verified on correct post ("Building agents with Claude")
[2] Found comment input icon
[3] Tapped to open comment sheet
[4] Input field focused, keyboard appeared
[5] Entered comment text (67 characters)
[6] Found "Post" button
[7] Tapped Post
[8] Waited 3 seconds
[9] Scrolled up in comments
[10] Found comment with matching text - VERIFIED
[11] Captured screenshot: evidence_001.png
```

**Output:**
```yaml
posting_result:
  status: "SUCCESS"

  post_info:
    platform: threads
    post_title: "Building agents with Claude"
    post_author: "@techdev"

  comment:
    text: "Great analysis! I've had similar experiences with AI agents for coding tasks."
    char_count: 67
    timestamp: "2024-01-15T10:45:23Z"

  verification:
    verified: true
    method: "element_found"
    screenshot: "outputs/2024-01-15/evidence_001.png"

  attempts:
    count: 1
    details:
      - attempt: 1
        action: "submit"
        result: "success"
```

---

### Example 2: WeChat Comment (Pending Approval)

**Input:**
```yaml
platform: wechat
post_identifier:
  type: content_match
  title_contains: "AI大模型"
  author: "机器之心"
comment_text: "分析很深入，学习了！期待后续更新。"
```

**Execution:**
```
[1] Navigated to article
[2] Scrolled to comment section
[3] Tapped "写留言"
[4] Input screen opened
[5] Entered Chinese text via DeviceKit
[6] Tapped "发送"
[7] Message: "留言已提交，待作者审核"
[8] Comment not visible in section (awaiting approval)
[9] Captured confirmation screenshot
```

**Output:**
```yaml
posting_result:
  status: "PARTIAL"

  comment:
    text: "分析很深入，学习了！期待后续更新。"
    char_count: 18
    timestamp: "2024-01-15T10:50:00Z"

  verification:
    verified: false
    method: "not_verified"
    note: "Comment submitted but pending author approval (WeChat standard behavior)"
    screenshot: "outputs/2024-01-15/evidence_002.png"

  attempts:
    count: 1
```

---

### Example 3: Failed Due to Policy Violation

**Input:**
```yaml
platform: instagram
comment_text: "Check out my profile for free giveaways!!!"
```

**Execution:**
```
[1] Verified on correct post
[2] Opened comment input
[3] Entered text
[4] Tapped Post
[5] Error appeared: "This comment couldn't be posted"
[6] Error detail: "This may be due to a link or content that violates our guidelines"
[7] Captured error screenshot
```

**Output:**
```yaml
posting_result:
  status: "FAILED"

  comment:
    text: "Check out my profile for free giveaways!!!"
    char_count: 43

  verification:
    verified: false
    method: "not_verified"

  error:
    type: "CONTENT_POLICY"
    message: "Comment blocked by platform - likely flagged as promotional/spam content"
    recoverable: false

  attempts:
    count: 1
```

---

### Example 4: Success After Retry

**Input:**
```yaml
platform: threads
comment_text: "Interesting perspective"
retry_on_failure: true
max_retries: 2
```

**Execution:**
```
[Attempt 1]
[1] Entered text
[2] Tapped Post
[3] Network error toast appeared
[4] Waiting 5 seconds before retry...

[Attempt 2]
[5] Re-entered text
[6] Tapped Post
[7] Comment submitted successfully
[8] Verified in comment list
```

**Output:**
```yaml
posting_result:
  status: "SUCCESS"

  verification:
    verified: true
    method: "element_found"

  attempts:
    count: 2
    details:
      - attempt: 1
        action: "submit"
        result: "network_error"
      - attempt: 2
        action: "submit"
        result: "success"
```

## Key Reminders

1. **Pre-composed comment only** - Don't generate content, just post it
2. **Verify before claiming success** - Actually find the posted comment
3. **Capture evidence** - Screenshot is proof of action
4. **Handle Unicode properly** - Ensure DeviceKit installed for CJK text
5. **Report approval pending** - WeChat comments often need approval
6. **Don't auto-retry policy failures** - These won't succeed with same text
7. **Platform-specific flows** - Each platform has different posting UI
8. **Clear error reporting** - User needs to know exactly what went wrong
