#!/usr/bin/env python
"""
XM全能营销助手
=============
微信 AI 营销工具 - UIA 操控 + AI 自动回复 + 群发 + 加好友 + 新好友处理

用法:
  python main.py                          # 交互菜单
  python main.py auto-reply               # 启动自动回复(持续)
  python main.py auto-reply --once        # 执行一次自动回复
  python main.py monitor                  # 仅监控未读(不回复)
  python main.py send --to 张三,李四 --msg "你好"  # 群发消息
  python main.py mass-send --file plan.json       # 从文件群发
  python main.py add-friends --contacts 138xxx,139xxx  # 加好友
  python main.py accept                    # 通过新好友申请
  python main.py contacts                 # 列出联系人
  python main.py convs                    # 列出会话
  python main.py experts                  # 列出AI专家
"""
import sys
import argparse

from loguru import logger

# 配置日志
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level:7}</level> | {message}",
    level="INFO",
)
logger.add("logs/xm-assistant.log", rotation="10 MB", retention=5, level="DEBUG")


def cmd_auto_reply(args):
    """自动回复"""
    from src.auto_reply import create_engine

    expert_ids = [int(x) for x in args.experts.split(",")] if args.experts else None
    engine = create_engine(base_url=args.api, expert_ids=expert_ids)

    if args.once:
        result = engine.run_once()
        print(f"\n完成: 检查{result['checked']} 回复{result['replied']} 服务{result['served']}")
        for d in result.get("details", []):
            print(f"  [{d['expert']}] {d['contact']}: {d['reply'][:60]}")
    else:
        engine.run_loop(interval=args.interval)


def cmd_monitor(args):
    """监控未读消息"""
    from src.wechat_uia import get_unread, list_conversations, is_login

    if not is_login():
        print("微信未登录或未找到窗口")
        return

    if args.all:
        convs = list_conversations()
        print(f"\n全部会话 ({len(convs)} 个):")
        for c in convs:
            marker = "🔴" if c["unread"] > 0 else "  "
            print(f"  {marker} {c['name']} (未读:{c['unread']})")
    else:
        unread = get_unread()
        print(f"\n未读会话 ({len(unread)} 个):")
        for c in unread:
            print(f"  {c['name']} ({c['unread']}条)")


def cmd_send(args):
    """群发消息"""
    from src.wechat_uia import send_to_many, is_login

    if not is_login():
        print("微信未登录")
        return

    targets = [t.strip() for t in args.to.split(",")]
    print(f"群发目标: {targets}")
    print(f"消息内容: {args.msg}")

    confirm = input("\n确认发送? (y/N): ")
    if confirm.lower() != "y":
        print("已取消")
        return

    result = send_to_many(targets, args.msg)
    success = sum(1 for v in result.values() if v)
    fail = len(result) - success
    print(f"\n完成: 成功 {success}, 失败 {fail}")


def cmd_contacts(args):
    """列出联系人"""
    from src.wechat_uia import list_contacts, is_login

    if not is_login():
        print("微信未登录")
        return

    contacts = list_contacts()
    print(f"\n联系人 ({len(contacts)} 个):")
    for i, c in enumerate(contacts, 1):
        print(f"  {i}. {c['name']}")


def cmd_convs(args):
    """列出会话"""
    cmd_monitor(argparse.Namespace(all=True))


def cmd_experts(args):
    """列出AI专家"""
    from src.prompt_manager import PromptManager
    from src.ai_client import AIClient

    client = AIClient(base_url=args.api) if args.api else None
    pm = PromptManager(client=client)
    experts = pm.load()

    print(f"\nAI专家 ({len(experts)} 个):")
    for e in experts:
        status = "启用" if e.is_enabled() else "禁用"
        bl = e.blacklist[:40] + "..." if len(e.blacklist) > 40 else e.blacklist
        print(f"  #{e.id} {e.remark} [{status}]")
        print(f"     黑名单: {bl or '(无)'}")
        print(f"     自动备注: {e.auto_notes or '关闭'}")


def cmd_accept(args):
    """通过好友请求"""
    from src.wechat_uia import accept_contacts, new_contact_count, is_login

    if not is_login():
        print("微信未登录")
        return

    count = new_contact_count()
    print(f"待处理好友请求: {count} 个")

    if count == 0:
        return

    accepted = accept_contacts(max_n=args.max)
    print(f"已通过: {accepted} 个")


def cmd_add_friends(args):
    """加好友"""
    from src.wechat_add_friend import add_friends, add_friends_from_file
    from src.wechat_uia import is_login

    if not is_login():
        print("微信未登录")
        return

    if args.file:
        result = add_friends_from_file(args.file)
    elif args.contacts:
        contacts = [c.strip() for c in args.contacts.split(",")]
        result = add_friends(contacts, verify_msg=args.verify, welcome_msg=args.welcome)
    else:
        print("请指定 --contacts 或 --file")
        return

    print(f"\n加好友完成: 成功 {result['added']}, 失败 {result['failed']}")
    for d in result.get("details", []):
        status = "✓" if d.get("status") == "added" else "✗"
        print(f"  {status} {d.get('contact', d.get('name', '?'))}")


def cmd_mass_send(args):
    """群发消息(增强版)"""
    from src.wechat_mass_send import mass_send, mass_send_from_file
    from src.wechat_uia import is_login

    if not is_login():
        print("微信未登录")
        return

    if args.file:
        result = mass_send_from_file(args.file)
    elif args.to:
        contacts = [c.strip() for c in args.to.split(",")]
        result = mass_send(contacts, message=args.msg, label=args.label or "")
    else:
        print("请指定 --to 或 --file")
        return

    print(f"\n群发完成: 成功 {result['sent']}, 失败 {result['failed']} (共{result['total']})")
    for d in result.get("details", []):
        status = "✓" if d.get("status") == "sent" else "✗"
        print(f"  {status} {d['target']}")


def cmd_check_new_contacts(args):
    """检测并通过新好友"""
    from src.wechat_new_contact import check_new_contacts, accept_all
    from src.wechat_uia import is_login

    if not is_login():
        print("微信未登录")
        return

    if args.all:
        result = accept_all(welcome_msg=args.welcome or "", label=args.label or "")
    else:
        result = check_new_contacts(config_file=args.config or "")

    print(f"\n新好友处理: 已处理 {result['processed']}, 通过 {result['accepted']}")


def cmd_interactive(args):
    """交互菜单"""
    while True:
        print("\n" + "=" * 50)
        print("  XM全能营销助手")
        print("=" * 50)
        print("  1. 自动回复 (持续监控)")
        print("  2. 自动回复 (执行一次)")
        print("  3. 查看未读消息")
        print("  4. 查看全部会话")
        print("  5. 查看联系人")
        print("  6. 查看AI专家")
        print("  7. 通过好友请求")
        print("  8. 群发消息")
        print("  9. 加好友(批量)")
        print(" 10. 处理新好友申请")
        print("  0. 退出")
        print("-" * 50)

        choice = input("请选择: ").strip()

        if choice == "1":
            ns = argparse.Namespace(api=args.api, experts=args.experts, once=False, interval=args.interval)
            cmd_auto_reply(ns)
        elif choice == "2":
            ns = argparse.Namespace(api=args.api, experts=args.experts, once=True, interval=15)
            cmd_auto_reply(ns)
        elif choice == "3":
            cmd_monitor(argparse.Namespace(all=False))
        elif choice == "4":
            cmd_monitor(argparse.Namespace(all=True))
        elif choice == "5":
            cmd_contacts(argparse.Namespace())
        elif choice == "6":
            cmd_experts(argparse.Namespace(api=args.api))
        elif choice == "7":
            cmd_accept(argparse.Namespace(max=20))
        elif choice == "8":
            to = input("发送给(逗号分隔): ").strip()
            msg = input("消息内容: ").strip()
            cmd_mass_send(argparse.Namespace(to=to, msg=msg, file=None, label=""))
        elif choice == "9":
            contacts = input("微信号/手机号(逗号分隔): ").strip()
            verify = input("验证消息: ").strip()
            welcome = input("欢迎语: ").strip()
            cmd_add_friends(argparse.Namespace(contacts=contacts, file=None, verify=verify, welcome=welcome))
        elif choice == "10":
            welcome = input("欢迎语(回车跳过): ").strip()
            label = input("备注标签(回车跳过): ").strip()
            cmd_check_new_contacts(argparse.Namespace(all=True, welcome=welcome, label=label, config=""))
        elif choice == "0":
            print("再见!")
            break
        else:
            print("无效选择")


def main():
    parser = argparse.ArgumentParser(description="XM全能营销助手")
    parser.add_argument("--api", default="https://client.rpa.dockingtech.com", help="AI 后端地址")
    parser.add_argument("--experts", default=None, help="指定AI专家ID(逗号分隔)")
    parser.add_argument("--interval", type=int, default=15, help="扫描间隔(秒)")

    sub = parser.add_subparsers(dest="command", help="子命令")

    # auto-reply
    p = sub.add_parser("auto-reply", help="自动回复")
    p.add_argument("--once", action="store_true", help="仅执行一次")
    p.set_defaults(func=lambda a: cmd_auto_reply(a))

    # monitor
    p = sub.add_parser("monitor", help="监控未读")
    p.add_argument("--all", action="store_true", help="显示全部会话")
    p.set_defaults(func=lambda a: cmd_monitor(a))

    # send
    p = sub.add_parser("send", help="群发消息")
    p.add_argument("--to", required=True, help="目标联系人(逗号分隔)")
    p.add_argument("--msg", required=True, help="消息内容")
    p.set_defaults(func=lambda a: cmd_send(a))

    # contacts
    p = sub.add_parser("contacts", help="列出联系人")
    p.set_defaults(func=lambda a: cmd_contacts(a))

    # convs
    p = sub.add_parser("convs", help="列出会话")
    p.set_defaults(func=lambda a: cmd_convs(a))

    # experts
    p = sub.add_parser("experts", help="列出AI专家")
    p.set_defaults(func=lambda a: cmd_experts(a))

    # accept-friends
    p = sub.add_parser("accept-friends", help="通过好友请求")
    p.add_argument("--max", type=int, default=20, help="最大通过数")
    p.set_defaults(func=lambda a: cmd_accept(a))

    # add-friends (批量加好友)
    p = sub.add_parser("add-friends", help="批量加好友")
    p.add_argument("--contacts", default=None, help="微信号/手机号(逗号分隔)")
    p.add_argument("--file", default=None, help="好友计划JSON文件")
    p.add_argument("--verify", default="", help="验证消息")
    p.add_argument("--welcome", default="", help="通过后欢迎语")
    p.set_defaults(func=lambda a: cmd_add_friends(a))

    # mass-send (增强群发)
    p = sub.add_parser("mass-send", help="群发消息(支持文件)")
    p.add_argument("--to", default=None, help="目标联系人(逗号分隔)")
    p.add_argument("--msg", default="", help="消息内容")
    p.add_argument("--file", default=None, help="群发计划JSON文件")
    p.add_argument("--label", default="", help="备注标签")
    p.set_defaults(func=lambda a: cmd_mass_send(a))

    # accept (新好友检测)
    p = sub.add_parser("accept", help="检测并通过新好友申请")
    p.add_argument("--all", action="store_true", help="通过所有申请")
    p.add_argument("--config", default="", help="自动接受配置JSON文件")
    p.add_argument("--welcome", default="", help="欢迎语")
    p.add_argument("--label", default="", help="备注标签")
    p.set_defaults(func=lambda a: cmd_check_new_contacts(a))

    args = parser.parse_args()

    if args.command:
        args.func(args)
    else:
        cmd_interactive(args)


if __name__ == "__main__":
    main()