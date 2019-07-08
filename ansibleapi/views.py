from django.http.response import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def api_return_error(request, api):
    response = {}
    response["response_code"] = 404
    response["response_message"] = "url " + api + " with method " + request.method + " not found"
    response["response_data"] = None
    return(HttpResponse(json.dumps(response),content_type='application/json'))