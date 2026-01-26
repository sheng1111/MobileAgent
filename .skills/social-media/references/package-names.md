# Social Media Package Names Reference

Complete Android package name list for launching and identifying apps.

## Major Platforms

| Platform | Package Name | Notes |
|----------|-------------|-------|
| LINE | `jp.naver.line.android` | - |
| LINE Lite | `com.linecorp.linelite` | Lightweight version |
| Facebook | `com.facebook.katana` | Main app |
| Facebook Lite | `com.facebook.lite` | Lightweight version |
| Messenger | `com.facebook.orca` | FB Messenger |
| Messenger Lite | `com.facebook.mlite` | Lightweight version |
| Instagram | `com.instagram.android` | - |
| Threads | `com.instagram.barcelona` | - |
| WhatsApp | `com.whatsapp` | - |
| WhatsApp Business | `com.whatsapp.w4b` | - |
| WeChat | `com.tencent.mm` | - |
| X (Twitter) | `com.twitter.android` | Package name unchanged after rebrand |
| Telegram | `org.telegram.messenger` | - |
| Telegram X | `org.thunderdog.challegram` | Alternative client |
| TikTok | `com.zhiliaoapp.musically` | International version |
| Douyin | `com.ss.android.ugc.aweme` | China version |
| Xiaohongshu | `com.xingin.xhs` | REDnote |
| Discord | `com.discord` | - |
| Snapchat | `com.snapchat.android` | - |
| Pinterest | `com.pinterest` | - |
| LinkedIn | `com.linkedin.android` | - |
| Reddit | `com.reddit.frontpage` | - |
| Tumblr | `com.tumblr` | - |
| Signal | `org.thoughtcrime.securesms` | - |

## Regional Platforms

### Asia

| Platform | Package Name | Notes |
|----------|-------------|-------|
| KakaoTalk | `com.kakao.talk` | Korea |
| BAND | `com.naver.band` | Korea |
| QQ | `com.tencent.mobileqq` | China |
| Weibo | `com.sina.weibo` | China |
| Bilibili | `tv.danmaku.bili` | China |
| Douban | `com.douban.frodo` | China |
| VK | `com.vkontakte.android` | Russia |

### Japan

| Platform | Package Name | Notes |
|----------|-------------|-------|
| mixi | `jp.mixi` | - |
| Ameba | `jp.ameba` | - |

## Dating Apps

| Platform | Package Name | Notes |
|----------|-------------|-------|
| Tantan (探探) | `com.p1.mobile.putong` | Asia |
| Tinder | `com.tinder` | Global |
| Bumble | `com.bumble.app` | Global |
| Hinge | `co.hinge.app` | Global |
| OkCupid | `com.okcupid.okcupid` | Global |
| Pairs | `jp.eure.android.pairs` | Japan/Taiwan |
| Soul | `cn.soulapp.android` | China |
| Momo (陌陌) | `com.immomo.momo` | China |
| Badoo | `com.badoo.mobile` | Global |
| Coffee Meets Bagel | `com.coffeemeetsbagel.android` | Global |
| Happn | `com.ftw_and_co.happn` | Global |
| Match | `com.match.android.matchmobile` | Global |

## Finding Package Names

To find package names not listed here:

```bash
# Search installed packages
adb shell pm list packages | grep -i <keyword>

# Examples
adb shell pm list packages | grep -i line
adb shell pm list packages | grep -i facebook
adb shell pm list packages | grep -i instagram
```

## Launching Apps

**MCP:**
```
mobile_launch_app with packageName: "jp.naver.line.android"
```

**Python:**
```python
from src.adb_helper import ADBHelper
adb = ADBHelper()
adb.launch_app("jp.naver.line.android")
```

## Notes

1. **Version variants**: Same app may have standard and Lite versions with different package names
2. **Regional versions**: Some apps have separate versions for different regions (e.g., TikTok/Douyin)
3. **Rebranding**: Twitter rebranded to X but package name remains `com.twitter.android`
4. **Availability**: Some apps only available in specific regional Play Stores
