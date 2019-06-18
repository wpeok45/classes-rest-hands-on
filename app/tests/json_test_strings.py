wl_add_1 = \
"""{
    "ip": "192.168.1.1",
    "credentials": {
        "password": "pass",
        "domain": "domain1",
        "username": "user"
    },
    "storage": [
        {
            "name": "c:",
            "size": "100"
        },
        {
            "name": "d:",
            "size": "100"
        }
    ]
}"""

wl_add_2 = \
"""{
    "ip": "192.168.1.2",
    "credentials": {
        "password": "pass",
        "domain": "domain1",
        "username": "user"
    },
    "storage": [
        {
            "name": "c:",
            "size": "100"
        },
        {
            "name": "e:",
            "size": "100"
        }
    ]
}"""

wl_mod_1 = \
"""{
    "ip": "192.168.1.1",
    "storage": [
        {
            "name": "f:",
            "size": "100"
        }
    ]
}"""

wl_mod_2 = \
"""{
    "ip": "192.168.1.1",
    "credentials": {
        "password": "pass2",
        "domain": "domain2",
        "username": "user2"
    }
}"""

wl_mod_3 = \
"""{
    "ip": "192.168.1.3"
}"""

migr_add_1 = \
"""{
    "source_ip": "192.168.1.1",
    "migration_target": {
        "destination_ip": "192.168.1.2",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_add_2 = \
"""{
    "source_ip": "192.168.1.2",
    "migration_target": {
        "destination_ip": "192.168.1.1",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "e:",
            "size": "100"
        }
    ]
}"""

migr_add_3 = \
"""{
    "source_ip": "192.168.1.3",
    "migration_target": {
        "destination_ip": "192.168.1.1",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_add_4 = \
"""{
    "source_ip": "192.168.1.1",
    "migration_target": {
        "destination_ip": "192.168.1.3",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_add_5 = \
"""{
    "source_ip": "192.168.1.1",
    "migration_target": {
        "destination_ip": "192.168.1.2",
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_add_6 = \
"""{
    "migration_target": {
        "destination_ip": "192.168.1.2",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_add_7 = \
"""{
    "source_ip": "192.168.1.1",
    "migration_target": {
        "cloud_type": "aws",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        }
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_add_8 = \
"""{
    "source_ip": "192.168.1.1",
    "migration_target": {
        "destination_ip": "192.168.1.2",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "google"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""

migr_mod_1 = \
"""{
    "source_ip": "192.168.1.2",
    "migration_target": {
        "destination_ip": "192.168.1.1",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "azure"
    },
    "selected_mount_points": [
        {
            "name": "f:",
            "size": "100"
        }
    ]
}"""

migr_mod_2 = \
"""{
    "foo": "bar"
}"""

migr_finish = \
"""{
    "source_ip": "192.168.1.1",
    "migration_target": {
        "destination_ip": "192.168.1.2",
        "cloud_credentials": {
            "password": "pass",
            "domain": "dom1",
            "username": "user"
        },
        "cloud_type": "aws"
    },
    "selected_mount_points": [
        {
            "name": "c:",
            "size": "100"
        }
    ]
}"""
