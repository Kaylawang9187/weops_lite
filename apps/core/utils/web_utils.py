from django.http import JsonResponse
from rest_framework import status


class WebUtils:
    @staticmethod
    def response_success(response_data={}):
        return JsonResponse({
            'data': response_data,
            'result': True,
            'messages': ''
        }, status=status.HTTP_200_OK)

    @staticmethod
    def response_error(response_data={}, error_message='', status=status.HTTP_400_BAD_REQUEST):
        return JsonResponse({
            'data': response_data,
            'result': False,
            'messages': error_message
        }, status=status)
