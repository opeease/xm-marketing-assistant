"""
微信 UIA 操控层
===============
纯 Windows UI Automation 控制微信客户端, 不依赖任何后端/数据库

操作清单:
  窗口:    find_window, connect, click_tab
  会话:    list_conversations, get_unread, enter_conversation, goto_unread
  消息:    get_messages, send_text, send_file, send_reply
  联系人:  list_contacts, click_contact, set_remark
  好友:    new_contact_count, accept_contacts
  群发:    send_to_contacts
  状态:    is_login, is_chat_room
"""
import re
import time
import threading
from typing import Dict, List, Optional, Tuple

import psutil
import uiautomation
import win32gui
import win32process
from loguru import logger

# ============================================================
# 全局配置
# ============================================================

SEARCH_TIMEOUT = 3       # UIA 控件搜索超时(秒)
SEND_INTERVAL = 0.5      # 发送消息间隔(秒)
WECHAT_NAMES = {"wechat.exe", "weixin.exe", "WeChat.exe", "WeChatAppEx.exe", "Weixin.exe"}

# 微信4.x导航栏按钮名称
NAV_CHAT = "WeChat"       # 聊天
NAV_CONTACTS = "通讯录"    # 通讯录

# 系统消息过滤
_SYS_MSG_PATTERNS = [
    r"^\[.*\].*可以开始聊天", r"^查看更多消息$", r"^以下是新消息$",
    r"^以下为新消息$", r"^微信转账$", r"^\d{4}年\d{1,2}月\d{1,2}日 \d{1,2}:\d{2}$",
    r"^.+?邀请.+?加入群聊", r"^.+?不是朋友关系", r"^.+?修改群名为.+?",
    r"^昨天 \d{1,2}:\d{2}$", r"^今天 \d{1,2}:\d{2}$",
    r"^星期[一二三四五六日] \d{1,2}:\d{2}$", r"^\d{4}-\d{2}-\d{2} \d{1,2}:\d{2}$",
]
_SYS_MSG_RE = re.compile("|".join(f"({p})" for p in _SYS_MSG_PATTERNS))

# 过滤的联系人
_SKIP_NAMES = {"新的朋友", "公众号", "搜索", "群聊", "订阅号", "视频号", "文件传输助手", "微信团队"}

_LOCK = threading.Lock()


# ============================================================
# 微信窗口查找
# ============================================================

def find_window() -> Optional[int]:
    """通过进程名+窗口尺寸找微信主窗口句柄"""
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            name = (proc.info.get("name") or "").lower()
            if not any(w in name for w in WECHAT_NAMES):
                continue
            pid = proc.info["pid"]

            def enum_cb(hwnd, result):
                _, p = win32process.GetWindowThreadProcessId(hwnd)
                if p == pid and win32gui.IsWindowVisible(hwnd):
                    t = win32gui.GetWindowText(hwnd)
                    r = win32gui.GetWindowRect(hwnd)
                    # WeChat 4.x 标题是 "WeChat", 旧版是 "微信"
                    if t and (r[2] - r[0]) > 400:
                        result.append(hwnd)
                return True

            hwnds = []
            win32gui.EnumWindows(enum_cb, hwnds)
            if hwnds:
                return max(hwnds, key=lambda h: win32gui.GetWindowRect(h)[2] * win32gui.GetWindowRect(h)[3])
        except Exception:
            continue
    return 0


def is_login() -> bool:
    """检查微信是否已登录"""
    hwnd = find_window()
    if not hwnd:
        return False
    try:
        return uiautomation.ControlFromHandle(hwnd).Exists(1)
    except Exception:
        return False


# ============================================================
# 微信窗口封装
# ============================================================

class WeChatWindow:
    """微信主窗口封装"""

    def __init__(self):
        self.hwnd: int = 0
        self.win: uiautomation.Control = None
        self.nav: uiautomation.Control = None
        self.sessions: uiautomation.Control = None

    def connect(self) -> bool:
        """连接到微信窗口"""
        with _LOCK:
            self.hwnd = find_window()
            if not self.hwnd:
                logger.error("未找到微信窗口")
                return False
            uiautomation.SetGlobalSearchTimeout(SEARCH_TIMEOUT)
            self.win = uiautomation.ControlFromHandle(self.hwnd)
            self.win.SetActive()
            time.sleep(0.3)
            self.nav = self.win.ToolBarControl(Name="导航", searchDepth=3)
            self.sessions = self.win.ListControl(Name="会话", searchDepth=4)
            return True

    def click_chat(self):
        """点击导航栏的聊天按钮(WeChat 4.x = 'WeChat')"""
        try:
            self.win.ButtonControl(Name=NAV_CHAT, searchDepth=5).Click()
            time.sleep(0.2)
        except Exception:
            # 兼容旧版
            self.win.ButtonControl(Name="聊天", searchDepth=5).Click()
            time.sleep(0.2)

    def click_contacts(self):
        """点击导航栏的通讯录按钮"""
        try:
            self.win.ButtonControl(Name=NAV_CONTACTS, searchDepth=5).Click()
            time.sleep(0.2)
        except Exception:
            pass


_wx: Optional[WeChatWindow] = None


def get_wx() -> WeChatWindow:
    global _wx
    if _wx is None or not _wx.win:
        _wx = WeChatWindow()
    return _wx


# ============================================================
# 会话操作
# ============================================================

def enter_conversation(name: str) -> bool:
    """Ctrl+F 搜索并进入指定会话
    微信4.x: 搜索弹窗是 WindowControl "Weixin", 结果是 ListItemControl
    """
    wx = get_wx()
    if not wx.win and not wx.connect():
        return False
    wx.win.SetActive()
    wx.win.SwitchToThisWindow()
    time.sleep(0.2)

    if not name:
        return False

    # Ctrl+F 打开搜索
    uiautomation.SendKeys("{Ctrl}F")
    time.sleep(0.5)
    import pyperclip
    pyperclip.copy(name)
    uiautomation.SendKeys("{Ctrl}a", waitTime=0.2)
    uiautomation.SendKeys("{Ctrl}v", waitTime=0.2)
    time.sleep(0.5)

    # 微信4.x: 搜索弹窗是主窗口内的 WindowControl "Weixin"
    search_win = wx.win.WindowControl(Name="Weixin", searchDepth=1)
    if search_win.Exists(maxSearchSeconds=2):
        # 查找匹配的联系人
        for child in search_win.GetChildren():
            try:
                item_name = child.Name
                if not item_name:
                    continue
                if item_name in ("最常使用", "群聊", "聊天记录", "搜索网络结果"):
                    continue
                if name in item_name or item_name in name:
                    child.Click()
                    time.sleep(0.5)
                    return True
            except:
                pass
        # 没找到精确匹配，回车选第一个
        uiautomation.SendKeys("{Enter}", waitTime=0.3)
        time.sleep(0.5)
        return True

    # 旧版微信3.x: ListControl(Name="@str:IDS_FAV_SEARCH_RESULT:3780")
    result = uiautomation.ListControl(Name="@str:IDS_FAV_SEARCH_RESULT:3780")
    if result.Exists(2):
        label = result.TextControl(RegexName="联系人|群聊")
        if label.Exists(1):
            uiautomation.SendKeys("{Enter}")
            time.sleep(0.3)
            return True
        logger.error("没有联系人标签")
        uiautomation.SendKeys("{Esc}")
        return False
    logger.error("没有悬浮窗口")
    uiautomation.SendKeys("{Esc}")
    return False


def list_conversations() -> List[Dict]:
    """获取会话列表 [{name, unread}, ...]"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return []
    wx.click_chat()

    result = []
    seen = set()

    def scan(ctrl, depth=30):
        nonlocal result, seen
        if depth <= 0:
            return
        try:
            for c in ctrl.GetChildren():
                try:
                    name = c.Name
                    if name and "\n" in name:
                        r = c.BoundingRectangle
                        if 280 <= r.width() <= 320 and 60 <= r.height() <= 100:
                            if name not in seen:
                                seen.add(name)
                                conv_name = name.split("\n")[0].strip()
                                if conv_name and conv_name not in _SKIP_NAMES:
                                    result.append({"name": conv_name, "unread": 0})
                    scan(c, depth - 1)
                except:
                    pass
        except:
            pass

    scan(wx.win)

    if not result:
        convs = wx.win.ListControl(Name="会话", searchDepth=4)
        if convs.Exists(1):
            for child in convs.GetChildren():
                try:
                    name = child.Name
                    if not name or name in _SKIP_NAMES:
                        continue
                    unread = 0
                    for c in reversed(child.GetChildren()):
                        if hasattr(c, "Name") and c.Name and c.Name.isdigit():
                            unread = int(c.Name)
                            break
                    result.append({"name": name.replace(f"{unread}条新消息", "").strip(), "unread": unread})
                except:
                    pass
    return result


def get_unread() -> List[Dict]:
    """获取有未读消息的会话"""
    return [c for c in list_conversations() if c["unread"] > 0]


def goto_unread() -> Tuple[str, int]:
    """跳转到第一条未读会话, 返回(会话名, 未读数)"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return ("", 0)
    # WeChat 4.x: ListItemControl
    items = wx.win.ListItemControl(searchDepth=10)
    if items.Exists(1):
        for item in items.GetChildren():
            try:
                name = item.Name
                if not name:
                    continue
                conv_name = name.split("\n")[0].strip()
                if not conv_name or conv_name in _SKIP_NAMES:
                    continue
                item.Click()
                time.sleep(0.3)
                return (conv_name, 1)
            except Exception:
                continue
    # 降级: 旧版 ListControl
    convs = wx.win.ListControl(Name="会话", searchDepth=4)
    if convs.Exists(1):
        for child in convs.GetChildren():
            try:
                sub = child.GetChildren()
                if len(sub) >= 3 and sub[-1].Name.isdigit():
                    unread = int(sub[-1].Name)
                    name = child.Name.replace(f"{unread}条新消息", "").strip()
                    child.Click()
                    time.sleep(0.3)
                    return (name, unread)
            except Exception:
                continue
    return ("", 0)


def is_chat_room() -> bool:
    """判断当前是否是群聊"""
    wx = get_wx()
    bar = wx.win.ToolBarControl(searchDepth=5)
    if bar.Exists(0.5):
        last = bar.GetLastChildControl()
        if last.Name == "语音聊天":
            return True
    return False


# ============================================================
# 消息读取 / 发送
# ============================================================

def _is_from_other(msg_ctrl) -> bool:
    """判断消息是否来自对方"""
    children = msg_ctrl.GetChildren()
    if not children:
        return False
    try:
        r = children[0].BoundingRectangle
        return r.width() >= 20 and r.height() >= 20
    except Exception:
        return False


def _filter_msg(msg: str) -> bool:
    return msg and not _SYS_MSG_RE.fullmatch(msg)


def get_messages(max_count: int = 50) -> List[Dict]:
    """获取当前会话消息 [{role, sender, content}, ...]"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return []
    chat_list = wx.win.ListControl(Name="消息", searchDepth=5)
    if not chat_list.Exists(1):
        chat_list = wx.sessions.GetNextSiblingControl()

    items = chat_list.GetChildren()
    items = items[-max_count:] if len(items) > max_count else items

    msgs = []
    for item in items:
        try:
            text = item.Name
            if not _filter_msg(text):
                continue
            role = "user" if _is_from_other(item) else "assistant"
            sender = ""
            children = item.GetChildren()
            if children and hasattr(children[0], "Name"):
                if children[0].BoundingRectangle.width() > 20:
                    sender = children[0].Name
            msgs.append({"role": role, "sender": sender or ("other" if role == "user" else "me"), "content": text})
        except Exception:
            continue
    return msgs


def send_text(text: str, press_enter: bool = True):
    """剪贴板方式发送文本"""
    if not text:
        return
    import pyperclip
    with _LOCK:
        time.sleep(SEND_INTERVAL)
        pyperclip.copy(text)
        time.sleep(0.2)
        uiautomation.SendKeys("{Ctrl}a")
        time.sleep(0.1)
        uiautomation.SendKeys("{Delete}")
        time.sleep(0.2)
        uiautomation.SendKeys("{Ctrl}v")
        time.sleep(0.3)
        if press_enter:
            uiautomation.SendKeys("{Enter}")
            time.sleep(0.3)


def send_reply(text: str):
    send_text(text, press_enter=True)


# ============================================================
# 联系人 / 好友
# ============================================================

def list_contacts() -> List[Dict]:
    """获取联系人列表"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return []
    wx.click_contacts()
    lst = wx.win.ListControl(searchDepth=4)
    result = []
    for child in lst.GetChildren():
        try:
            name = child.Name
            if name and name not in _SKIP_NAMES:
                result.append({"name": name})
        except Exception:
            continue
    return result


def click_contact(name: str) -> bool:
    """在联系人列表点击指定联系人"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return False
    wx.click_contacts()
    for child in wx.win.ListControl(searchDepth=4).GetChildren():
        try:
            if child.Name == name:
                child.Click()
                return True
        except Exception:
            continue
    return False


def new_contact_count() -> int:
    """待处理好友请求数"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return 0
    wx.click_contacts()
    btn = wx.win.ButtonControl(Name="新的朋友", searchDepth=3)
    if btn.Exists(0.5):
        try:
            v = btn.GetNextSiblingControl()
            if v and v.Name.isdigit():
                return int(v.Name)
        except Exception:
            pass
    return 0


def accept_contacts(max_n: int = 20) -> int:
    """批量通过好友请求"""
    n = new_contact_count()
    if not n:
        return 0
    wx = get_wx()
    wx.win.ButtonControl(Name="新的朋友", searchDepth=3).Click()
    time.sleep(0.5)
    accepted = 0
    for i, child in enumerate(wx.win.ListControl(searchDepth=4).GetChildren()):
        if i >= max_n:
            break
        try:
            btn = child.ButtonControl(Name="接受", searchDepth=2)
            if btn.Exists(0.3):
                btn.Click()
                time.sleep(0.5)
                accepted += 1
        except Exception:
            continue
    uiautomation.SendKeys("{Esc}")
    return accepted


def set_remark(label: str) -> bool:
    """为当前聊天对象设置备注"""
    wx = get_wx()
    if not wx.win and not wx.connect():
        return False
    try:
        info = wx.win.ButtonControl(Name="聊天信息", searchDepth=3)
        if not info.Exists(1):
            return False
        info.Click()
        time.sleep(0.3)
        detail = wx.win.GetFirstChildControl()
        avatar = detail.ListControl(Name="聊天成员").GetFirstChildControl()
        nick = avatar.Name
        avatar.Click()
        time.sleep(0.3)
        rl = detail.TextControl(Name="备注", searchDepth=2)
        if not rl.Exists(1):
            return False
        rv = rl.GetNextSiblingControl().TextControl()
        rv.MoveCursorToMyCenter()
        edit = rl.GetParentControl().GetParentControl().ButtonControl()
        edit.Click()
        time.sleep(0.3)
        import pyperclip
        rv.SendKeys("{Ctrl}a"); rv.SendKeys("{Delete}")
        time.sleep(0.3)
        pyperclip.copy(f"{label}-{nick}")
        rv.SendKeys("{Ctrl}v"); rv.SendKeys("{Enter}")
        rv.SendKeys("{Esc}"); rv.SendKeys("{Esc}")
        return True
    except Exception as e:
        logger.error(f"set_remark 失败: {e}")
    return False


# ============================================================
# 群发
# ============================================================

def send_to_many(names: List[str], text: str) -> Dict[str, bool]:
    """向多个联系人群发消息"""
    result = {}
    for name in names:
        try:
            if not enter_conversation(name):
                result[name] = False
                continue
            time.sleep(0.5)
            send_text(text)
            result[name] = True
        except Exception as e:
            logger.error(f"[{name}] 群发失败: {e}")
            result[name] = False
    return result