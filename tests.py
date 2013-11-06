from __future__ import unicode_literals
import unittest
import time

import pymongo
from pymongo.errors import OperationFailure

from mongoredis import MongoRedis


class BaseTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        host = '127.0.0.1'
        port = 27017
        user = 'admin'
        password = 'test'
        db_name = 'test'
        client = pymongo.MongoClient(host, port)
        try:
            client[db_name].authenticate(user, password)
        except OperationFailure:
            client['admin'].authenticate(user, password)
        db = client[db_name]
        self.mr_client = MongoRedis(db, collection_name='cache_test')
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.mr_client.flushdb()
        self.mr_client.start()

    def tearDown(self):
        self.mr_client.end()


class TestKeyMethods(BaseTestCase):

    def test_delete(self):
        self.mr_client.set('a', 'b')
        self.mr_client.set('c', 'd')
        self.mr_client.set('e', 'f')
        self.mr_client.set('g', 'h')
        # Delete multiple
        r = self.mr_client.delete('a', 'DNE')
        self.assertEqual(r, 1)
        r = self.mr_client.delete('c', 'e')
        self.assertEqual(r, 2)
        # Delete DNE
        r = self.mr_client.delete('DNE')
        self.assertEqual(r, 0)
        # Delete One
        r = self.mr_client.delete('g')
        self.assertEqual(r, 1)

    def test_expire(self):
        self.mr_client.set('a', 'b')
        r = self.mr_client.ttl('a')
        self.assertEqual(r, long(-1))
        self.mr_client.expire('a', 15)
        r = self.mr_client.ttl('a')
        self.assertTrue(14 < r < 15)

    def test_flushdb(self):
        self.mr_client.set('a', 'b')
        self.mr_client.set('c', 'd')
        self.assertTrue(self.mr_client.get('a'))
        self.assertTrue(self.mr_client.get('c'))
        self.mr_client.flushdb()
        self.assertFalse(self.mr_client.get('a'))
        self.assertFalse(self.mr_client.get('c'))

    def test_get(self):
        r = self.mr_client.get('DNE')
        self.assertIsNone(r)
        self.mr_client.set('a', 'b')
        r = self.mr_client.get('a')
        self.assertEqual(r, 'b')
        self.mr_client.set('a', 'b', 4)
        time.sleep(5)
        r = self.mr_client.get('a')
        self.assertIsNone(r)
        # In events where process is down gets should still fail!
        self.mr_client.end()
        self.mr_client.set('ts', 'b', 3)
        time.sleep(3)
        self.assertIsNone(self.mr_client.get('ts'))

    def test_set(self):
        # Set clean
        r = self.mr_client.set('a', 'b')
        self.assertTrue(r)
        # Set exists
        r = self.mr_client.set('a', 'c', nx=True)
        self.assertIsNone(r)
        r = self.mr_client.set('e', 'f', xx=True)
        self.assertIsNone(r)
        r = self.mr_client.set('a', 'c', xx=True)
        self.assertTrue(r)
        r = self.mr_client.get('a')
        self.assertEqual(r, 'c')
        # Set Expire
        self.mr_client.set('f', 'd', 3)
        r = self.mr_client.ttl('f')
        self.assertTrue(2 < r < 3)
        time.sleep(4)
        r = self.mr_client.get('f')
        self.assertIsNone(r)


    def test_ttl(self):
        r = self.mr_client.set('a', 'b', 5)
        time.sleep(1)
        r = self.mr_client.ttl('a')
        self.assertTrue(3 < r < 4)
        time.sleep(2)
        r = self.mr_client.ttl('a')
        self.assertTrue(1 < r < 2)




if __name__ == '__main__':
    unittest.main()
