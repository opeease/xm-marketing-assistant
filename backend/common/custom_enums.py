from enum import IntEnum, StrEnum


class WsMsgTypes(StrEnum):
    TaskStep = "task_step"
    AutomationStepStart = "automation_step_start"
    AutomationStepProgress = "automation_step_progress"
    AutomationStepComplete = "automation_step_complete"
    AutomationStepError = "automation_step_error"
    AutomationThought = "automation_thought"
    AutomationDetail = "automation_detail"
    OcrDownProgress = "ocr_down_progress"
    OcrDownCallBack = "ocr_down_callback"
    HotUpdateProgress = "hot_update_progress"


class TaskType(StrEnum):
    IMMEDIATE = "immediate"
    FIXED_TIME = "fixedTime"


class SocialMediaPlatform(StrEnum):
    DOUYIN = "douyin"
    XHS = "xhs"
    XHS_EXPOSURE = "xhs_exposure"
    TENCENT = "tencent"
    KUAISHOU = "kuaishou"
    KUAISHOU_EXPOSURE = "kuaishou_exposure"


class TaskStatus(StrEnum):
    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETED = "Completed"
    ERROR = "Error"
    EXPIRED = "Expired"
    CANCELED = "Canceled"
    PARTIAL = "Partial"


class AutoExposureConfType(IntEnum):
    COMMENT = 1
    PRIVATE_MSG = 2


class ExposureConfType(IntEnum):
    AUTO = 0
    TARGETED = 1
    URL = 2
    SEARCH_ACCOUNT = 3
    RETENTION = 4


class ExposureStopReason(StrEnum):
    ACCOUNT_INVALID = "授权账号已失效"
    ACCOUNT_NOT_FOUND = "未查询到授权账号"
    ACCOUNT_SECOND_VERIFY = "账号需做二次验证"
    VIDEO_LOADING_FAILED = "视频加载失败"
    MAX_DAILY_LIMIT = "超出当天最多曝光次数"
    INVALID_TARGET_ACCOUNT = "未找到目标账号"
    RISK_CONTROL = "账号触发风险控制"
    NOTHING_LEFT_TO_WATCH = "作品已翻完"
    KEYWORDS_HAVE_NO_MORE_VIDEO = "关键词相关作品已翻完"
    UNKNOWN_EXCEPTION = "未知异常"


class MountComponentType(IntEnum):
    POSITION = 1
    FLOATING_MENU = 2
    FLOATING_CONTENT = 3


class WechatMsgStatus(IntEnum):
    PENDING = 0
    PROCESSED = 1
    REPLIED = 2
    SKIPPED = -1


class LocalConfigKey(StrEnum):
    WX_ID = "wxid"
    SYNC_CONTACT_TASK_ID = "sync_contact_task_id"
    LAST_INTERRUPT_CONTACT = "last_interrupt_contact"
    LAST_INTERRUPT_GROUP = "last_interrupt_group"


class AddContactPlanStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
