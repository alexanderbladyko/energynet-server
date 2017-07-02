from test.base import BaseTest

from utils.redis import redis
from redis_db import (
    KeyField, Integer, String, BaseModel, SetField, ListField, HashField
)


class TestClass(BaseModel):
    key = 'testing'
    int_key = KeyField(Integer())
    str_key = KeyField(String())
    int_set = SetField(Integer())
    str_set = SetField(String())
    int_list = ListField(Integer())
    str_list = ListField(String())
    hash_key = HashField(
        int_key=Integer(),
        str_key=String(),
        none_key=String(),
    )


class RedisKeyFieldTestCase(BaseTest):
    def setUp(self):
        TestClass.int_key.write(redis, 2, id=1)
        TestClass.int_key.write(redis, '33', id=2)
        TestClass.str_key.write(redis, 'test1', id=1)
        TestClass.int_set.write(redis, [1, 2, 3, 4, 5], id=1)
        TestClass.str_set.write(redis, ['a', 'x', 'w'], id=1)
        TestClass.int_list.write(redis, [4, 5, 8, 33], id=1)
        TestClass.str_list.write(redis, ['l', 'u', 't'], id=2)
        TestClass.hash_key.write(redis, {
            'int_key': 13,
            'str_key': 'str_test',
            'none_key': None,
            'invalid_key': 'some_val',
        }, id=1)
        super(RedisKeyFieldTestCase, self).setUp()

    def tearDown(self):
        TestClass.int_key.delete(redis, id=1)
        TestClass.int_key.delete(redis, id=2)
        TestClass.str_key.delete(redis, id=1)
        TestClass.int_set.delete(redis, id=1)
        TestClass.str_set.delete(redis, id=1)
        TestClass.int_list.delete(redis, id=1)
        TestClass.str_list.delete(redis, id=2)
        TestClass.hash_key.delete(redis, id=1)
        super(RedisKeyFieldTestCase, self).tearDown()

    def test_keys(self):
        self.assertEqual(TestClass.int_key.key(), 'testing:int_key')
        self.assertEqual(TestClass.str_key.key(), 'testing:str_key')
        self.assertEqual(TestClass.int_key.key(5), 'testing:5:int_key')
        self.assertEqual(TestClass.str_key.key(id=17), 'testing:17:str_key')
        self.assertEqual(TestClass.int_set.key(id=5), 'testing:5:int_set')
        self.assertEqual(TestClass.str_set.key(id=5), 'testing:5:str_set')
        self.assertEqual(TestClass.int_list.key(id=5), 'testing:5:int_list')
        self.assertEqual(TestClass.str_list.key(id=5), 'testing:5:str_list')
        self.assertEqual(TestClass.hash_key.key(id=2), 'testing:2:hash_key')

    def test_field_read(self):
        self.assertEqual(TestClass.int_key.read(redis, 1), 2)
        self.assertEqual(TestClass.int_key.read(redis, 2), 33)
        self.assertEqual(TestClass.str_key.read(redis, 1), 'test1')
        self.assertEqual(TestClass.int_set.read(redis, 1), {1, 2, 3, 4, 5})
        self.assertEqual(TestClass.str_set.read(redis, 1), {'a', 'x', 'w'})
        self.assertEqual(TestClass.int_list.read(redis, 1), [4, 5, 8, 33])
        self.assertEqual(TestClass.str_list.read(redis, 2), ['l', 'u', 't'])
        self.assertEqual(TestClass.hash_key.read(redis, 1), {
            'int_key': 13,
            'str_key': 'str_test',
            'none_key': None,
        })
