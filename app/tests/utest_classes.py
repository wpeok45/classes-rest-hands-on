#!/usr/bin/env python3

import unittest
import app.classes as app
import time
import os


class TestCredentials(unittest.TestCase):
    def test_username_not_str(self):
        self.assertRaises(
            ValueError, app.Credentials, 123, 'password', 'domain')

    def test_password_not_str(self):
        self.assertRaises(
            ValueError, app.Credentials, 'username', [], 'domain')

    def test_domain_not_str(self):
        self.assertRaises(
            ValueError, app.Credentials, 'username', 'password', True)

    def test_proper_credintials(self):
        c = app.Credentials('John', 'JohnPass', 'domain1')
        self.assertEqual(c.username, 'John')
        self.assertEqual(c.password, 'JohnPass')
        self.assertEqual(c.domain, 'domain1')


class TestMountPoint(unittest.TestCase):
    def test_name_not_str(self):
        self.assertRaises(ValueError, app.MountPoint, 1, 50)

    def test_size_not_int(self):
        self.assertRaises(ValueError, app.MountPoint, 'c:', '100')

    def test_proper_mount_point(self):
        mp = app.MountPoint('c:', 100)
        self.assertEqual(mp.name, 'c:')
        self.assertEqual(mp.size, 100)


class TestSource(unittest.TestCase):
    def setUp(self):
        self.s = app.Source('192.168.1.1', 'user', 'pass')
        self.s_specific_source = app.Source(
            '192.168.1.1', 'user', 'pass', False)

    def test_ip_none(self):
        self.assertRaises(ValueError, app.Source, None, 'user', 'pass')

    def test_username_none(self):
        self.assertRaises(ValueError, app.Source, '192.168.1.1', None, 'pass')

    def test_password_none(self):
        self.assertRaises(ValueError, app.Source, '192.168.1.1', 'user', None)

    def test_change_ip(self):
        ip = self.s.get_ip()
        self.s.change_ip('192.168.1.2')
        self.assertEqual(self.s.get_ip(), '192.168.1.2')
        self.s.change_ip(ip)

    def test_change_ip_to_none(self):
        self.assertRaises(ValueError, self.s.change_ip, None)

    def test_change_ip_cannot_change_ip_for_specified_source(self):
        self.s_specific_source.change_ip('192.168.1.2')
        self.assertEqual(self.s_specific_source.get_ip(), '192.168.1.1')

    def test_change_username(self):
        username = self.s.get_username()
        self.s.change_username("user2")
        self.assertEqual(self.s.get_username(), "user2")
        self.s.change_username(username)

    def test_change_username_to_none(self):
        self.assertRaises(ValueError, self.s.change_username, None)

    def test_change_password(self):
        password = self.s.get_password()
        self.s.change_password("pass2")
        self.assertEqual(self.s.get_password(), "pass2")
        self.s.change_password(password)

    def test_change_password_to_none(self):
        self.assertRaises(ValueError, self.s.change_password, None)

    def test_proper_source(self):
        self.assertEqual(self.s.get_ip(), '192.168.1.1')
        self.assertEqual(self.s.get_username(), 'user')
        self.assertEqual(self.s.get_password(), 'pass')


class TestWorkload(unittest.TestCase):
    def setUp(self):
        self.credentials = app.Credentials('John', 'JohnPass', 'domain1')
        self.storage = [app.MountPoint('c:', 100), app.MountPoint('d:', 100)]

    def test_ip_not_str(self):
        self.assertRaises(ValueError,
                          app.Workload,
                          123,
                          self.credentials,
                          self.storage)

    def test_credentials_not_credentials_class(self):
        self.assertRaises(ValueError,
                          app.Workload,
                          '192.168.1.1',
                          'user:pass',
                          self.storage)

    def test_storage_not_list(self):
        self.assertRaises(ValueError,
                          app.Workload,
                          '192.168.1.1',
                          self.credentials,
                          app.MountPoint('c:', 100))

    def test_storage_not_list_of_mountpoint_class(self):
        self.assertRaises(ValueError,
                          app.Workload,
                          '192.168.1.1',
                          self.credentials, [1, 2, 3])

    def test_proper_workload(self):
        wl = app.Workload('192.168.1.1', self.credentials, self.storage)
        self.assertEqual(wl.ip, '192.168.1.1')
        self.assertEqual(wl.credentials, self.credentials)
        self.assertEqual(wl.storage, self.storage)


class TestMigrationTarget(unittest.TestCase):
    def setUp(self):
        self.cloud_credentials = app.Credentials(
            'John', 'JohnPass', 'domain1')
        self.credentials = app.Credentials('John', 'JohnPass', 'domain1')
        self.storage = [app.MountPoint('c:', 100), app.MountPoint('d:', 100)]
        self.target_vm = app.Workload(
            '192.168.1.1', self.credentials, self.storage)
        self.mt = app.MigrationTarget(
            "aws", self.cloud_credentials, self.target_vm)

    def test_cloud_type_not_str(self):
        self.assertRaises(ValueError,
                          app.MigrationTarget,
                          123,
                          self.cloud_credentials,
                          self.target_vm)

    def test_cloud_type_not_in_set(self):
        self.assertRaises(ValueError,
                          app.MigrationTarget,
                          "amazon",
                          self.cloud_credentials,
                          self.target_vm)

    def test_cloud_credintials_not_credentials_class(self):
        self.assertRaises(ValueError,
                          app.MigrationTarget,
                          "aws",
                          'user:pass',
                          self.target_vm)

    def test_target_vm_not_workload_class(self):
        self.assertRaises(ValueError,
                          app.MigrationTarget,
                          "aws",
                          self.cloud_credentials,
                          "target")

    def test_change_cloud_type(self):
        ct = self.mt.get_cloud_type()
        for nct in ["aws", "azure", "vsphere", "vcloud"]:
            self.mt.change_cloud_type(nct)
            self.assertEqual(self.mt.get_cloud_type(), nct)
        self.assertRaises(ValueError, self.mt.change_cloud_type, "google")
        self.mt.change_cloud_type(ct)

    def test_proper_migrationtarget(self):
        self.assertEqual(self.mt.get_cloud_type(), "aws")
        self.assertEqual(self.mt.cloud_credentials, self.cloud_credentials)
        self.assertEqual(self.mt.target_vm, self.target_vm)


class TestMigration(unittest.TestCase):
    def setUp(self):
        self.selected_mount_points = [app.MountPoint('c:', 100)]

        self.selected_absent_mount_points = [app.MountPoint('c:', 100),
                                             app.MountPoint('z:', 100)]

        self.source_credentials = app.Credentials('John',
                                                  'JohnPass',
                                                  'domain1')

        self.source_storage = [app.MountPoint('c:', 100),
                               app.MountPoint('d:', 100),
                               app.MountPoint('e:', 100)]

        self.source = app.Workload('192.168.1.1',
                                   self.source_credentials,
                                   self.source_storage)

        self.cloud_credentials = app.Credentials('CloudJohn',
                                                 'CloudJohnPass',
                                                 'domain1')

        self.target_credentials = app.Credentials('John',
                                                  'JohnPass',
                                                  'domain1')

        self.target_storage = [app.MountPoint('f:', 100),
                               app.MountPoint('g:', 100)]

        self.target_vm = app.Workload('192.168.1.1',
                                      self.target_credentials,
                                      self.target_storage)

        self.migration_target = app.MigrationTarget("aws",
                                                    self.cloud_credentials,
                                                    self.target_vm)

        self.migration = app.Migration(self.selected_mount_points,
                                       self.source,
                                       self.migration_target)

    def test_selected_mount_points_not_list(self):
        self.assertRaises(ValueError,
                          app.Migration,
                          "asd",
                          self.source,
                          self.migration_target)

    def test_selected_mount_points_not_list_of_mountpoint(self):
        self.assertRaises(ValueError,
                          app.Migration,
                          [1, 2, 3],
                          self.source,
                          self.migration_target)

    def test_source_not_workload_class(self):
        self.assertRaises(ValueError,
                          app.Migration,
                          self.selected_mount_points,
                          "source",
                          self.migration_target)

    def test_migration_target_not_migrationtarget_class(self):
        self.assertRaises(ValueError,
                          app.Migration,
                          self.selected_mount_points,
                          self.source,
                          "target")

    def test_proper_migration(self):
        self.assertEqual(self.migration.selected_mount_points,
                         self.selected_mount_points)
        self.assertEqual(self.migration.source, self.source)
        self.assertEqual(self.migration.migration_target,
                         self.migration_target)

    def test_run_error_migration_volume_c_is_not_allowed(self):
        self.migration.volume_c_allowed = False
        self.migration.run()
        self.assertEqual(self.migration.migration_state, "error")

    def test_run_error_migration_selected_storages_are_absent(self):
        self.migration_abs = app.Migration(self.selected_absent_mount_points,
                                           self.source,
                                           self.migration_target)
        self.migration_abs.run()
        self.assertEqual(self.migration_abs.migration_state, "error")

    def test_run_successful(self):
        self.migration.run()
        self.assertEqual(self.migration.migration_state, "success")
        self.assertEqual(self.target_vm.ip, self.source.ip)
        self.assertEqual(self.target_vm.credentials, self.source.credentials)
        selected_mountpoints_are_in_target_storage =\
            False not in [x.name in [y.name for y in self.target_vm.storage]
                          for x in self.selected_mount_points]
        copied_target_storage_elements_are_equal_to_source_ones =\
            False not in [x in self.source.storage
                          for x in self.target_vm.storage
                          if x.name in
                          [y.name for y in self.selected_mount_points]]
        self.assertTrue(selected_mountpoints_are_in_target_storage)
        self.assertTrue(
            copied_target_storage_elements_are_equal_to_source_ones)
        self.assertEqual([(x.name, x.size) for x in self.target_vm.storage],
                         [("f:", 100), ("g:", 100), ("c:", 100)])


class TestPersistenceLayer(unittest.TestCase):
    def setUp(self):
        self.source_source = app.Source('192.168.1.1', 'user', 'pass')

        self.source_source_with_different_ip = app.Source('192.168.1.2',
                                                          'user',
                                                          'pass')

        self.selected_mount_points = [app.MountPoint('c:', 100)]

        self.source_credentials = app.Credentials('John',
                                                  'JohnPass',
                                                  'domain1')

        self.source_storage = [app.MountPoint('c:', 100),
                               app.MountPoint('d:', 100),
                               app.MountPoint('e:', 100)]

        self.source = app.Workload('192.168.1.1',
                                   self.source_credentials,
                                   self.source_storage)

        self.source_with_different_ip = app.Workload('192.168.1.2',
                                                     self.source_credentials,
                                                     self.source_storage)

        self.cloud_credentials = app.Credentials('CloudJohn',
                                                 'CloudJohnPass',
                                                 'domain1')

        self.target_credentials = app.Credentials('John',
                                                  'JohnPass',
                                                  'domain1')

        self.target_storage = [app.MountPoint('f:', 100),
                               app.MountPoint('g:', 100)]

        self.target_vm = app.Workload('192.168.2.1',
                                      self.target_credentials,
                                      self.target_storage)

        self.migration_target = app.MigrationTarget("aws",
                                                    self.cloud_credentials,
                                                    self.target_vm)

        self.migration = app.Migration(self.selected_mount_points,
                                       self.source,
                                       self.migration_target)

        self.migration_with_different_ip = app.Migration(
            self.selected_mount_points,
            self.source_with_different_ip,
            self.migration_target)

        self.obj_list1 = [self.selected_mount_points,
                          self.source_credentials,
                          self.source_storage,
                          self.source,
                          self.cloud_credentials,
                          self.target_credentials,
                          self.target_storage,
                          self.target_vm,
                          self.migration_target,
                          self.migration]

    def test_delete(self):
        if os.path.exists('dump.pickle'):
            os.remove('dump.pickle')
        self.assertFalse(os.path.exists('dump.pickle'))
        with open('dump.pickle', 'w'):
            pass
        self.assertTrue(os.path.exists('dump.pickle'))
        pl = app.PersistenceLayer([], 'dump.pickle')
        pl.delete()
        self.assertFalse(os.path.exists('dump.pickle'))

    def test_create_read(self):
        if os.path.exists('dump.pickle'):
            os.remove('dump.pickle')
        self.assertFalse(os.path.exists('dump.pickle'))
        pl1 = app.PersistenceLayer(self.obj_list1, 'dump.pickle')
        pl1.create()
        self.assertTrue(os.path.exists('dump.pickle'))
        pl2 = app.PersistenceLayer([], 'dump.pickle')
        obj_list2 = pl2.read()
        self.assertEqual(self.obj_list1, obj_list2)

    def test_update(self):
        if os.path.exists('dump.pickle'):
            os.remove('dump.pickle')
        self.assertFalse(os.path.exists('dump.pickle'))
        app.PersistenceLayer(
            [self.selected_mount_points, self.source_credentials],
            'dump.pickle').create()
        self.assertTrue(os.path.exists('dump.pickle'))
        app.PersistenceLayer([self.source_storage], 'dump.pickle').update()
        pl = app.PersistenceLayer([], 'dump.pickle')
        self.assertEqual(pl.read(), [self.source_storage,
                                     self.selected_mount_points,
                                     self.source_credentials])
        os.remove('dump.pickle')
        self.assertFalse(os.path.exists('dump.pickle'))

    def test_create_same_ip(self):
        if os.path.exists('dump.pickle'):
            os.remove('dump.pickle')
        self.assertFalse(os.path.exists('dump.pickle'))
        self.assertRaises(ValueError,
                          app.PersistenceLayer(
                              [self.source_source, self.source_source],
                              'dump.pickle').create)

        app.PersistenceLayer(
            [self.source_source, self.source_source_with_different_ip],
            'dump.pickle').create()

        self.assertTrue(os.path.exists('dump.pickle'))
        os.remove('dump.pickle')

        self.assertFalse(os.path.exists('dump.pickle'))
        self.assertRaises(ValueError,
                          app.PersistenceLayer(
                              [self.migration, self.migration],
                              'dump.pickle').create)

        app.PersistenceLayer(
            [self.migration, self.migration_with_different_ip],
            'dump.pickle').create()

        self.assertTrue(os.path.exists('dump.pickle'))
        os.remove('dump.pickle')


if __name__ == "__main__":
    unittest.main()
