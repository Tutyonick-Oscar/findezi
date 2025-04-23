import threading
import traceback
from re import sub

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

local = threading.local()


def get_user(request):

    header_token = request.META.get("HTTP_AUTHORIZATION", None)
    if header_token is not None:
        try:
            token_key = sub("Bearer ", "", header_token)
            token_decoded = AccessToken(token=token_key).payload
            user = get_user_model().objects.get(id=token_decoded.get("user_id", None))
            request.user = user
        except Exception as e:
            print("Exception while getting the connected user :", e)


class AuthUserMiddleware:
    """setting user to request
    this class is used to associate the user to the incoming request
    so that we can easely get the current user in all application parts by calling the CURRENT_USER
    attribute of local object (threading).
    a usefull exemple of this is in the apps.core.model.BaseModel class
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        get_user(request)
        local.CURRENT_USER = request.user

        response = self.get_response(request)

        return response


class ExceptionHandlerMiddleware:
    """uncaught exceptions handler
    this class is used to handle all uncaught exceptions, severaly exceptions of type 500
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwds):

        response = self.get_response(request)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        try:
            response.render()
        except Exception:
            ...

        return response

    def process_exception(self, request, exception):

        error_message = str(exception)

        print(
            "==================================== Exception =========================================="
        )
        print(error_message)
        print(traceback.format_exc())
        print(
            "==================================== End Exception ========================================"
        )
        response = Response(
            {
                "success": False,
                "response_code": 500,
                "response_data": None,
                "response_message": f"ERROR : {error_message}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response
