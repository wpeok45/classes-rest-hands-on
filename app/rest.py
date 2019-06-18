#!/usr/bin/env python3

from app.classes import *
from flask import Flask, jsonify, request, abort
import json
from pprint import pprint

fl = Flask(__name__.split('.')[0])

db = {'workloads': {}, 'migrations': {}}

#
# input json aren't validated. mostly.
# there are many simplifications also: fast and dirty realization, sorry
#


@fl.route('/workload', methods=['PUT'])
def workload_add():
    if not request.json or 'ip' not in request.json:
        abort(400)
    data = request.json
    credentials = Credentials(data['credentials']['username'],
                              data['credentials']['password'],
                              data['credentials']['domain'])
    storage = []
    for d in data["storage"]:
        storage.append(MountPoint(d["name"], int(d["size"])))
    if not db["workloads"]:
        i = 0
    else:
        i = max(db["workloads"].keys()) + 1
    db["workloads"][i] = Workload(data["ip"], credentials, storage)
    # pprint(db)
    return '{"status":"' + str(i) + '"}'


@fl.route('/workload/<int:id>', methods=['POST'])
def workload_modify(id):
    if id not in db['workloads'].keys():
        return '{"status":"not found"}'
    data = request.json
    modified = False
    if 'credentials' in data:
        db['workloads'][id].credentials = Credentials(
            data['credentials']['username'],
            data['credentials']['password'],
            data['credentials']['domain'])
        modified = True
    if 'storage' in data:
        db['workloads'][id].storage = []
        for d in data["storage"]:
            db['workloads'][id].storage.append(MountPoint(d["name"],
                                               int(d["size"])))
        modified = True
    # pprint(db)
    if modified:
        return '{"status":"modified"}'
    else:
        return '{"status":"not modified"}'


@fl.route('/workload/<int:id>', methods=['DELETE'])
def workload_remove(id):
    if id in db['workloads'].keys():
        del(db['workloads'][id])
        # pprint(db)
        return '{"status":"removed"}'
    else:
        return '{"status":"not found"}'


@fl.route('/migration', methods=['PUT'])
def migration_add():
    if not request.json:
        abort(400)
    data = request.json
    selected_mount_points = []
    for d in data["selected_mount_points"]:
        selected_mount_points.append(MountPoint(d["name"], int(d["size"])))
    source = None
    target_vm = None
    for w in db['workloads'].values():
        try:
            if w.ip == data["source_ip"]:
                source = w
            if w.ip == data["migration_target"]["destination_ip"]:
                target_vm = w
        except KeyError:
            abort(400)
    if not source or not target_vm:
        abort(400)
    try:
        cloud_credentials = Credentials(
            data["migration_target"]["cloud_credentials"]["username"],
            data["migration_target"]["cloud_credentials"]["password"],
            data["migration_target"]["cloud_credentials"]["domain"])
        cloud_type = data["migration_target"]["cloud_type"]
    except KeyError:
        abort(400)
    try:
        migration_target = MigrationTarget(cloud_type,
                                           cloud_credentials,
                                           target_vm)
    except ValueError:
        abort(400)
    migration = Migration(selected_mount_points, source, migration_target)
    if not db["migrations"]:
        i = 0
    else:
        i = max(db["migrations"].keys()) + 1
    db["migrations"][i] = migration
    # pprint(db)
    return '{"status":"' + str(i) + '"}'


@fl.route('/migration/<int:id>', methods=['POST'])
def migration_modify(id):
    if not request.json:
        abort(400)
    data = request.json

    if id not in db['migrations'].keys():
        return '{"status":"not found"}'

    migration = db['migrations'][id]
    modified = False
    if 'selected_mount_points' in data:
        selected_mount_points = []
        for d in data["selected_mount_points"]:
            selected_mount_points.append(MountPoint(d["name"],
                                                    int(d["size"])))
        migration.selected_mount_points = selected_mount_points
        modified = True

    if 'source_ip' in data:
        source = None
        for w in db['workloads'].values():
            if w.ip == data["source_ip"]:
                source = w
                break
        if not source:
            abort(400)
        migration.source = w
        modified = True

    if "migration_target" in data:
        target_vm = None
        for w in db['workloads'].values():
            try:
                if w.ip == data["migration_target"]["destination_ip"]:
                    target_vm = w
                    break
            except KeyError:
                abort(400)
        if not target_vm:
            abort(400)
        try:
            cloud_credentials = Credentials(
                data["migration_target"]["cloud_credentials"]["username"],
                data["migration_target"]["cloud_credentials"]["password"],
                data["migration_target"]["cloud_credentials"]["domain"])
            cloud_type = data["migration_target"]["cloud_type"]
        except KeyError:
            abort(400)
        migration_target = MigrationTarget(cloud_type,
                                           cloud_credentials,
                                           target_vm)
        migration.migration_target = migration_target
        modified = True

    # pprint(db)
    if modified:
        return '{"status":"modified"}'
    else:
        return '{"status":"not modified"}'


@fl.route('/migration/<int:id>', methods=['DELETE'])
def migration_remove(id):
    if id in db['migrations'].keys():
        del(db['migrations'][id])
        return '{"status":"removed"}'
    else:
        return '{"status":"not found"}'


@fl.route('/migration/<int:id>/run', methods=['GET'])
def migration_run(id):
    if id in db['migrations'].keys():
        db['migrations'][id].run()
        # pprint(db)
        return '{"status":"' + db['migrations'][id].migration_state + '"}'
    else:
        return '{"status":"not found"}'


@fl.route('/migration/<int:id>/finished', methods=['GET'])
def migration_finished(id):
    if id in db['migrations'].keys():
        if db['migrations'][id].migration_state == 'success':
            return '{"status":"finished"}'
        else:
            return '{"status":"not finished"}'
    else:
        return '{"status":"not found"}'


def main():
    fl.run(debug=True)
