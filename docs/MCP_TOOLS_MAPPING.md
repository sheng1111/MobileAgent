# MCP Tools ↔ Skills Mapping

This document maps all available MCP tools to their corresponding skills and use cases.

## MCP Servers Overview

| Server | Package | Purpose | Status |
|--------|---------|---------|--------|
| **mobile-macro** | `src.mcp_macro_server` | High-level automation macros | Recommended |
| **mobile-mcp** | `@mobilenext/mobile-mcp` | Low-level device control | Fallback |
| **filesystem** | `@modelcontextprotocol/server-filesystem` | File operations | Utility |
| **fetch** | `mcp-server-fetch` | Web content retrieval | Utility |
| **context7** | `@upstash/context7-mcp` | Library documentation | Reference |

---

## 1. mobile-macro Server (High-Level)

### Tools

| Tool | Description | Parameters | Use Case |
|------|-------------|------------|----------|
| `find_and_click` | Find element and click with verification | `text`, `resource_id`, `description`, `class_name`, `timeout`, `verify`, `retry` | Most click operations |
| `type_and_submit` | Type text and optionally submit | `text`, `input_text`, `input_id`, `clear_first`, `submit` | Form input, search |
| `smart_wait` | Wait for element appear/disappear | `text`, `resource_id`, `gone`, `timeout` | Loading states, transitions |
| `scroll_and_find` | Scroll until element found | `text`, `resource_id`, `direction`, `max_scrolls` | Finding content below fold |
| `navigate_back` | Press back with verification | `expected_text`, `max_attempts` | Navigation, exit screens |
| `dismiss_popup` | Dismiss dialogs automatically | `button_texts`, `timeout` | Handle interruptions |
| `launch_and_wait` | Launch app and wait for ready | `package`, `wait_text`, `timeout` | App startup |
| `get_screen_summary` | Get current screen state | (none) | Observation, debugging |
| `run_patrol` | Automated social media browsing | `keyword`, `platform`, `max_posts`, `max_scrolls`, `max_time_minutes` | Keyword monitoring |

### Skills Using mobile-macro

| Skill | Tools Used | Primary Use |
|-------|------------|-------------|
| **search-triage** | `find_and_click`, `type_and_submit`, `scroll_and_find`, `navigate_back`, `get_screen_summary` | Multi-round search |
| **comment-scan** | `scroll_and_find`, `get_screen_summary`, `navigate_back` | Comment analysis |
| **article-extract** | `scroll_and_find`, `get_screen_summary` | Content extraction |
| **comment-post** | `find_and_click`, `type_and_submit`, `smart_wait` | Posting comments |
| **patrol** | `run_patrol` | Automated monitoring |

---

## 2. mobile-mcp Server (Low-Level)

### Device Management

| Tool | Description | Parameters |
|------|-------------|------------|
| `mobile_list_available_devices` | List connected devices | `{ "noParams": {} }` (IMPORTANT) |
| `mobile_list_apps` | List installed apps | `device` |
| `mobile_launch_app` | Launch app by package | `device`, `packageName` |
| `mobile_terminate_app` | Stop running app | `device`, `packageName` |
| `mobile_install_app` | Install APK/IPA | `device`, `path` |
| `mobile_uninstall_app` | Remove app | `device`, `bundle_id` |

### Screen Interaction

| Tool | Description | Parameters |
|------|-------------|------------|
| `mobile_click_on_screen_at_coordinates` | Tap at x,y | `device`, `x`, `y` |
| `mobile_double_tap_on_screen` | Double tap | `device`, `x`, `y` |
| `mobile_long_press_on_screen_at_coordinates` | Long press | `device`, `x`, `y`, `duration` |
| `mobile_swipe_on_screen` | Swipe gesture | `device`, `direction`, `distance`, `x`, `y` |
| `mobile_type_keys` | Type text (Unicode supported) | `device`, `text`, `submit` |
| `mobile_press_button` | Hardware buttons | `device`, `button` (BACK, HOME, etc.) |

### Screen Information

| Tool | Description | Parameters |
|------|-------------|------------|
| `mobile_list_elements_on_screen` | Get accessibility tree | `device` |
| `mobile_take_screenshot` | Capture screen (returns image) | `device` |
| `mobile_save_screenshot` | Save screenshot to file | `device`, `saveTo` |
| `mobile_get_screen_size` | Get screen dimensions | `device` |
| `mobile_get_orientation` | Get portrait/landscape | `device` |
| `mobile_set_orientation` | Change orientation | `device`, `orientation` |

### Other

| Tool | Description | Parameters |
|------|-------------|------------|
| `mobile_open_url` | Open URL in browser | `device`, `url` |

### Skills Using mobile-mcp

| Skill | Tools Used | When to Use |
|-------|------------|-------------|
| **device-check** | `mobile_list_available_devices`, `mobile_list_apps` | Connectivity verification |
| **screen-analyze** | `mobile_list_elements_on_screen`, `mobile_take_screenshot` | UI analysis |
| **app-action** | All screen interaction tools | Single-step operations |
| **troubleshoot** | `mobile_list_available_devices`, `mobile_press_button` | Diagnosis |

---

## 3. filesystem Server

| Tool | Description | Use Case |
|------|-------------|----------|
| `read_text_file` | Read file contents | Load config, read data |
| `write_file` | Write file contents | Save extraction results |
| `edit_file` | Edit file in place | Modify config |
| `list_directory` | List directory contents | Browse outputs |
| `create_directory` | Create folder | Setup output dirs |
| `search_files` | Glob pattern search | Find files |

### Skills Using filesystem

| Skill | Tools Used |
|-------|------------|
| **content-extract** | `write_file`, `create_directory` |
| **article-extract** | `write_file` |
| **progress-report** | `write_file`, `read_text_file` |

---

## 4. fetch Server

| Tool | Description | Use Case |
|------|-------------|----------|
| `fetch` | Retrieve web content | Get documentation, verify URLs |

### Skills Using fetch

| Skill | Tools Used |
|-------|------------|
| **wechat-browse** | `fetch` (for fallback web content) |

---

## 5. context7 Server

| Tool | Description | Use Case |
|------|-------------|----------|
| `resolve-library-id` | Find library documentation ID | Get library info |
| `query-docs` | Query library documentation | API reference lookup |

### Skills Using context7

| Skill | Tools Used |
|-------|------------|
| (Internal reference only) | `query-docs` |

---

## Tool Selection Priority

### For Click Operations

```
1. find_and_click (macro) - Best: combines search + click + verify
2. mobile_click_on_screen_at_coordinates - When coordinates are known
3. Never: screenshot → guess → click
```

### For Element Discovery

```
1. mobile_list_elements_on_screen - Always try first (100ms)
2. get_screen_summary (macro) - When you need overview
3. mobile_take_screenshot - LAST resort, visual verification only
```

### For Text Input

```
1. type_and_submit (macro) - Handles focus + clear + type + submit
2. mobile_type_keys - Direct typing when field is focused
```

### For Navigation

```
1. navigate_back (macro) - Includes verification
2. mobile_press_button (BACK) - Direct button press
```

### For Scrolling

```
1. scroll_and_find (macro) - When searching for element
2. mobile_swipe_on_screen - When browsing content
```

---

## Skill → MCP Tool Matrix

| Skill | Primary Tools | Secondary Tools |
|-------|---------------|-----------------|
| **task-clarify** | (none - LLM reasoning only) | - |
| **progress-report** | filesystem: `write_file` | mobile-mcp: `mobile_save_screenshot` |
| **search-triage** | macro: `find_and_click`, `type_and_submit`, `scroll_and_find` | mobile-mcp: `mobile_list_elements_on_screen` |
| **comment-scan** | macro: `scroll_and_find`, `get_screen_summary` | mobile-mcp: `mobile_list_elements_on_screen` |
| **article-extract** | macro: `scroll_and_find`, `get_screen_summary` | filesystem: `write_file` |
| **wechat-browse** | macro: `launch_and_wait`, `find_and_click`, `scroll_and_find` | mobile-mcp: `mobile_list_elements_on_screen` |
| **comment-draft** | (none - LLM generation only) | - |
| **comment-post** | macro: `find_and_click`, `type_and_submit`, `smart_wait` | mobile-mcp: `mobile_type_keys` |
| **device-check** | mobile-mcp: `mobile_list_available_devices` | - |
| **screen-analyze** | mobile-mcp: `mobile_list_elements_on_screen` | mobile-mcp: `mobile_take_screenshot` |
| **app-action** | macro: `find_and_click`, `type_and_submit` | mobile-mcp: all interaction tools |
| **troubleshoot** | mobile-mcp: `mobile_list_available_devices`, `mobile_press_button` | - |
| **unicode-setup** | (ADB commands via Bash) | mobile-mcp: `mobile_type_keys` |
| **patrol** | macro: `run_patrol` | (encapsulates all others) |

---

## Important Notes

### mobile_list_available_devices Parameter

```json
// CORRECT
{ "noParams": {} }

// WRONG
{}
```

### Element-First Strategy

Always use `mobile_list_elements_on_screen` before `mobile_take_screenshot`:
- Element list: ~100ms, precise coordinates
- Screenshot: 2-5s, requires vision processing, imprecise

### Unicode Text Input

Requires DeviceKit APK installed:
```bash
adb install apk_tools/mobilenext-devicekit.apk
```

Then `mobile_type_keys` supports Chinese, Japanese, Korean text.

---

## Version

- Document version: 1.0
- Last updated: 2026-02-02
- Compatible with: mobile-mcp@latest, src.mcp_macro_server
