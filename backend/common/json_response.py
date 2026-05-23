from flask import jsonify, make_response


class JsonResponse:
    """统一 JSON 响应格式"""

    def __init__(self, code: int = 200, data=None, msg: str = "success"):
        self.code = code
        self.data = data
        self.msg = msg

    @classmethod
    def success(cls, data=None, msg: str = "success"):
        return cls(200, data, msg).to_response()

    @classmethod
    def error(cls, msg: str = "error", data=None):
        return cls(500, data, msg).to_response()

    def to_dict(self):
        return {"code": self.code, "msg": self.msg, "data": self.data}

    def to_response(self):
        response = make_response(jsonify(self.to_dict()))
        response.headers["Content-Type"] = "application/json"
        return response
