import json
import logging
from django.utils import timezone
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Play
from ansible.executor.task_queue_manager import TaskQueueManager

from ansibleapi.ansibleutils.inventorymanager import AnsibleInventoryManager
from ansibleapi.ansibleutils.options import AnsibleOptions
from ansibleapi.ansibleutils.resultscallback import AnsibleResultsCallback
from ansibleapi.ansibleutils.variablemanager import AnsibleVariableManager
from ansibleapi.utils import task, BaseTask, DummyHistory, tmp_file
from ansibleapi.worker import app
from shutil import copyfile
import os

@task(app, ignore_result=True, bind=True)
class ExecuteAnsibleModuleAPI(BaseTask):

    """
        :param extra: {
            "project": Project(),

            "data":
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
            "history": History(),
        }
    """
    status_codes = {
        4: "OFFLINE",
        -9: "INTERRUPTED",
        "other": "ERROR"
    }

    logger = logging.getLogger(__name__)

    def __init__(self, app, **kwargs):
        super(self.__class__, self).__init__(app, **kwargs)
        # super.__init__(app, **kwargs)
        self.data = kwargs['data']
        # logging.debug(self.data)
        self.history = kwargs['history'] if kwargs['history'] else DummyHistory()
        self.project = kwargs['project']
        self.task = kwargs['data']['args']

    def execute(self):
        output = None
        try:
            self.prepare()
            output = self.executer()
            logging.debug("Outout: %s", output)
            self.history.raw_stdout = json.dumps(output)
            self.history.status = "OK"
        except Exception as ex:
            self.history.status = "ERROR"
            self.error_handler(ex)
            raise ex
        finally:
            self.history.stop_time = timezone.now()
            self.history.save()
        return output

    def executer(self):

        loader = DataLoader()

        inventory_tmp = self.data["args"]
        """
        { 
            "192.168.1.1": "ls -las",
            "192.168.1.2": "ifconfig",

        }
        """
        inventories = AnsibleInventoryManager(loader=loader, sources=[inventory_tmp])

        # load variable manager
        # over write với variable
        variable_manager = AnsibleVariableManager(loader=loader, inventory=inventories)

        results_callback = AnsibleResultsCallback()

        private_key_file = None

        options = AnsibleOptions()

        tmp = None
        #load ansible option
        # logging.debug("self.data: %s", self.data)
        for k_option, v_option in self.data.items():
            # logging.debug("options key: %s ", k_option)
            # logging.debug("options value: %s ", v_option)
            if k_option not in ["args", "extend", "module", "private_key"]:
                # add option
                if v_option == "true":
                    v_option = True
                options.__setattr__(k_option, v_option)
            elif k_option == "private_key":
                try:
                    # lấy value của param truyền vào tạo thành file key tmp
                    private_key = ""
                    private_key = str(v_option)
                    tmp = tmp_file()
                    tmp.write(private_key)

                    key_tmp = str(tmp.name) + "copy"
                    copyfile(src=str(tmp.name), dst=key_tmp)

                    if os.path.exists(key_tmp):
                        os.chmod(key_tmp, 0o600)
                    # add private key vào option
                    options.private_key_file = key_tmp

                except Exception as e:
                    raise TaskError(e.message)
                    logger.error(e.message)
        for host, command in dict(self.task).items():

            play_source = dict(
                name="Automation Play Module " + self.data["module"] + " " + str(command),
                hosts=str(host),
                gather_facts='no',
                tasks=[dict(action=dict(module=self.data["module"], args=str(command)))]
            )

            ansible_play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

            # actually run it
            tqm = None
            try:
                tqm = TaskQueueManager(
                    inventory=inventories,
                    variable_manager=variable_manager,
                    loader=loader,
                    options=options,
                    passwords=None,
                    stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
                )
                tqm.run(ansible_play)
            except Exception as e:
                raise e
            finally:
                if tqm is not None:
                    tqm.cleanup()

        # xóa file tmp
        if os.path.exists(key_tmp):
            os.remove(key_tmp)

        logging.debug("results_callback: %s", results_callback.return_data)

        return results_callback.return_data

    def prepare(self):
        self.history.status = "RUN"
        self.history.save()

    def run(self):
        return self.execute()
        # return 123

    def error_handler(self, exception):
        default_status = self.status_codes["other"]
        self.history.raw_stdout = self.history.raw_stdout + str(exception)
        self.history.status = default_status