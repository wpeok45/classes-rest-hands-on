#!/usr/bin/env python3

from typing import Dict, List, Tuple
import time
import pickle
import os


class Common():
    def __eq__(self, other):
        if isinstance(other, eval(type(self).__name__)):
            return self.__dict__ == other.__dict__
        return NotImplemented


class Workload(Common):
    # ip: str
    # credentials: Credentials
    # storage: List[MountPoint]

    def __init__(self, ip, credentials, storage):
        if (isinstance(ip, str) and
                isinstance(credentials, Credentials) and
                isinstance(storage, list) and
                (False not in [isinstance(x, MountPoint) for x in storage])):
            #    ^^ all storage elements belong to MountPoint class
            self.ip = ip
            self.credentials = credentials
            self.storage = storage
        else:
            raise ValueError

    def __repr__(self):
        return "workload_class:{}:{}:{}".format(self.ip,
                                                self.credentials,
                                                self.storage)


class Credentials(Common):
    # username: str
    # password: str
    # domain: str

    def __init__(self, username, password, domain):
        if (isinstance(username, str) and
                isinstance(password, str) and
                isinstance(domain, str)):
            self.username = username
            self.password = password
            self.domain = domain
        else:
            raise ValueError

    def __repr__(self):
        return "credentials_class:{}:{}:{}".format(self.username,
                                                   self.password,
                                                   self.domain)


class MountPoint(Common):
    # name: str
    # size: int

    def __init__(self, name, size):
        if isinstance(name, str) and isinstance(size, int):
            self.name = name
            self.size = size
        else:
            raise ValueError

    def __repr__(self):
        return "mountpoint_class:{}:{}".format(self.name, self.size)


class Source(Common):
    def __init__(self, ip, username, password, change_ip_possible=True):
        if ip is None or username is None or password is None:
            raise ValueError
        self.__ip = ip
        self.__username = username
        self.__password = password
        self.__change_ip_possible = change_ip_possible

    def change_ip(self, ip):
        if ip is None:
            raise ValueError
        if self.__change_ip_possible:
            self.__ip = ip

    def change_username(self, username):
        if username is None:
            raise ValueError
        self.__username = username

    def change_password(self, password):
        if password is None:
            raise ValueError
        self.__password = password

    def get_ip(self):
        return self.__ip

    def get_username(self):
        return self.__username

    def get_password(self):
        return self.__password


class MigrationTarget(Common):
    # __cloud_type : str
    # cloud_credentials : Credentials
    # target_vm : Workload

    __cloud_types = ["aws", "azure", "vsphere", "vcloud"]

    def __init__(self, cloud_type, cloud_credentials, target_vm):
        if (cloud_type in self.__cloud_types and
                isinstance(cloud_type, str) and
                isinstance(cloud_credentials, Credentials) and
                isinstance(target_vm, Workload)):
            self.__cloud_type = cloud_type
            self.cloud_credentials = cloud_credentials
            self.target_vm = target_vm
        else:
            raise ValueError

    def change_cloud_type(self, cloud_type):
        if cloud_type in self.__cloud_types:
            self.__cloud_type = cloud_type
        else:
            raise ValueError

    def get_cloud_type(self):
        return self.__cloud_type

    def __repr__(self):
        return "migration_target_class:{}:{}:{}".format(self.__cloud_type,
                                                        self.cloud_credentials,
                                                        self.target_vm)


class Migration(Common):
    # selected_mount_points: List[MountPoint]
    # source: Workload
    # migration_target: MigrationTarget
    # migration_state: str

    volume_c_allowed = True

    def __init__(self, selected_mount_points, source, migration_target):
        if (isinstance(selected_mount_points, list) and
                (False not in [isinstance(x, MountPoint)
                               for x in selected_mount_points]) and
                isinstance(source, Workload) and
                isinstance(migration_target, MigrationTarget)):
            self.selected_mount_points = selected_mount_points
            self.source = source
            self.migration_target = migration_target
            self.migration_state = "not started"
        else:
            raise ValueError

    def run(self):
        self.migration_state = "running"
        # source storage contains all of selected mountpoins
        source_storage_ok = False not in [y.name in
                                          [x.name for x in self.source.storage]
                                          for y in self.selected_mount_points]
        if self.volume_c_allowed and source_storage_ok:
            for source_storage in self.source.storage:
                if source_storage.name in [x.name
                                           for x
                                           in self.selected_mount_points]:
                    self.migration_target.target_vm.storage.append(
                        source_storage)
            self.migration_target.target_vm.ip = self.source.ip
            self.migration_target.target_vm.credentials =\
                self.source.credentials
            time.sleep(60)
            self.migration_state = "success"
        else:
            self.migration_state = "error"

    def __repr__(self):
        return "migration_class:{}:{}:{}:{}".format(self.selected_mount_points,
                                                    self.source,
                                                    self.migration_target,
                                                    self.migration_state)


class PersistenceLayer():
    def __init__(self, obj_list, dumpfile):
        if isinstance(obj_list, list) and isinstance(dumpfile, str):
            self.obj_list = obj_list
            self.dumpfile = dumpfile
        else:
            raise ValueError

    def create(self, obj=[]):
        ip_list = {'Source': [], 'Migration': []}
        if obj == []:
            obj = self.obj_list
        for n in obj:
            if isinstance(n, Source):
                ip_list['Source'].append(n.get_ip())
            elif isinstance(n, Migration):
                ip_list['Migration'].append(n.source.ip)
        for v in ip_list.values():
            if len(set(v)) != len(v):
                raise ValueError
        with open(self.dumpfile, 'wb') as f:
            pickle.dump(obj, f)

    def update(self):
        new_obj_list = self.obj_list[:]
        saved_obj_list = self.read()
        for n in saved_obj_list:
            if n not in new_obj_list:
                new_obj_list.append(n)
        self.create(new_obj_list)

    def read(self):
        with open(self.dumpfile, 'rb') as f:
            self.obj_list = pickle.load(f)
        return self.obj_list

    def delete(self):
        os.remove(self.dumpfile)
