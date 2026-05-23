"""养号控制器"""
from http import HTTPStatus

from flask import Blueprint, request
from loguru import logger

from common.json_response import JsonResponse

bp = Blueprint("cultivation_account", __name__)


@bp.route("/list-plans", methods=["GET"])
def list_cultivation_account_plans():
    try:
        data = {"plans": []}
        return JsonResponse(code=HTTPStatus.OK, msg="获取养号规则列表成功", data=data).to_response()
    except Exception as e:
        logger.exception(f"获取养号规则列表失败: {e}")
        return JsonResponse.error()


@bp.route("/save-plan", methods=["POST"])
def save_cultivation_account_plan():
    try:
        return JsonResponse(code=HTTPStatus.OK, msg="保存成功").to_response()
    except Exception as e:
        logger.exception(f"保存养号规则失败: {e}")
        return JsonResponse.error()


@bp.route("/detail", methods=["POST"])
def detail_cultivation_account_plan():
    try:
        return JsonResponse(code=HTTPStatus.OK, msg="获取详情成功").to_response()
    except Exception as e:
        logger.exception(f"获取养号规则详情失败: {e}")
        return JsonResponse.error()


@bp.route("/logs", methods=["POST"])
def logs_cultivation_account_plan():
    try:
        return JsonResponse(code=HTTPStatus.OK, msg="获取日志成功").to_response()
    except Exception as e:
        logger.exception(f"获取养号动作日志失败: {e}")
        return JsonResponse.error()


@bp.route("/delete-plan", methods=["POST"])
def delete_cultivation_account_plan():
    try:
        return JsonResponse(code=HTTPStatus.OK, msg="删除成功").to_response()
    except Exception as e:
        logger.exception(f"删除养号规则失败: {e}")
        return JsonResponse.error()


@bp.route("/start-plan", methods=["POST"])
def start_cultivation_account_plan():
    try:
        return JsonResponse(code=HTTPStatus.OK, msg="启动成功").to_response()
    except Exception as e:
        logger.exception(f"启动养号规则失败: {e}")
        return JsonResponse.error()
