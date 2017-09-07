from test.base import BaseTest

from utils.redis import redis
from redis_db import (
    KeyField, Integer, String, Float, BaseModel, SetField, ListField,
    HashField, DictField,
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
    )
    float_str_dict = DictField(Float(), String())


class GetByIdTestCase(BaseTest):
    def setUp(self):
        redis.set('testing:1:int_key', 2)
        redis.set('testing:2:int_key', '33')
        redis.set('testing:1:str_key', 'test1')
        redis.sadd('testing:1:int_set', *[1, 2, 3, 4, 5])
        redis.sadd('testing:1:str_set', *['a', 'x', 'w'])
        redis.lpush('testing:1:int_list', *[4, 5, 8, 33])
        redis.lpush('testing:1:str_list', *['c', 'b', 'a'])
        redis.lpush('testing:2:str_list', *['l', 'u', 't'])
        redis.hmset('testing:1:hash_key', {
            'int_key': 13,
            'invalid_key': 'some_val',
        })
        redis.hmset('testing:1:float_str_dict', {
            1.3: 'one.three',
            9.6: 'nine.six',
        })
        super(GetByIdTestCase, self).setUp()

    def tearDown(self):
        redis.delete('testing:1:int_key')
        redis.delete('testing:2:int_key')
        redis.delete('testing:1:str_key')
        redis.delete('testing:1:int_set')
        redis.delete('testing:1:str_set')
        redis.delete('testing:1:int_list')
        redis.delete('testing:1:str_list')
        redis.delete('testing:2:str_list')
        redis.delete('testing:1:hash_key')
        redis.delete('testing:1:float_str_dict')
        super(GetByIdTestCase, self).tearDown()

    def test_all_fields(self):
        test_obj = TestClass.get_by_id(redis, 1)
        self.assertEqual(test_obj.int_key, 2)
        self.assertEqual(test_obj.str_key, 'test1')
        self.assertEqual(test_obj.int_set, {1, 2, 3, 4, 5})
        self.assertEqual(test_obj.str_set, {'a', 'x', 'w'})
        self.assertEqual(test_obj.int_list, [33, 8, 5, 4])
        self.assertEqual(test_obj.str_list, ['a', 'b', 'c'])
        self.assertEqual(test_obj.hash_key, {
            'int_key': 13,
            'str_key': None,
        })
        self.assertEqual(test_obj.float_str_dict, {
            1.3: 'one.three',
            9.6: 'nine.six',
        })

    def test_some_fields(self):
        test_obj = TestClass.get_by_id(redis, 2, [
            TestClass.int_key, TestClass.str_list, TestClass.int_list,
        ])
        self.assertEqual(test_obj.int_key, 33)
        self.assertEqual(test_obj.str_key, None)
        self.assertEqual(test_obj.str_list, ['t', 'u', 'l'])
        self.assertEqual(test_obj.int_list, [])
        self.assertEqual(test_obj.hash_key, None)
        self.assertEqual(test_obj.float_str_dict, None)
