"""Boss 控制器"""
from functools import wraps
from http import HTTPStatus

from flask import Blueprint, request, g
from loguru import logger

from common.ApiEndpoint import BossAPI
from common.json_response import JsonResponse
from scripts.service.boss_service.BossService import BossService
from scripts.utils.common import get_local_config

bp = Blueprint("boss", __name__, url_prefix="/boss")


@bp.before_request
def boss_interceptor():
    try:
        g.token = request.headers.get("Authorization", "")
    except Exception:
        pass


@bp.route("/test", methods=["GET"])
def test():
    try:
        return JsonResponse(code=HTTPStatus.OK, msg="Boss接口测试成功",
                            data={"token": g.token}).to_response()
    except Exception as e:
        logger.error(f"测试接口异常: {e}")
        return JsonResponse.error()


@bp.route("/open-tiktok-auth", methods=["POST"])
def open_tiktok_auth():
    result = BossService().open_tiktok_auth()
    if result.get("success"):
        return JsonResponse(code=HTTPStatus.OK, msg="获取成功",
                            data=result.get("data")).to_response()
    return JsonResponse(code=HTTPStatus.BAD_REQUEST,
                        msg=result.get("message", "获取失败")).to_response()


@bp.route("/preparation-check", methods=["GET"])
def preparation_check():
    data = BossService().preparation_check()
    return JsonResponse(code=HTTPStatus.OK, msg="Boss接口预检成功",
                        data=data.to_json()).to_response()


@bp.route("/contacts-tags", methods=["GET"])
def get_contacts_tags():
    try:
        data = BossService().get_contacts_tags()
        return JsonResponse(code=HTTPStatus.OK, msg="获取标签列表成功", data=data).to_response()
    except Exception as e:
        logger.error(f"获取标签列表异常: {e}")
        return JsonResponse.error()


@bp.route("/contacts-query-summary", methods=["POST"])
def query_contacts_summary():
    try:
        request_data = request.get_json() or {}
        data = BossService().get_contacts_query_summary(
            tag_ids=request_data.get("tagIds"),
            remark_keyword=request_data.get("remarkKeyword"),
            contact_type=request_data.get("contactType"),
            sample_size=request_data.get("sampleSize", 5),
        )
        return JsonResponse(code=HTTPStatus.OK, msg="查询联系人摘要成功", data=data).to_response()
    except Exception as e:
        logger.error(f"查询联系人摘要异常: {e}")
        return JsonResponse.error()


@bp.route("/get-agent-access-token", methods=["GET"])
def get_agent_access_token():
    try:
        result = get_local_config().__getattribute__  # placeholder
        data = {}
        data["userId"] = get_local_config("user_id")
        return JsonResponse(code=HTTPStatus.OK, msg="获取成功", data=data).to_response()
    except Exception as e:
        logger.error(f"获取Agent Token异常: {e}")
        return JsonResponse.error()
