"""WeChat 控制器 - 微信自动化 API"""
import asyncio
import datetime
import json
import os
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus

from flask import Blueprint, request
from loguru import logger

from common.custom_enums import LocalConfigKey
from common.custom_types import ContactData
from common.json_response import JsonResponse
from scripts.automation.automation import automationMgr
from scripts.automation.automation_state import AutomationStateManager
from scripts.automation.simple_workflow import SimpleWorkflow
from scripts.config import app_config
from scripts.db.contact import ContactDBManger
from scripts.db.v4_message import V4Message
from scripts.service.FileCacheService import FileCacheService
from scripts.utils.common import get_local_config, set_local_config, batch_import_contents
from scripts.utils.time import is_later_than_cur_time, is_later_than_hour_cross_day
from scripts.wechat.wechat_controls import get_wx_controls
from scripts.wechat.WechatDb import WechatDb
from scripts.wechat_ocr.WechatOcrService import WechatOcrService
from scripts.wechat_ocr.WeChatOCRInstaller import WeChatOCRInstaller
from scripts.ws.remote_controll_handler import handle_workflow_auto_release

bp = Blueprint("wechat", __name__)
long_task_executor = ThreadPoolExecutor(4)


@bp.route("/is-wx-login", methods=["GET"])
def is_wx_login():
    try:
        from scripts.wechat_uia import is_login
        result = is_login()
        return JsonResponse.success(data={"isLogin": result})
    except Exception as e:
        logger.exception(f"检查微信登录状态失败: {e}")
        return JsonResponse.error(msg=f"检查失败: {e}")


@bp.route("/check-ocr-status", methods=["GET"])
def check_ocr_status():
    ocr_installer = WeChatOCRInstaller()
    file_status = ocr_installer.get_file_exists()
    data = {"ocr_file_status": file_status}
    if not file_status:
        ocr_installer.thread_start_download()
    else:
        ocr_service = WechatOcrService()
        ocr_service.init_ocr_service()
    return JsonResponse(code=HTTPStatus.OK, data=data).to_response()


@bp.route("/open-wx-controller", methods=["POST"])
def open_wx_controller():
    force_start = request.args.get("force_start", "false").lower() == "true"
    from scripts.wechat_uia import is_login
    is_login_status = is_login()
    can_use_ocr = app_config.can_use_ocr

    logger.info(f"微信登录状态: {is_login_status}, OCR支持: {can_use_ocr}, 强制启动: {force_start}")
    data = {"isLogin": is_login_status, "canUseOCR": can_use_ocr, "forceStart": force_start}

    if is_login_status or can_use_ocr or force_start:
        state = AutomationStateManager()
        state.set_cloud_task_active(False)
        long_task_executor.submit(automationMgr.run)
        msg = "微信启动成功"
        if force_start and not is_login_status:
            msg = "微信未登录但已强制启动自动化程序(部分功能受限)"
        elif force_start and not can_use_ocr:
            msg = "CPU不支持但已强制启动自动化程序(部分功能受限)"
        return JsonResponse(code=HTTPStatus.OK, msg=msg, data=data).to_response()

    msg = "微信未登录" if not is_login_status else "当前CPU不支持"
    return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg=msg, data=data).to_response()


@bp.route("/get-wx-contacts", methods=["GET"])
def get_wx_contacts():
    contacts = ContactDBManger().get_all()
    return JsonResponse.success(data=contacts)


@bp.route("/clear-all-wx-contacts", methods=["POST"])
def clear_all_wx_contacts():
    try:
        ContactDBManger().delete_all()
        return JsonResponse.success()
    except Exception as e:
        logger.exception(f"清空所有联系人数据失败: {e}")
        return JsonResponse.error()


@bp.route("/sync-database", methods=["POST"])
def sync_database():
    try:
        from scripts.wechat.contact_manager import silence_sync
        wechat_db = WechatDb()
        suc, reason, _ = wechat_db.main_export_db_file()
        if suc:
            silence_sync()
            return JsonResponse(code=HTTPStatus.OK, msg="同步成功").to_response()
        return JsonResponse(code=HTTPStatus.INTERNAL_SERVER_ERROR,
                            msg=f"静默同步失败, {reason}").to_response()
    except Exception as e:
        logger.exception(f"同步数据库失败: {e}")
        return JsonResponse(code=HTTPStatus.INTERNAL_SERVER_ERROR, msg="同步失败").to_response()


@bp.route("/start-workflow", methods=["POST"])
def start_workflow():
    try:
        params = request.get_json() or {}
        workflow_type = params.get("type", 1)
        if workflow_type == 1:
            from scripts.scheduler.manager import SchedulerManager
            SchedulerManager().add_clip_workflow_scheduler()
            start_time = get_local_config("auto_clip_timing", "00:00")
            need_execute = is_later_than_hour_cross_day(datetime.datetime.now(), start_time)
            if need_execute:
                asyncio.run(handle_workflow_auto_release({}))
        else:
            start_time = get_local_config("simple_workflow_start_time", "00:00")
            need_execute = is_later_than_cur_time(start_time)
            if need_execute:
                SimpleWorkflow().start()
        return JsonResponse(code=HTTPStatus.OK, msg="工作流开启成功").to_response()
    except Exception as e:
        logger.exception(f"工作流开启失败: {e}")
        return JsonResponse.error(msg="工作流开启失败")


@bp.route("/upsert-contact-manually", methods=["POST"])
def upsert_contact_manually():
    try:
        params = request.get_json() or {}
        data_type = params.get("type", "user")
        nickname = params.get("nickName", "")
        wx_id = params.get("wxId", nickname) if data_type == "user" else nickname
        remark = params.get("remark", "") if data_type == "user" else nickname
        tags = params.get("tags", "")
        member_count = params.get("memberCount", 0)
        data_id = params.get("id")
        if data_type == "user" and not wx_id:
            return JsonResponse.error(msg="微信号不能为空")
        ContactDBManger().upsert(ContactData(
            nickname=nickname, wx_id=wx_id, remark=remark,
            type=data_type, tags=tags, member_count=member_count, id=data_id,
        ))
        logger.info(f"联系人编辑成功: {data_id}_{wx_id}")
        return JsonResponse.success()
    except Exception as e:
        logger.exception(f"手动新增联系人或群聊失败: {e}")
        return JsonResponse.error()


@bp.route("/delete-contact-manually", methods=["POST"])
def delete_contact_manually():
    try:
        params = request.get_json() or {}
        data_id = params.get("id")
        if not data_id:
            return JsonResponse.error(msg="联系人不存在")
        ContactDBManger().delete(data_id)
        logger.info(f"联系人删除成功: {data_id}")
        return JsonResponse.success()
    except Exception as e:
        logger.exception(f"手动删除联系人失败: {e}")
        return JsonResponse.error()


@bp.route("/set-wx-auto-login", methods=["POST"])
def set_wx_auto_login():
    data = request.get_json() or {}
    auto_login_config = data.get("auto_login_config", {})
    set_local_config("wx_auto_login", json.dumps(auto_login_config))
    return JsonResponse.success()


@bp.route("/get-wx-auto-login", methods=["GET"])
def get_wx_auto_login():
    config = get_local_config("wx_auto_login", "{}")
    return JsonResponse.success(data={"auto_login_config": config})


@bp.route("/batch-add-contact", methods=["POST"])
def batch_add_contact():
    try:
        data = request.get_json() or {}
        file_path = data.get("file_path")
        if not file_path:
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少文件路径参数", data={"success": False}).to_response()
        if not os.path.exists(file_path):
            return JsonResponse(code=HTTPStatus.NOT_FOUND, msg="文件不存在", data={"success": False}).to_response()
        if not file_path.endswith((".txt", ".xlsx")):
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="不支持的文件格式，仅支持 .txt 和 .xlsx 文件",
                                data={"success": False}).to_response()
        contact_list = batch_import_contents(file_path)
        return JsonResponse(code=HTTPStatus.OK, msg="批量添加联系人完成",
                            data={"contact_list": contact_list, "success": True}).to_response()
    except ValueError as e:
        logger.error(f"Excel文件处理错误: {e}")
        return JsonResponse.error(msg="Excel文件处理错误")
    except KeyError:
        logger.error(f"Excel文件中缺少微信号列")
        return JsonResponse.error(msg="文件中缺少微信号列")
    except Exception as e:
        logger.exception(f"处理文件失败: {e}")
        return JsonResponse.error(msg="处理文件失败")
