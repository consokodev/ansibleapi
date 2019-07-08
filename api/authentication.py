# -*- coding: utf-8 -*-
import base64

from django.middleware.csrf import CsrfViewMiddleware
from django.utils.six import text_type
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from rest_framework import HTTP_HEADER_ENCODING, exceptions
from api import models
from api import response_status
from api.base import ResponseAPI
import collections
import hashlib


def get_authorization_header(request):
    """
    Return request's 'Authorization:' header, as a bytestring.
    Hide some test client ickyness where the header can be unicode.
    """
    auth = request.META.get('HTTP_AUTHORIZATION')
    return auth


def generator_signature(sign_str):
    sign = hashlib.md5()
    sign.update(sign_str.lower())
    return base64.b64encode((sign.hexdigest().encode('utf-8')))


# AuthenSignature decoter
def authen_signature(*listparam):
    """
    listparam = pk, data, project_id

    + Authen theo secret_key chi theo project_id chỉ đối với api execommand

    + Đối với các API khác thì sử dụng secret_key chung

    sẽ check các param trong list truyền lên, đồng thời gen sign và compare với param hiện tại


    :param arg: [a,f,s,f,sd]
    :return:
    """

    def varlidate(func):
        def wrapper(self, request, *args, **kwargs):

            # check header authen sign
            if get_authorization_header(request) == "":
                return ResponseAPI(
                    response_code=response_status.PERMISSION_DENY.code,
                    response_message=response_status.PERMISSION_DENY.message + " Sign không tồn tại",
                    response_data=None).resp

            sign_data = get_authorization_header(request).split(' ')

            if sign_data[0] != "Sign":
                return ResponseAPI(
                    response_code=response_status.INVALID_SIGNATURE.code,
                    response_message=response_status.INVALID_SIGNATURE.message + " Không truyền Sign trên header",
                    response_data=None).resp

            sign_str = ""
            str_body = ""

            # chi check data in get param
            if "execute_command" not in listparam:

                # có truyền data lên
                if request.method not in ["GET", "DELETE"]:

                    if isinstance(request.data, dict):
                        sort = collections.OrderedDict(sorted(request.data.items()))
                        str_body = "".join([str(va) for va in sort.values()])
                    else:
                        # data truyen len khong phai dang dis
                        return ResponseAPI(
                            response_code=response_status.INVALID_DATA.code,
                            response_message=response_status.INVALID_DATA.message,
                            response_data=None).resp

            # check data in get param vào body
            else:

                # có truyền data lên
                if request.method not in ["GET", "DELETE"]:

                    if isinstance(request.data, dict):
                        sort = collections.OrderedDict(sorted(request.data.items()))
                        str_body = str_body + "".join([str(va) for va in sort.values()])

                    else:
                        # data truyen len khong phai dang dis
                        return ResponseAPI(
                            response_code=response_status.INVALID_DATA.code,
                            response_message=response_status.INVALID_DATA.message,
                            response_data=None).resp

                if kwargs["pk"] != "":

                    # lấy secret ky cua product
                    try:
                        project = models.Projects.objects.get(pk=kwargs["pk"])
                        str_body = str_body + str(project.secret_key)
                    except Exception as e:
                        return ResponseAPI(
                            response_code=response_status.NOT_FOUND.code,
                            response_message=response_status.NOT_FOUND.message,
                            response_data=None).resp

            sign_str = (str_body + settings.SECRET_KEY).encode('utf-8')

            if generator_signature(sign_str).decode('utf-8') != sign_data[1]:
                return ResponseAPI(
                    response_code=response_status.INVALID_SIGNATURE.code,
                    response_message=response_status.INVALID_SIGNATURE.message + " Sai Sign rồi má",
                    response_data=None).resp
            return func(self, request, *args, **kwargs)

        return wrapper

    return varlidate