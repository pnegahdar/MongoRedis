MongoRedis
==========

MongoRedis is a software level drop-in replacement for RedisPy that operates on top of mongodb. The goal is to give you the simplicity of redis commands like set, get, expire without needing that extra dependency in your stack. Obviously performance will hinder but it works on mongodb and widens the types of objects (dicts, datetime, etc) you can save in cache.

## How?
```python
pip install mongoredis

from mongoredis import MongoRedis
from pymongo import MongoClient

db = MongoClient().test_db
mr = MongoRedis(db)
# Start the backround expiring process
mr.start()

# Use like redis-py
mr.set('some_key', 'some_value', 5)
mr.get('some_key)
mr.expire('some_key', 100)
```

Also see [redis-py documentation](https://github.com/andymccurdy/redis-py/), [redis documetaiton](http://redis.io/commands) and [pymongo](http://api.mongodb.org/python/current/api/index.html) documentation.

## Why?

Redis isn't great at distribution and failover even with redis-sentinel and its other solutions. If you're already maintaing mongodb as a major part of your stack on multiple nodes it becomes problematic to maintain redis with it in failover situations. But redis' intuitive interface is amazing. This project tries to take the best of both worlds.

One of the cooler things is that all mongodb types are supported so you can persist datetimes, dictionarys, floats, ints, lists,  etc.


## Performance?

Yup, performance will definitely take a hit. But atleast fsyncs are much more frequent (default configuration) and not everything is held in memory. Heres a stackoverflow thread comparing the performance of mogodb and redis: [StackOverflow](http://stackoverflow.com/questions/5252577/how-much-faster-is-redis-than-mongodb)

In most applications the performance difference shouldn't really matter.


## Contributing?

Please do. I did some of the commands and will add more later on. Here is how to contribute:

1) Find a command from [Redis-py](https://github.com/andymccurdy/redis-py/blob/master/redis/client.py#L604) and [Redis.io](http://redis.io/commands) that is missing in this library

2) Add the command to mongoredis.py class, make sure the interface is very close (preferably identical) to the interface defined by redis-py

3) Write a test for it in tests.py

4) Make a pull request :)
