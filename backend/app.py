#!/usr/bin/env python
"""
XM全能营销助手 - Flask 后端入口
=================================
完整还原从反编译得到的 Python 后端架构

启动:
  python app.py --port 8766

API 文档:
  base:           /base/*           系统信息/环境检查
  wechat:         /wechat/*         微信自动化
  social_media:   /social_media/*   社交平台管理
  boss:           /boss/*           业务平台
  cultivation:    /cultivation_account/*  养号
"""
import argparse
import os
import sys
import threading

from flask import Flask, render_template_string
from loguru import logger

# 将 backend 目录加入 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common.json_response import JsonResponse
from scripts.controller.base import bp as base_bp
from scripts.controller.wechat import bp as wechat_bp
from scripts.controller.social_media import bp as social_media_bp
from scripts.controller.boss import bp as boss_bp
from scripts.controller.cultivation_account import bp as cultivation_bp
from scripts.config import app_config


def create_app() -> Flask:
    """创建 Flask 应用"""
    app = Flask(__name__)

    # 注册 Blueprints
    app.register_blueprint(base_bp)
    app.register_blueprint(wechat_bp, url_prefix="/wechat")
    app.register_blueprint(social_media_bp, url_prefix="/social_media")
    app.register_blueprint(boss_bp)  # 自带 /boss 前缀
    app.register_blueprint(cultivation_bp)

    # 根路径
    @app.route("/")
    def index():
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>XM全能营销助手 - 后端服务</title>
        <style>body{font-family:sans-serif;margin:40px;line-height:1.6}
        .endpoint{background:#f5f5f5;padding:8px 12px;margin:4px 0;border-radius:4px}
        code{background:#eee;padding:2px 6px;border-radius:3px}</style>
        </head>
        <body>
        <h1>XM全能营销助手 - 后端服务</h1>
        <p>基于反编译源码还原的 Flask API 服务器</p>
        <h2>API 端点</h2>
        <h3>基础</h3>
        <div class="endpoint"><code>GET  /base/check-env</code> 检查环境</div>
        <div class="endpoint"><code>GET  /base/get-performance-metrics</code> CPU/内存</div>
        <div class="endpoint"><code>GET  /base/get-websocket-port</code> WS端口</div>
        <h3>微信</h3>
        <div class="endpoint"><code>GET  /wechat/is-wx-login</code> 检查登录</div>
        <div class="endpoint"><code>POST /wechat/open-wx-controller</code> 启动自动化</div>
        <div class="endpoint"><code>GET  /wechat/get-wx-contacts</code> 联系人列表</div>
        <div class="endpoint"><code>POST /wechat/sync-database</code> 同步数据库</div>
        <div class="endpoint"><code>POST /wechat/batch-add-contact</code> 批量导入</div>
        <h3>社交平台</h3>
        <div class="endpoint"><code>GET  /social_media/list-accounts</code> 账号列表</div>
        <div class="endpoint"><code>POST /social_media/batch-import-urls</code> 批量导入URL</div>
        <h3>Boss平台</h3>
        <div class="endpoint"><code>GET  /boss/open-tiktok-auth</code> 抖音授权</div>
        <div class="endpoint"><code>GET  /boss/preparation-check</code> 预检</div>
        </body>
        </html>
        """)

    # 全局异常处理 - 开发模式下打印堆栈
    if not app.debug:
        @app.errorhandler(Exception)
        def handle_exception(e):
            logger.exception(f"全局异常: {e}")
            return JsonResponse(code=500, msg=f"服务器内部异常: {str(e)}").to_response()

    return app


def setup_logging(level: str = "INFO"):
    """配置日志"""
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:7}</level> | {message}",
        level=level,
    )
    logger.add("logs/backend.log", rotation="10 MB", retention=5, level="DEBUG")


def main():
    parser = argparse.ArgumentParser(description="XM全能营销助手 - 后端服务")
    parser.add_argument("--port", type=int, default=8766, help="监听端口")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--debug", action="store_true", help="调试模式")
    parser.add_argument("--log-level", default="INFO", help="日志级别")
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger.info("=" * 50)
    logger.info("XM全能营销助手 - 后端服务启动")
    logger.info(f"监听地址: {args.host}:{args.port}")
    logger.info(f"调试模式: {args.debug}")
    logger.info("=" * 50)

    # 检查微信状态
    from scripts.wechat_uia import is_login
    wx_login = is_login()
    logger.info(f"微信登录状态: {wx_login}")
    app_config.can_use_ocr = True

    # 启动 Flask
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
