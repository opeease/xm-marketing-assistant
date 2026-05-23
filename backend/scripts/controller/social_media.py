"""社交平台控制器"""
import json
import os
from http import HTTPStatus

from flask import Blueprint, request
from loguru import logger

from common.json_response import JsonResponse
from scripts.config import app_config
from scripts.db.social_media_users import SocialMediaUserDB
from scripts.http.service import APIService
from scripts.http.task_service import TaskAPIService
from scripts.utils.common import batch_import_contents
from scripts.utils.threading_utils import run_in_isolated_thread
from scripts.ws.ws_manager import WebSocketManager

bp = Blueprint("social_media", __name__)
ws = WebSocketManager()


@bp.route("/platform-feature-config", methods=["GET"])
def platform_feature_config():
    return JsonResponse(code=HTTPStatus.OK, msg="获取成功", data={
        "xhsEnabled": app_config.xhs_enabled,
        "xhsUnavailableTip": app_config.xhs_unavailable_tip,
    }).to_response()


@bp.route("/list-accounts", methods=["GET"])
def list_accounts():
    platform = request.args.get("platform", "")
    users = SocialMediaUserDB().list_users(platform=platform)
    return JsonResponse.success(data=users)


@bp.route("/delete-social-media", methods=["POST"])
def delete_social_media():
    try:
        data = request.get_json()
        user_id = data.get("id")
        if not user_id:
            return JsonResponse(code=HTTPStatus.BAD_REQUEST, msg="缺少必要参数: id",
                                data={"success": False}).to_response()
        exist_user = SocialMediaUserDB().get_user(user_id)
        if not exist_user:
            return JsonResponse.error(msg="账号不存在")
        success = SocialMediaUserDB().delete_user(user_id)
        APIService().remove_exposure_conf_by_account({
            "account": exist_user["uid"],
            "accountId": exist_user["id"],
        })
        return JsonResponse(code=HTTPStatus.OK if success else HTTPStatus.NOT_FOUND,
                            msg="删除成功" if success else "删除失败：未找到指定账号",
                            data={"success": success}).to_response()
    except Exception:
        logger.exception("删除失败")
        return JsonResponse.error(msg="删除失败")


@bp.route("/batch-import-urls", methods=["POST"])
def batch_import_urls():
    try:
        data = request.get_json()
        file_path = data.get("file_path", "")
        if not file_path or not os.path.exists(file_path):
            return JsonResponse.error(msg="文件不存在")
        if not file_path.endswith((".txt", ".xlsx")):
            return JsonResponse.error(msg="仅支持 .txt 和 .xlsx")
        data_list = batch_import_contents(file_path, header_name="链接", is_tiktok_link=True)
        if not data_list:
            return JsonResponse.error(msg="未找到有效链接")
        return JsonResponse.success(msg="批量导入成功", data={"data": data_list, "success": True})
    except ValueError as e:
        logger.error(f"Excel文件处理错误: {e}")
        return JsonResponse.error(msg="处理错误")
    except KeyError:
        logger.error(f"Excel文件中缺少链接列")
        return JsonResponse.error(msg="缺少链接列")
    except Exception:
        logger.exception("处理文件失败")
        return JsonResponse.error(msg="处理文件失败")
