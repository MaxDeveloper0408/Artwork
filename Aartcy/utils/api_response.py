class APIResponse:
    @staticmethod
    def error(message, code):
        return {'status': 'error', 'message': message, 'code': code}

    @staticmethod
    def success(data):
        return {'status': 'success', 'data': data}
