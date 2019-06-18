#!/usr/bin/env python3

import unittest
import app.rest as app
import requests
import app.tests.json_test_strings as j

DEFAULT_HEADER = 'application/json'


class TestRest(unittest.TestCase):
    def _request(
            self, url, payload='', req="POST", headers=DEFAULT_HEADER):

        _url = self.host + url
        _headers = {'content-type': headers}
        if req == "POST":
            _response = requests.post(_url, data=payload, headers=_headers)
        elif req == "PUT":
            _response = requests.put(_url, data=payload, headers=_headers)
        elif req == "DELETE":
            _response = requests.delete(_url, headers=_headers)
        elif req == "GET":
            _response = requests.get(_url, headers=_headers)
        data = {}
        if _response.status_code == 200:
            data = _response.json()
        return _response.status_code, data

    def setUp(self):
        self.host = "http://127.0.0.1:5000"

    def test_workload_migration(self):
        # workload add
        status, response = self._request("/workload", j.wl_add_1, "PUT")
        self.assertEqual(response['status'], '0')
        status, response = self._request("/workload", j.wl_add_2, "PUT")
        self.assertEqual(response['status'], '1')

        # migration add
        status, response = self._request("/migration", j.migr_add_1, "PUT")
        self.assertEqual(response['status'], '0')
        status, response = self._request("/migration", j.migr_add_2, "PUT")
        self.assertEqual(response['status'], '1')
        status, response = self._request("/migration", j.migr_add_3, "PUT")
        self.assertEqual(status, 400)
        status, response = self._request("/migration", j.migr_add_4, "PUT")
        self.assertEqual(status, 400)
        status, response = self._request("/migration", j.migr_add_5, "PUT")
        self.assertEqual(status, 400)
        status, response = self._request("/migration", j.migr_add_6, "PUT")
        self.assertEqual(status, 400)
        status, response = self._request("/migration", j.migr_add_7, "PUT")
        self.assertEqual(status, 400)
        status, response = self._request("/migration", j.migr_add_8, "PUT")
        self.assertEqual(status, 400)

        # migration modify
        status, response = self._request("/migration/0", j.migr_mod_1, "POST")
        self.assertEqual(response['status'], 'modified')
        status, response = self._request("/migration/7", j.migr_mod_1, "POST")
        self.assertEqual(response['status'], 'not found')
        status, response = self._request("/migration/1", j.migr_mod_2, "POST")
        self.assertEqual(response['status'], 'not modified')

        # migration run
        status, response = self._request("/migration/1/run", req="GET")
        self.assertEqual(response['status'], 'success')
        status, response = self._request("/migration/10/run", req="GET")
        self.assertEqual(response['status'], 'not found')

        # migration check finished
        status, response = self._request("/migration/1/finished", req="GET")
        self.assertEqual(response['status'], 'finished')
        status, response = self._request("/migration/0/finished", req="GET")
        self.assertEqual(response['status'], 'not finished')
        status, response = self._request("/migration/10/finished", req="GET")
        self.assertEqual(response['status'], 'not found')

        # migration remove
        status, response = self._request("/migration/0", req="DELETE")
        self.assertEqual(response['status'], 'removed')
        status, response = self._request("/migration/1", req="DELETE")
        self.assertEqual(response['status'], 'removed')

        # workload modify
        status, response = self._request("/workload/0", j.wl_mod_1, "POST")
        self.assertEqual(response['status'], 'modified')
        status, response = self._request("/workload/1", j.wl_mod_2, "POST")
        self.assertEqual(response['status'], 'modified')
        status, response = self._request("/workload/10", j.wl_mod_2, "POST")
        self.assertEqual(response['status'], 'not found')
        status, response = self._request("/workload/0", j.wl_mod_3, "POST")
        self.assertEqual(response['status'], 'not modified')

        # workload remove
        status, response = self._request("/workload/0", req="DELETE")
        self.assertEqual(response['status'], 'removed')
        status, response = self._request("/workload/1", req="DELETE")
        self.assertEqual(response['status'], 'removed')


if __name__ == "__main__":
    unittest.main()
