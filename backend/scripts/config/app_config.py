import os
import threading

from scripts.utils.file import get_documents_path

project_name = "dt-ai-helper"

# 服务器地址
es_host = "sls.dockingtech.com"
es_port = 443
api_location_host = "192.168.0.46"
api_location_port = 8026
api_task_location_host = "192.168.0.46"
api_task_location_port = 7070
api_production_url = "https://client.rpa.dockingtech.com"
api_task_production_url = "https://agent.dockingtech.com"
oss_base_url = "https://cldrpa-oss.oss-cn-chengdu.aliyuncs.com"
dbkey_resources_url = f"{oss_base_url}/resources/dbkey"

# 状态
init_open = False
can_use_ocr = True
wechat_version = ""
send_ws_status = True
xhs_enabled = False
xhs_unavailable_tip = "小红书平台升级中，暂不可用"

# 路径
root_path = get_documents_path()
cache_path = os.path.join(root_path, f"{project_name}/cache")
main_log_context = threading.local()

# 自动化
automation_time_window_poll_interval_seconds = 1

# 版本
hot_fix_version = "1.0.2"
