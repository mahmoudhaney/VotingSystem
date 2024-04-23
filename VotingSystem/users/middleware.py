import logging

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logging.info(f"Incoming request: {request.method} {request.path}")
        response = self.get_response(request)
        logging.info(f"Outgoing response: {response.status_code}")
        return response