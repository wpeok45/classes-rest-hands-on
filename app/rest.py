#!/usr/bin/env python3
 
from app.classes import *
from flask import Flask, abort
from flask_restx import Api, Resource, fields
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version="1.0", title="Workload migration API", description="",)

ns = api.namespace("workload", description="namespace operations")
ns1 = api.namespace("migration", description="namespace operations")
db = {'workloads': {}, 'migrations': {}}


credentials_field = api.model('credentials', {
    'password': fields.String,
    'domain': fields.String,
    'username': fields.String
})

storage_field = api.model("storage", {"name": fields.String, "size": fields.Integer})

workload_model = api.model('workload', {
    'ip': fields.String(required=True, description='unique IP'),
    'credentials': fields.Nested(credentials_field, required=True),
    'storage': fields.List(fields.Nested(storage_field), required=True)
})

migration_target_field = api.model('migration_target', {
    'destination_ip': fields.String(required=True, description='unique IP'),
    'cloud_credentials': fields.Nested(credentials_field, required=True),
    'cloud_type': fields.String(required=True, description='aws, azure, vsphere, vcloud - no other values are allowed')
})

migration_model = api.model('migration', {
    'source_ip': fields.String(required=True, description='unique IP'),
    'migration_target': fields.Nested(migration_target_field, required=True),
    'selected_mount_points': fields.List(fields.Nested(storage_field), required=True)
})

@ns1.route("/")
class Migration_API_List(Resource):
    """Shows a list of all migration, and lets you POST to add new migration"""

    @ns1.doc("list_migrations")
    @ns1.marshal_with(migration_model)
    def get(self):
        """Get migrations"""
        return list(db["migrations"].values())

    @ns1.doc("create_migration")
    @ns1.expect(migration_model)
    @ns1.marshal_with(migration_model, code=201)
    def post(self):
        """Create a new migration"""
        data = api.payload
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
            abort(400, 'no source or no target_vm')
        try:
            cloud_credentials = Credentials(
                data["migration_target"]["cloud_credentials"]["username"],
                data["migration_target"]["cloud_credentials"]["password"],
                data["migration_target"]["cloud_credentials"]["domain"])
            cloud_type = data["migration_target"]["cloud_type"]
        except KeyError:
            abort(400, 'Credentials init, KeyError')
        try:
            migration_target = MigrationTarget(cloud_type,
                                            cloud_credentials,
                                            target_vm)
        except ValueError:
            abort(400, 'MigrationTarget init, ValueError')
        migration = Migration(selected_mount_points, source, migration_target)
        if not db["migrations"]:
            i = 0
        else:
            i = max(db["migrations"].keys()) + 1
        db["migrations"][i] = migration
        # pprint(db)
        #return '{"status":"' + str(i) + '"}'

        return api.payload, 201


@ns1.route("/<int:id>")
@ns1.response(404, "Migration not found")
@ns1.param("id", "The workload identifier")
class Migration_API(Resource):
    """Show a single migration item and lets you delete them"""

    @ns1.doc("get_migration")
    @ns1.marshal_with(migration_model)
    def get(self, id):
        """Fetch a given migration"""
        if id not in db['migrations'].keys():  return "", 404
        return db["migration"][id]

    @ns1.doc("delete_migration")
    @ns1.response(204, "Migration deleted")
    def delete(self, id):
        """Delete a migration given its identifier"""
        if id not in db['migrations'].keys():  return "", 404
        del(db['migrations'][id])
        return "", 204

    @ns1.expect(migration_model)
    @ns1.marshal_with(migration_model)
    def put(self, id):
        """Update a migration given its identifier"""
        if id not in db['migrations'].keys(): return "", 404

        data = api.payload
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

        return api.payload, 200 if modified else 304 # Not Modified

@ns1.route("/<int:id>/run")
@ns1.response(404, "Migration not found")
@ns1.param("id", "The workload identifier")
class Migration_API_run(Resource):
    @ns1.doc("run_migration")
    def get(self, id):
        if id not in db['migrations'].keys():  return "", 404
        db['migrations'][id].run()
        return '{"status":"' + db['migrations'][id].migration_state + '"}',200


@ns1.route("/<int:id>/finished")
@ns1.response(404, "Migration not found")
@ns1.param("id", "The workload identifier")
class Migration_API_finish(Resource):
    @ns1.doc("get_migration")
    def get(self, id):
        if id not in db['migrations'].keys(): return "", 404
        if db['migrations'][id].migration_state == 'success':
            return 'finished',200
        else:
            return 'not finished',200


###############################
#
#   
###############################
@ns.route("/")
class Workload_API_List(Resource):
    """Shows a list of all workloads, and lets you POST to add new workload"""

    @ns.doc("list_workloads")
    @ns.marshal_with(workload_model)
    def get(self):
        """Get workloads"""
        return list(db["workloads"].values())

    @ns.doc("create_workload")
    @ns.expect(workload_model)
    @ns.marshal_with(workload_model, code=201)
    def post(self):
        """Create a new workload"""
        data = api.payload
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

        return api.payload, 201


@ns.route("/<int:id>")
@ns.response(404, "Workload not found")
@ns.param("id", "The workload identifier")
class Workload_API(Resource):
    """Show a single workload item and lets you delete them"""

    @ns.doc("get_workload")
    @ns.marshal_with(workload_model)
    def get(self, id):
        """Fetch a given workload"""
        if id not in db['workloads'].keys():  return "", 404
        return db["workloads"][id]

    @ns.doc("delete_workload")
    @ns.response(204, "Workload deleted")
    def delete(self, id):
        """Delete a workload given its identifier"""
        if id not in db['workloads'].keys():  return "", 404
        del(db['workloads'][id])
        return "", 204

    @ns.expect(workload_model)
    @ns.marshal_with(workload_model)
    def put(self, id):
        """Update a workload given its identifier"""
        if id not in db['workloads'].keys(): return "", 404

        data = api.payload
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

        return api.payload, 200 if modified else 304 # Not Modified


def main():
    app.run(debug=True)
    
