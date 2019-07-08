# -*- coding: utf-8 -*-
from ansible.inventory.data import InventoryData
from ansible.module_utils._text import to_text
from ansible.module_utils.six import string_types
from ansible.inventory.manager import InventoryManager, display


try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

import os
from shutil import copyfile

from ansible import constants as C
import logging

class AnsibleInventoryManager(InventoryManager):
    ''' Overwrite Creates and manages inventory '''
    logger = logging.getLogger(__name__)

    def __init__(self, loader, sources=None):

        # base objects
        self._loader = loader
        self._inventory = InventoryData()

        # a list of host(names) to contain current inquiries to
        self._restriction = None
        self._subset = None

        # caches
        self._hosts_patterns_cache = {}  # resolved full patterns
        self._pattern_cache = {}  # resolved individual patterns
        self._inventory_plugins = []  # for generating inventory

        self._list_file_tmp = []
        # the inventory dirs, files, script paths or lists of hosts
        if sources is None:
            self._sources = []
        elif isinstance(sources, string_types):
            self._sources = [sources]
        else:
            self._sources = sources

        # get to work!
        self.parse_source(sources)

    def parse_source(self, source, cache=False):
        ''' giữ nguyên và không parse haha '''

        """
        source : [
                    { 
                        "192.168.1.1": "ls -las",
                        "192.168.1.2": "ifconfig" 
                    }
                ]
        """
        if len(source) > 0:
            # lấy list instance inventory input
            for inven in source:

                # không sài khúc này nhưng không xóa để chơi  cho tưởng nhớ bản gốc
                # add group
                # for group in inven.groups_list:
                #     self._inventory.add_group(group.name)
                #
                #     # add var của group
                #     if group.have_vars:
                #         obj_var_group, tmp_name_group = group.get_generated_vars()
                #
                #         if tmp_name_group != None:
                #             # add key tmp vào variable
                #             file_tmp_group = tmp_name_group.name + "copy"
                #             # khổ lắm chỗ này cheat nè , éo có class kế thừa mẹ gì đâu huhu !!
                #             copyfile(src=tmp_name_group.name, dst=file_tmp_group)
                #             self._inventory.set_variable(group.name, "ansible_ssh_private_key_file", file_tmp_group)
                #             self._list_file_tmp.append(file_tmp_group)
                #             # xóa khỏi dict
                #             obj_var_group.pop("ansible_ssh_private_key_file", None)
                #
                #         for k_group_var, v_group_var in obj_var_group.items():
                #             self._inventory.set_variable(group.name, k_group_var, v_group_var)
                #
                #     # add host cho group
                #     if len(group.hosts.all()) > 0:
                #
                #         # add host
                #         for host_ingroup in group.hosts.all():
                #             # add host cho group
                #             self._inventory.add_host(host=host_ingroup.name, group=group.name)
                #
                #             # add var cho host
                #             if host_ingroup.have_vars:
                #                 obj_var_host, tmp_name_host = host_ingroup.get_generated_vars()
                #                 if tmp_name_host != None:
                #                     file_tmp_host = tmp_name_host.name + "copy"
                #                     copyfile(src=tmp_name_host.name, dst=file_tmp_host)
                #                     os.chmod(file_tmp_host, 0600)
                #                     self._inventory.set_variable(host_ingroup.name, "ansible_ssh_private_key_file", file_tmp_host)
                #                     self._list_file_tmp.append(file_tmp_host)
                #                     # xóa khỏi dict
                #                     obj_var_host.pop("ansible_ssh_private_key_file", None)
                #
                #                 for k_host_ingroup_var, v_host_ingroup_var in obj_var_host.items():
                #                     self._inventory.set_variable(host_ingroup.name, k_host_ingroup_var, v_host_ingroup_var)

                # add host in ungroup
                for host in inven.keys():
                    self._inventory.add_host(host=str(host), group="ungrouped")
                    self._inventory.set_variable(str(host), "ansible_ssh_common_args", "-o StrictHostKeyChecking=no")

                    # không có var cho từng host luôn, bê đê mất giá trị ansible
                    # add var cho host ungroup
                    # if host_ungroup.have_vars:
                    #
                    #     obj_var_host_ungroup, tmp_name_host_ungroup = host_ungroup.get_generated_vars()
                    #     if tmp_name_host_ungroup != None:
                    #         file_tmp_host_ungroup = tmp_name_host_ungroup.name + "copy"
                    #         copyfile(src=tmp_name_host_ungroup.name, dst=file_tmp_host_ungroup)
                    #         os.chmod(file_tmp_host_ungroup, 0600)
                    #         self._inventory.set_variable(host_ungroup.name, "ansible_ssh_private_key_file", file_tmp_host_ungroup)
                    #         self._list_file_tmp.append(file_tmp_host_ungroup)
                    #         # xóa khỏi dict
                    #         obj_var_host_ungroup.pop("ansible_ssh_private_key_file", None)
                    #
                    #     for k_host_var, v_host_var in host_ungroup.vars.items():
                    #         self._inventory.set_variable(host_ungroup.name, k_host_var, v_host_var)


                # theo chuẩn của ansible sẻ sử dụng,
                # vcl, nhìn thấy sửa ít chưa sửa nhiều lăm DKM bạc đầu
                # add var default cho inventory
                # if inven.have_vars:
                #     for k_inven_var, v_inven_var in inven.vars.items():
                #         try:
                #             self._inventory.set_variable(inven.name, k_inven_var, v_inven_var)
                #         except:
                #             pass
        else:
            display.warning("Unable to parse %s as an inventory source" % to_text(source))
        return True
    #
    # def files_tmp(self):
    #     return self._list_file_tmp
