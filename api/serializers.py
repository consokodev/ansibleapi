import logging

from django.conf import settings
from rest_framework import serializers
from api import models
from api.exceptions import DoesNotExist
from api.models import Projects, History
import re


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Projects

        fields = ('id', 'project_id', 'project_name')
        read_only_fields = ['id']


class ProjectExecuteCommandSerializer(serializers.Serializer):
    logger = logging.getLogger(__name__)
    args = serializers.DictField()
    become = serializers.CharField()
    become_method = serializers.CharField()
    become_user = serializers.CharField()
    extend = serializers.CharField()
    module = serializers.CharField()
    private_key = serializers.CharField()
    remote_user = serializers.CharField()

    def check_module_allow(self):
        if(self.data["module"] not in settings.MODULE):
            return False
        return True

    def execute_module_api(self, request, project):
        """
        :param request:
        data post =
        {
            "args": { "192.168.1.1": "ls -las" },
            "become": "true",
            "become_method": "sudo",
            "become_user": "user00",
            "extend": "value",
            "module": "shell",
            "private_key": "ddddd",
            "remote_user": "uppatch"
        }
        project: Projects()
        :return:
        history_id
        """

        data = request.data
        project = project

        if(isinstance(project,Projects)):
            extra = {
                "project": project,
                "data": data,
                "sync": False,
            }
            logging.debug("extra: %s", extra)
            history_id = project.execute_api(**extra)
            return history_id
        else:
            return DoesNotExist(project)


class HistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ("id",
                  "project",
                  "module",
                  "kind",
                  "status",
                  "start_time",
                  "stop_time",
                  "json_args"
                  )

    def get_raw(self, request):
        params = request.query_params
        color = params.get("color", "no")
        if(color=="yes"):
            return self.instance.raw_stdout
        else:
            ansi_escape = re.compile(r'\x1b[^m]*m')
            return ansi_escape.sub('', self.instance.raw_stdout)

    def get_raw_stdout(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri("raw/")
