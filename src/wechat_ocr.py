"""
微信 OCR 服务 - 基于汇编改编
原始: WechatOcrService.pyc (30KB) - 仅反汇编

功能:
  1. 对微信窗口截图并OCR识别文字
  2. 定位微信界面中的特定图标/按钮
  3. 检测未读消息
  4. 发送消息到文件传输助手
"""
import time
from typing import Dict, List, Optional, Tuple

from loguru import logger

from scripts.wechat_uia import get_wx, is_login


class WechatOcrService:
    """微信 OCR 服务"""

    def __init__(self):
        self._initialized = False
        self._window_rect = None
        self.db_key = ""

    def init_ocr_service(self):
        """初始化OCR服务"""
        self._initialized = True
        logger.info("OCR服务已初始化")

    def has_db_key(self) -> bool:
        """是否有数据库密钥(OCR可读数据库)"""
        return bool(self.db_key)

    # ---- 窗口管理 ----

    def find_wechat_window(self) -> bool:
        """找微信窗口"""
        hwnd = self._find_window_internal()
        return hwnd is not None

    def get_wechat_window_rect(self) -> Optional[Dict]:
        """获取窗口尺寸"""
        wx = get_wx()
        if wx.win:
            try:
                r = wx.win.BoundingRectangle
                return {"left": r.left, "top": r.top, "width": r.width(), "height": r.height()}
            except:
                pass
        return None

    def ensure_wechat_window_rect(self):
        """确保窗口位置"""
        pass

    def check_wechat_is_login(self) -> bool:
        """检查微信是否登录"""
        return is_login()

    def activate_wechat_window(self):
        """激活微信窗口"""
        wx = get_wx()
        if wx.win:
            wx.win.SetActive()

    # ---- 截图与OCR ----

    def screenshot_position(self, x: int, y: int, w: int, h: int) -> bytes:
        """截图指定区域"""
        import pyautogui
        img = pyautogui.screenshot(region=(x, y, w, h))
        return img.tobytes()

    def ocr_location(self, image: bytes) -> List[Dict]:
        """OCR识别图片中的文字"""
        # TODO: 接入实际OCR引擎
        return []

    def ocr_result_callback(self, texts: list):
        """OCR结果回调"""
        pass

    def red_bg_to_white_and_text_to_black(self, img) -> bytes:
        """红底转白底, 文字转黑色(红包识别)"""
        return img

    def find_red_pic_to_number(self) -> int:
        """找红包中的数字"""
        return 0

    # ---- 图标定位 ----

    def find_smile_icon_pos_by_ocr(self) -> Optional[Tuple[int, int]]:
        """定位表情图标"""
        return None

    def find_send_button_pos_by_ocr(self) -> Optional[Tuple[int, int]]:
        """定位发送按钮"""
        return None

    def rect_find_icon_position(self, icon_type: str) -> Optional[Tuple[int, int, int, int]]:
        """通过OCR找图标位置"""
        return None

    def handle_icon_position(self, icon_type: str) -> bool:
        """处理图标点击"""
        return False

    # ---- 聊天相关 ----

    def get_current_user_name(self) -> str:
        """获取当前聊天用户名"""
        wx = get_wx()
        if wx.win:
            try:
                # 尝试读取当前聊天标题
                bar = wx.win.ToolBarControl(Name="导航", searchDepth=3)
                if bar.Exists(1):
                    sibling = bar.GetNextSiblingControl()
                    if sibling:
                        return sibling.Name or ""
            except:
                pass
        return ""

    def get_chat_title(self) -> str:
        return self.get_current_user_name()

    def handle_chat_window_position(self):
        """调整聊天窗口位置"""
        pass

    # ---- 未读消息检测 ----

    def get_wechat_unread_count(self) -> int:
        """获取总未读数"""
        from scripts.wechat_uia import get_unread
        return len(get_unread())

    def click_chat_list_first_red(self) -> bool:
        """点击第一条未读消息"""
        from scripts.wechat_uia import goto_unread
        name, _ = goto_unread()
        return bool(name)

    def in_first_chat_group(self) -> bool:
        """是否在第一个对话中"""
        return True

    def click_unread_btn(self):
        """点击未读按钮"""
        pass

    # ---- 消息发送 ----

    def send_msg_to_file_helper(self, msg: str):
        """发送消息到文件传输助手"""
        from scripts.wechat_uia import enter_conversation, send_text
        if enter_conversation("文件传输助手"):
            send_text(msg)

    def input_msg(self, text: str):
        """输入消息"""
        import pyperclip, uiautomation
        pyperclip.copy(text)
        uiautomation.SendKeys("{Ctrl}v}", waitTime=0.2)

    # ---- 内部 ----

    def _find_window_internal(self):
        from scripts.wechat_uia import find_window
        return find_window()
