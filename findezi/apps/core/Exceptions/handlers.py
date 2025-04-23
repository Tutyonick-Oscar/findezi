from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler


def common_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(exc, ValidationError):
            details = exc.get_full_details()

        response.data["success"] = False
        response.data["response_code"] = response.status_code
        response.data["response_data"] = None
        try:
            response.data["response_message"] = response.data["detail"]
        except Exception:
            if isinstance(exc, ValidationError):
                response.data["response_message"] = details
                [response.data.pop(error, None) for error in details]
            else:
                response.data["response_message"] = str(exc.detail)

        # then we pop unusable fields
        response.data.pop("detail", None)
        response.data.pop("non_field_errors", None)

    return response
