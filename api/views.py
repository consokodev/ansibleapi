# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from api import models, response_status
from api.serializers import ProjectSerializer, ProjectExecuteCommandSerializer, HistorySerializer
from api.base import ResponseAPI
from api.exceptions import DoesNotExist,ServerError
from api.authentication import authen_signature

class ProjectViewSet(APIView):
    logger = logging.getLogger(__name__)

    @authen_signature()
    def get(self, request):
        projects = None
        try:
            projects = models.Projects.objects.all()
        except Exception as e:
            raise ServerError(e.message)

        response_data = [ProjectSerializer(prj).data for prj in projects]
        logging.debug("Project response_data: %s", response_data)

        return ResponseAPI(response_code=response_status.SUCCESS.code,
                           response_message=response_status.SUCCESS.message,
                           response_data=response_data).resp

    def post(self, request):
        """

        :param (
                  'id_project',
                  'name_project',
                  'security_key'
                  )
        :return:
        """

        serializer = ProjectSerializer(data=request.data)
        if(serializer.is_valid()):
            if(models.Projects.objects.filter(project_id=request.data["project_id"])):
                return ResponseAPI(
                    response_code=response_status.INVALID_DATA.code,
                    response_message=response_status.INVALID_DATA.message + " project_id " + str(request.data["project_id"]),
                    response_data=None
                ).resp

            if(models.Projects.objects.filter(project_name=request.data["project_name"])):
                return ResponseAPI(
                    response_code=response_status.INVALID_DATA.code,
                    response_message=response_status.INVALID_DATA.message + " project_name " + str(request.data["project_name"]),
                    response_data=None
                ).resp

            serializer.save()
            logging.debug("Save new project success: %s", serializer.data)
            return ResponseAPI(
                response_code=response_status.SUCCESS.code,
                response_message=response_status.SUCCESS.message,
                response_data=serializer.data
            ).resp
        logging.debug("Save new project error: %s", str(serializer.errors))

        return ResponseAPI(
            response_code=response_status.INVALID_PARAM.code,
            response_message=response_status.INVALID_DATA.message,
            response_data=None
        ).resp

class ProjectExecuteCommandSet(APIView):
    logger = logging.getLogger(__name__)

    def get_object(self, pk):
        try:
            return models.Projects.objects.get(pk=pk)
        except Exception as e:
            return None

    def post(self, request, pk):

        project = self.get_object(pk)

        if(project is None):
            return ResponseAPI(
                response_code=response_status.INVALID_DATA.code,
                response_message=response_status.INVALID_DATA.message + " project_id " + pk,
                response_data=None
            ).resp

        serializer = ProjectExecuteCommandSerializer(data=request.data)

        if(serializer.is_valid()):
            if(serializer.check_module_allow()):
                rdata = serializer.execute_module_api(request, project)
                logging.debug(str({"history_id" : rdata, "detail" : "Started project " + str(project.pk)}))

                return ResponseAPI(
                    response_code=response_status.SUCCESS.code,
                    response_message=response_status.SUCCESS.message,
                    response_data={"history_id": rdata, "detail": "Started at project " + str(project.pk)}
                ).resp
            else:
                return ResponseAPI(
                    response_code=response_status.MODULE_NOT_ALLOW.code,
                    response_message=response_status.MODULE_NOT_ALLOW.message,
                    response_data=None
                ).resp
        logging.debug(response_status.INVALID_PARAM.message + " " + str(request.data))

        return ResponseAPI(
            response_code=response_status.INVALID_PARAM.code,
            response_message=response_status.INVALID_PARAM.message,
            response_data=None
        ).resp

class HistoryViewRawSet(APIView):

    def get_object(self, pk):
        try:
            return models.History.objects.get(pk=pk)
        except Exception as e:
            raise DoesNotExist(e.message)

    def get(self, request, pk):
        history = self.get_object(pk)
        result = HistorySerializer(history).get_raw(request)

        return ResponseAPI(
            response_code=response_status.SUCCESS.code,
            response_message=response_status.SUCCESS.message,
            response_data=result
        ).resp

class HistoryViewSet(APIView):

    def get_object(self, pk):
        try:
            return models.History.objects.get(pk=pk)
        except Exception as e:
            raise DoesNotExist(e.message)

    def get(self, request, pk):
        history = self.get_object(pk=pk)
        serializer = HistorySerializer(history)

        return ResponseAPI(
            response_code=response_status.SUCCESS.code,
            response_message=response_status.SUCCESS.message,
            response_data=serializer.data
        ).resp