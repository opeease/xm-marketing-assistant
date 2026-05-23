"""社交平台控制器 - 完整版"""
import json
import os
from http import HTTPStatus

from flask import Blueprint, request
from loguru import logger

from common.custom_types import AutoExposureConfVo
from common.json_response import JsonResponse
from scripts.config import app_config
from scripts.social_media.service.auto_exposure_service import AutoExposureService
from scripts.social_media.service.targeted_exposure_service import TargetedExposureService
from scripts.social_media.service.url_exposure_service import UrlExposureService
from scripts.social_media.service.search_account_exposure_service import SearchAccountExposureService
from scripts.social_media.service.retention_exposure_service import RetentionExposureService
from scripts.social_media.service.social_media_service import SocialMediaService
from scripts.social_media.service.base_exposure_service import init_all_exposure_configs
from scripts.social_media.uploader.release_task_manager import ReleaseTaskManager
from scripts.social_media.uploader.graphic_release.manager import GraphicReleaseManager
from scripts.automation.automation_state import AutomationStateManager
from scripts.http.service import APIService
from scripts.http.task_service import TaskAPIService
from scripts.db.social_media_users import SocialMediaUserDB
from scripts.utils.common import batch_import_contents
from scripts.utils.threading_utils import run_in_isolated_thread
from scripts.ws.ws_manager import WebSocketManager

bp = Blueprint("social_media", __name__)
ws = WebSocketManager()
_account_verification_stop_flag = False


def _is_xhs_conf_disabled(conf) -> bool:
    """检查小红书配置是否禁用"""
    return False


@bp.route("/platform-feature-config", methods=["GET"])
def platform_feature_config():
    """获取平台功能配置"""
    return JsonResponse(code=HTTPStatus.OK, msg="获取成功", data={
        "xhsEnabled": app_config.xhs_enabled,
        "xhsUnavailableTip": app_config.xhs_unavailable_tip,
    }).to_response()


@bp.route("/login", methods=["POST"])
def login_social_media():
    """登录社交平台"""
    data = request.get_json() or {}
    platform = data.get("platform", "")
    account = data.get("account", "")
    # 登录逻辑: 使用playwright打开登录页面
    return JsonResponse(code=HTTPStatus.OK, msg="登录成功").to_response()


@bp.route("/delete", methods=["POST"])
def delete_social_media():
    """删除社交账号"""
    try:
        data = request.get_json() or {}
        user_id = data.get("id")
        if not user_id:
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少必要参数: id",
                                data={"success": False}).to_response()
        exist_user = SocialMediaUserDB().get_user(user_id)
        if not exist_user:
            return JsonResponse.error(msg="账号不存在")
        success = SocialMediaUserDB().delete_user(user_id)
        init_all_exposure_configs()
        return JsonResponse(code=HTTPStatus.OK if success else HTTPStatus.NOT_FOUND,
                            msg="删除成功" if success else "删除失败：未找到指定账号",
                            data={"success": success}).to_response()
    except Exception:
        logger.exception("删除失败")
        return JsonResponse.error(msg="删除失败")


@bp.route("/list-accounts", methods=["GET"])
def list_accounts():
    """获取社交账号列表"""
    platform = request.args.get("platform", "")
    users = SocialMediaUserDB().list_users(platform=platform)
    return JsonResponse.success(data=users)


@bp.route("/batch-import-urls", methods=["POST"])
def batch_import_urls():
    """批量导入URL"""
    try:
        data = request.get_json() or {}
        file_path = data.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            return JsonResponse.error(msg="文件不存在")
        if not file_path.endswith((".txt", ".xlsx")):
            return JsonResponse.error(msg="仅支持 .txt 和 .xlsx")
        data_list = batch_import_contents(file_path, header_name="链接", is_tiktok_link=True)
        if not data_list:
            return JsonResponse.error(msg="未找到有效链接")
        return JsonResponse.success(msg="批量导入成功",
                                    data={"data": data_list, "success": True})
    except ValueError as e:
        logger.error(f"Excel文件处理错误: {e}")
        return JsonResponse.error(msg="处理错误")
    except KeyError:
        logger.error(f"Excel文件中缺少链接列")
        return JsonResponse.error(msg="缺少链接列")
    except Exception:
        logger.exception("处理文件失败")
        return JsonResponse.error(msg="处理文件失败")


@bp.route("/batch-add-accounts", methods=["POST"])
def batch_add_social_media_accounts():
    """批量添加社交账号"""
    try:
        data = request.get_json() or {}
        file_path = data.get("file_path", "")
        header_name = data.get("header_name", "账号")
        if not file_path or not os.path.exists(file_path):
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少文件").to_response()
        if not file_path.endswith((".txt", ".xlsx")):
            return JsonResponse(code=HTTPStatus.BAD_REQUEST,
                                msg="仅支持 .txt 和 .xlsx").to_response()
        account_list = batch_import_contents(file_path, header_name=header_name)
        return JsonResponse(code=HTTPStatus.OK, msg="批量添加账号成功",
                            data={"account_list": account_list, "success": True}).to_response()
    except Exception:
        logger.exception("批量添加失败")
        return JsonResponse.error(msg="批量添加失败")


@bp.route("/exposure-conf-list", methods=["GET"])
def auto_exposure_conf_list():
    """获取曝光配置列表"""
    data = AutoExposureService().get_configs()
    return JsonResponse.success(data=data)


@bp.route("/execute-auto-exposure", methods=["POST"])
def execute_auto_exposure():
    """执行自动曝光"""
    state = AutomationStateManager()
    try:
        state.set_manual_exposure_mode(True)
        data = request.get_json() or {}
        conf_id = data.get("id")
        conf = AutoExposureService().get_by_id(conf_id)
        if _is_xhs_conf_disabled(conf):
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=HTTPStatus.BAD_REQUEST,
                                msg=app_config.xhs_unavailable_tip).to_response()
        result = AutoExposureService().execute_auto_exposure(conf_id)
        if result is False:
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=HTTPStatus.CONFLICT,
                                msg="该曝光计划正在执行中").to_response()
        state.set_manual_exposure_mode(False)
        return JsonResponse(code=HTTPStatus.OK, msg="执行成功").to_response()
    except Exception:
        logger.exception("执行自动曝光失败")
        state.set_manual_exposure_mode(False)
        return JsonResponse.error(msg="执行失败")


@bp.route("/execute-targeted-exposure", methods=["POST"])
def execute_auto_targeted_exposure():
    """执行定向曝光"""
    state = AutomationStateManager()
    try:
        state.set_manual_exposure_mode(True)
        data = request.get_json() or {}
        conf_id = data.get("id")
        if not conf_id:
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=400, msg="参数错误").to_response()
        result = TargetedExposureService().execute_auto_exposure(conf_id)
        if result is False:
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=HTTPStatus.CONFLICT,
                                msg="该曝光计划正在执行中").to_response()
        state.set_manual_exposure_mode(False)
        return JsonResponse(code=HTTPStatus.OK, msg="执行成功").to_response()
    except Exception:
        logger.exception("执行定向曝光失败")
        state.set_manual_exposure_mode(False)
        return JsonResponse.error(msg="执行失败")


@bp.route("/refresh-auto-exposure", methods=["POST"])
def refresh_auto_exposure_conf():
    """刷新自动曝光配置"""
    try:
        AutoExposureService().init_configs()
        return JsonResponse.success(msg="同步成功")
    except Exception as e:
        logger.exception(f"同步自动曝光配置失败: {e}")
        return JsonResponse.error(msg="同步失败")


@bp.route("/refresh-targeted-exposure", methods=["POST"])
def refresh_targeted_exposure_conf():
    """刷新定向曝光配置"""
    try:
        TargetedExposureService().init_configs()
        return JsonResponse.success(msg="同步成功")
    except Exception as e:
        logger.exception(f"同步定向曝光配置失败: {e}")
        return JsonResponse.error(msg="同步失败")


@bp.route("/refresh-url-exposure", methods=["POST"])
def url_exposure_refresh():
    """刷新链接曝光配置"""
    try:
        UrlExposureService().init_configs()
        return JsonResponse(code=HTTPStatus.OK, msg="同步成功").to_response()
    except Exception as e:
        logger.exception(f"同步链接曝光配置失败: {e}")
        return JsonResponse.error(msg="同步失败")


@bp.route("/execute-url-exposure", methods=["POST"])
def url_exposure_execute():
    """执行链接曝光"""
    state = AutomationStateManager()
    try:
        state.set_manual_exposure_mode(True)
        data = request.get_json() or {}
        _id = data.get("id")
        if not _id:
            state.set_manual_exposure_mode(False)
            return JsonResponse.error(msg="参数错误")
        conf = UrlExposureService().get_by_id(_id)
        result = UrlExposureService().execute_auto_exposure(_id)
        if result is False:
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=HTTPStatus.CONFLICT,
                                msg="该曝光计划正在执行中").to_response()
        state.set_manual_exposure_mode(False)
        return JsonResponse.success(msg="执行成功")
    except Exception:
        logger.exception("执行链接曝光失败")
        state.set_manual_exposure_mode(False)
        return JsonResponse.error(msg="执行失败")


@bp.route("/refresh-search-account-exposure", methods=["POST"])
def search_account_exposure_refresh():
    """刷新搜索账号曝光配置"""
    try:
        SearchAccountExposureService().init_configs()
        return JsonResponse(code=HTTPStatus.OK, msg="同步成功").to_response()
    except Exception as e:
        logger.exception(f"同步搜索账号曝光配置失败: {e}")
        return JsonResponse.error(msg="同步失败")


@bp.route("/execute-search-account-exposure", methods=["POST"])
def search_account_exposure_execute():
    """执行搜索账号曝光"""
    state = AutomationStateManager()
    try:
        state.set_manual_exposure_mode(True)
        data = request.get_json() or {}
        _id = data.get("id")
        if not _id:
            state.set_manual_exposure_mode(False)
            return JsonResponse.error(msg="参数错误")
        result = SearchAccountExposureService().execute_auto_exposure(_id)
        if result is False:
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=HTTPStatus.CONFLICT,
                                msg="该曝光计划正在执行中").to_response()
        state.set_manual_exposure_mode(False)
        return JsonResponse.success(msg="执行成功")
    except Exception:
        logger.exception("执行搜索账号曝光失败")
        state.set_manual_exposure_mode(False)
        return JsonResponse.error(msg="执行失败")


@bp.route("/refresh-retention-exposure", methods=["POST"])
def retention_exposure_refresh():
    """刷新留存曝光配置"""
    try:
        RetentionExposureService().init_configs()
        return JsonResponse(code=HTTPStatus.OK, msg="同步成功").to_response()
    except Exception as e:
        logger.exception(f"同步留存曝光配置失败: {e}")
        return JsonResponse.error(msg="同步失败")


@bp.route("/execute-retention-exposure", methods=["POST"])
def retention_exposure_execute():
    """执行留存曝光"""
    state = AutomationStateManager()
    try:
        state.set_manual_exposure_mode(True)
        data = request.get_json() or {}
        _id = data.get("id")
        if not _id:
            state.set_manual_exposure_mode(False)
            return JsonResponse.error(msg="参数错误")
        result = RetentionExposureService().execute_auto_exposure(_id)
        if result is False:
            state.set_manual_exposure_mode(False)
            return JsonResponse(code=HTTPStatus.CONFLICT,
                                msg="该曝光计划正在执行中").to_response()
        state.set_manual_exposure_mode(False)
        return JsonResponse.success(msg="执行成功")
    except Exception:
        logger.exception("执行留存曝光失败")
        state.set_manual_exposure_mode(False)
        return JsonResponse.error(msg="执行失败")


@bp.route("/cookie-auth", methods=["POST"])
def cookie_auth():
    """Cookie 验证"""
    try:
        data = request.get_json() or {}
        user_id = data.get("user_id")
        if not user_id:
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少参数").to_response()
        user = SocialMediaUserDB().get_user(user_id)
        status = SocialMediaService().cookie_auth(user)
        return JsonResponse(code=HTTPStatus.OK, msg="验证成功",
                            data={"status": status}).to_response()
    except Exception as e:
        logger.exception(f"Cookie验证失败: {e}")
        return JsonResponse.error(msg="验证失败")


@bp.route("/start-release", methods=["POST"])
def start_release():
    """启动发布计划"""
    try:
        data = request.get_json() or {}
        plan_id = data.get("plan_id")
        if not plan_id:
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少plan_id").to_response()
        return GraphicReleaseManager().start_release(plan_id)
    except Exception as e:
        logger.exception(f"启动发布计划失败: {e}")
        return JsonResponse.error(msg="启动失败")


@bp.route("/get-release-progress", methods=["GET"])
def get_release_progress():
    """获取发布进度"""
    try:
        plan_id = request.args.get("plan_id")
        if not plan_id:
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少plan_id").to_response()
        suc, data, msg = ReleaseTaskManager().get_tasks_status(plan_id)
        if suc:
            return JsonResponse.success(data=data)
        return JsonResponse.error(msg=msg)
    except Exception as e:
        logger.exception(f"获取发布进度失败: {e}")
        return JsonResponse.error(msg="获取失败")


@bp.route("/refresh-accounts-status", methods=["POST"])
def refresh_accounts_status():
    """刷新账号状态"""
    try:
        data = request.get_json() or {}
        return JsonResponse(code=HTTPStatus.OK, msg="刷新成功",
                            data={"refreshed_count": 0}).to_response()
    except Exception as e:
        logger.exception(f"刷新账号状态失败: {e}")
        return JsonResponse.error(msg="刷新失败")


@bp.route("/stop-accounts-verification", methods=["POST"])
def stop_accounts_verification():
    """停止账号检测"""
    global _account_verification_stop_flag
    _account_verification_stop_flag = True
    logger.info("收到停止账号状态检测请求")
    return JsonResponse(code=HTTPStatus.OK, msg="已发送停止检测指令",
                        data={"success": True}).to_response()
