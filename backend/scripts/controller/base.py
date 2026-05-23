"""Base 控制器 - 系统基础 API"""
import sys
from http import HTTPStatus

from flask import Blueprint, request
from loguru import logger

from common.json_response import JsonResponse
from scripts.automation.automation import automationMgr
from scripts.config import app_config
from scripts.config.app_config import hot_fix_version
from scripts.service.CommonService import CommonService
from scripts.service.EnvironmentService import (
    check_wechat_version, checkBrowserInstallStatus, checkDocPath,
    checkOcrSupportStatus, checkWechatMultipleOpen, checkZoomSupportStatus,
)
from scripts.utils.browser import BrowserUtil
from scripts.utils.logger_util import LogLevelFilter
from scripts.utils.process import get_current_process_pids
from scripts.ws.bootstrap import ensure_websocket_started
from scripts.ws.ws_manager import WebSocketManager

bp = Blueprint("base", __name__)


@bp.route("/get-browser-path", methods=["GET"])
def get_browser_path():
    try:
        path = BrowserUtil().get_path_sync()
        return JsonResponse(code=HTTPStatus.OK, data={"path": path}).to_response()
    except Exception as e:
        logger.error(f"获取浏览器路径失败: {e}")
        return JsonResponse.error(msg="获取浏览器路径失败")


@bp.route("/get-python-version", methods=["GET"])
def get_python_version():
    return JsonResponse(code=HTTPStatus.OK, data={"python_version": hot_fix_version}).to_response()


@bp.route("/check-default-browser", methods=["GET"])
def check_default_browser():
    try:
        has_default = BrowserUtil().check_default_browser()
        return JsonResponse(code=HTTPStatus.OK, data={"has_default": has_default}).to_response()
    except Exception as e:
        logger.error(f"检查默认浏览器失败: {e}")
        return JsonResponse.error(msg="检查失败")


@bp.route("/thread-dump", methods=["GET"])
def thread_dump():
    frames = sys._current_frames()
    thread_info = [{"thread_id": tid, "frame": str(f)} for tid, f in frames.items()]
    return JsonResponse(code=HTTPStatus.OK, data=thread_info).to_response()


@bp.route("/service-start", methods=["POST"])
def service_start():
    return JsonResponse(code=HTTPStatus.OK, msg="服务启动成功").to_response()


@bp.route("/get-websocket-port", methods=["GET"])
def get_websocket_port():
    try:
        ws_manager = WebSocketManager()
        if not getattr(ws_manager, "running", False):
            ws_manager = ensure_websocket_started(host="0.0.0.0", start_port=8765)
        data = {
            "host": getattr(ws_manager, "host", "0.0.0.0"),
            "port": getattr(ws_manager, "port", 8765),
            "running": getattr(ws_manager, "running", False),
        }
        return JsonResponse(code=HTTPStatus.OK, msg="获取WebSocket端口成功", data=data).to_response()
    except Exception as e:
        logger.exception(f"获取WebSocket端口失败: {e}")
        return JsonResponse.error(msg="获取失败")


@bp.route("/set-automation-msg-id", methods=["POST"])
def set_automation_msg_id():
    try:
        data = request.get_json()
        msg_id = data.get("msgId")
        if not msg_id:
            return JsonResponse(code=400, msg="消息ID不能为空").to_response()
        logger.info(f"设置自动化消息ID: {msg_id}")
        return JsonResponse(code=200, msg="设置成功").to_response()
    except Exception as e:
        logger.error(f"设置消息ID失败: {e}")
        return JsonResponse.error(msg="设置失败")


@bp.route("/check-env", methods=["GET"])
def check_env():
    is_wx_available, current_wx_version, recommend_version = check_wechat_version()
    data = {
        "chrome": checkBrowserInstallStatus(),
        "wx": is_wx_available,
        "current_wx_version": current_wx_version,
        "recommend_wx_version": recommend_version,
        "documents_path": checkDocPath(),
        "is_multiple_open": checkWechatMultipleOpen(),
        "ocr_support_status": checkOcrSupportStatus(),
        "screen_zoom_support_status": checkZoomSupportStatus(),
    }
    app_config.can_use_ocr = data["ocr_support_status"]
    logger.debug(f"check_env: {data}")
    return JsonResponse(code=HTTPStatus.OK, msg="获取安装环境成功", data=data).to_response()


@bp.route("/get-process-pids", methods=["GET"])
def get_process_pids():
    data = {"pids": get_current_process_pids()}
    return JsonResponse(code=HTTPStatus.OK, msg="获取进程号成功", data=data).to_response()


@bp.route("/change-log-level", methods=["POST"])
def change_log_level():
    level = request.get_json().get("level", "INFO")
    allowed = ["INFO", "DEBUG", "ERROR", "WARNING", "ALL"]
    if level not in allowed:
        return JsonResponse(code=400, msg=f"日志等级只能是{allowed}").to_response()
    LogLevelFilter().changeLevel(level)
    return JsonResponse(code=HTTPStatus.OK, msg="改变日志等级成功",
                        data={"currentLevel": level}).to_response()


@bp.route("/get-performance-metrics", methods=["GET"])
def get_performance_metrics():
    try:
        import psutil
        data = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
        }
        return JsonResponse(code=200, msg="获取系统信息成功", data=data).to_response()
    except Exception as e:
        logger.exception(f"获取系统信息失败: {e}")
        return JsonResponse.error(msg="获取失败")


@bp.route("/upload-sys-log", methods=["POST"])
def upload_sys_log():
    suc = CommonService.upload_log()
    if suc:
        return JsonResponse.success()
    return JsonResponse.error()
