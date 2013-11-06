from __future__ import unicode_literals
import datetime
from multiprocessing.process import Process
import time as pytime

from pymongo.errors import DuplicateKeyError
from pymongo.database import Database


class MongoRedis(object):
    def __init__(self, mongo_db, collection_name='cache'):
        # Ensure index
        if not isinstance(mongo_db, Database):
            raise ValueError(
                'mongo_db must be instance of pymongo.database.Database')
        self.col = mongo_db[collection_name]
        self.col.ensure_index('k', unique=True)
        self.col.ensure_index('exp')
        self.prune_expired()

    def start(self):
        """
        Starts the background process that prunes expired items
        """

        def task():
            while True:
                self.prune_expired()
                pytime.sleep(.5)

        self.processs = Process(target=task)
        self.processs.start()

    def end(self):
        """
        End the background process that prunes expired items
        """
        if not hasattr(self, 'process'):
            self.processs.terminate()

    def prune_expired(self):
        """
        Deletes expired keys from the db, returns count deleted
        """
        now = pytime.time()
        result = self.col.remove({'exp': {'$exists': True, '$lte': now}})
        return result['n']

    ### REDIS COMMANDS ###
    def delete(self, *names):
        """
        Delete one or more keys specified by ``names``
        """
        return self.col.remove({'k': {'$in': names}})['n']

    __delitem__ = delete

    def expire(self, name, time):
        """
        Set an expire flag on key ``name`` for ``time`` seconds. ``time``
        can be represented by an integer or a Python timedelta object.
        """
        expire_at = pytime.time()
        if isinstance(time, datetime.timedelta):
            time = time.seconds + time.days * 24 * 3600
        expire_at += time
        return bool(
            self.col.update({'k': name}, {'$set': {'exp': expire_at}})['n'])

    def flushdb(self):
        """
        Delete all keys in the current database
        """
        self.col.remove()
        return True

    def get(self, name):
        """
        Return the value at key ``name``, or None if the key doesn't exist
        """
        now = pytime.time()
        result = self.col.find_one({'k': name}) or {}
        if result.get('exp', now) < now:
            return None
        return result.get('v')

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        """
        Set the value at key ``name`` to ``value``

        ``ex`` sets an expire flag on key ``name`` for ``ex`` seconds.

        ``px`` sets an expire flag on key ``name`` for ``px`` milliseconds.

        ``nx`` if set to True, set the value at key ``name`` to ``value`` if it
            does not already exist.

        ``xx`` if set to True, set the value at key ``name`` to ``value`` if it
            already exists.
        """
        upsert = True
        expire_at = pytime.time()
        if px:
            # if isinstance(px, datetime.timedelta):
            #     ms = int(px.microseconds / 1000)
            #     px = (px.seconds + px.days * 24 * 3600) * 1000 + ms
            # expire_at += px * 0.001
            raise NotImplementedError # Millis to fine grained
        elif ex:
            if isinstance(ex, datetime.timedelta):
                ex = ex.seconds + ex.days * 24 * 3600
            expire_at += ex
        if nx:
            try:
                data = {'k': name, 'v': value, 'exp': expire_at}
                if ex:
                    data['exp'] = expire_at
                self.col.save(data)
                return True
            except DuplicateKeyError:
                return None
        elif xx:
            upsert = False
        data = {'v': value}
        if ex:
            data['exp'] = expire_at
        result = self.col.update({'k': name}, {'$set': data}, upsert=upsert)
        return True if result['n'] == 1 else None

    __setitem__ = set

    def ttl(self, name):
        """
        Returns the number of seconds until the key ``name`` will expire
        """
        now = pytime.time()
        exp = (self.col.find_one({'k': name}) or {}).get('exp', now)
        diff = exp - now
        return long(-1) if diff <= 0 else diff




