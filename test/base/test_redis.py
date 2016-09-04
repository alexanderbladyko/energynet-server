from test.base import BaseTest

from base.redis import (
    ObjectList, IdField, DataField, ObjectField, ObjectListField
)
from utils.redis import redis, redis_session


class TestObjectList(ObjectList):
    key = 'object'

    id = IdField()
    data = DataField([
        'key1', 'key2', 'key3'
    ])
    other_object = ObjectField()
    other_objects = ObjectListField()


class ObjectListTestCase(BaseTest):
    def setUp(self):

        super(ObjectListTestCase, self).setUp()

    def tearDown(self):
        redis.delete('object:index')
        object_ids = redis.smembers('object')
        for id in object_ids:
            redis.delete('object:%d')

        redis.delete('object')

        super(ObjectListTestCase, self).tearDown()

    def test_id_field(self):
        obj = TestObjectList()
        obj.save()

        self.assertEqual(1, obj.id)
        self.assertEqual(b'1', redis.get('object:index'))
        self.assertSetEqual({b'1'}, redis.smembers('object'))

    def test_id_field_pipeline(self):
        with redis_session() as pipeline:
            obj = TestObjectList()
            obj.save(p=pipeline)

            self.assertEqual(1, obj.id)
            self.assertEqual(b'1', redis.get('object:index'))
            self.assertEqual(set(), redis.smembers('object'))

        self.assertEqual(1, obj.id)
        self.assertEqual(b'1', redis.get('object:index'))
        self.assertSetEqual({b'1'}, redis.smembers('object'))

    def test_data_field(self):
        data = {'key1': 'value1', 'key2': 3, 'invalid_keys': 'some_value'}
        obj = TestObjectList()
        obj.data = data
        obj.save()

        self.assertDictEqual(data, obj.data)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.data])

        actual_data = {'key1': 'value1', 'key2': '3', 'key3': None}
        self.assertDictEqual(actual_data, actual_obj.data)

        redis.delete('object:1:data')

    def test_data_field_pipeline(self):
        with redis_session() as pipeline:
            data = {'key1': 'value1', 'key2': 3, 'invalid_keys': 'some_value'}
            obj = TestObjectList()
            obj.data = data
            obj.save(p=pipeline)

            self.assertDictEqual(data, obj.data)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.data])

        actual_data = {'key1': 'value1', 'key2': '3', 'key3': None}
        self.assertDictEqual(actual_data, actual_obj.data)

        redis.delete('object:1:data')

    def test_object_field(self):
        obj = TestObjectList()
        obj.other_object = 3
        obj.save()

        self.assertEqual(3, obj.other_object)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.other_object])
        self.assertEqual(3, actual_obj.other_object)

        redis.delete('object:1:other_object')

    def test_object_field_pipeline(self):
        with redis_session() as pipeline:
            obj = TestObjectList()
            obj.other_object = 3
            obj.save(p=pipeline)

        self.assertEqual(3, obj.other_object)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.other_object])
        self.assertEqual(3, actual_obj.other_object)

        redis.delete('object:1:other_object')

    def test_object_list_field(self):
        obj = TestObjectList()
        obj.other_objects = [3]
        obj.save()

        self.assertListEqual([3], obj.other_objects)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.other_objects])
        self.assertListEqual([3], actual_obj.other_objects)

        redis.delete('object:1:other_objects')

    def test_object_list_field_pipeline(self):
        with redis_session() as pipeline:
            obj = TestObjectList()
            obj.other_objects = [3]
            obj.save(p=pipeline)

        self.assertListEqual([3], obj.other_objects)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.other_objects])
        self.assertListEqual([3], actual_obj.other_objects)

        redis.delete('object:1:other_objects')

    def test_get_by_id(self):
        data = {'key1': 'value1', 'key2': 3, 'invalid_keys': 'some_value'}
        obj = TestObjectList()
        obj.data = data
        obj.other_object = 3
        obj.other_objects = [3]
        obj.save()

        actual_obj = TestObjectList.get_by_id(1)
        self.assertEqual(1, actual_obj.id)
        self.assertEqual(3, actual_obj.other_object)
        self.assertListEqual([3], actual_obj.other_objects)

        actual_obj = TestObjectList.get_by_id(1, [TestObjectList.data])
        self.assertEqual(1, actual_obj.id)
        self.assertIsNotNone(actual_obj.data)
        self.assertIsNone(actual_obj.other_object)
        self.assertIsNone(actual_obj.other_objects)

        redis.delete('object:1:data')
        redis.delete('object:1:other_object')
        redis.delete('object:1:other_objects')

    def test_get_all(self):
        for i in range(3):
            obj = TestObjectList()
            obj.other_object = i
            obj.other_objects = [i]
            obj.save()

        obj_list = TestObjectList.get_all()

        for i in range(3):
            actual_obj = next(o for o in obj_list if o.id == (i + 1))
            self.assertEqual(i, actual_obj.other_object)
            self.assertListEqual([i], actual_obj.other_objects)

        obj_list = TestObjectList.get_all([TestObjectList.other_object])

        for i in range(3):
            actual_obj = next(o for o in obj_list if o.id == (i + 1))
            self.assertEqual(i, actual_obj.other_object)
            self.assertIsNone(actual_obj.other_objects)

        for i in range(3):
            redis.delete('object:' + str(i+1) + ':other_object')
            redis.delete('object:' + str(i+1) + ':other_objects')

    def test_get_by_ids(self):
        for i in range(3):
            obj = TestObjectList()
            obj.other_object = i
            obj.other_objects = [i]
            obj.save()

        obj_list = TestObjectList.get_by_ids([1, 3])

        for i in [0, 2]:
            actual_obj = next(o for o in obj_list if o.id == (i + 1))
            self.assertEqual(i, actual_obj.other_object)
            self.assertListEqual([i], actual_obj.other_objects)

        obj_list = TestObjectList.get_by_ids([1, 3], [TestObjectList.other_object])

        for i in [0, 2]:
            actual_obj = next(o for o in obj_list if o.id == (i + 1))
            self.assertEqual(i, actual_obj.other_object)
            self.assertIsNone(actual_obj.other_objects)

        for i in range(3):
            redis.delete('object:' + str(i+1) + ':other_object')
            redis.delete('object:' + str(i+1) + ':other_objects')

    def test_delete(self):
        data = {'key1': 'value1', 'key2': 3, 'invalid_keys': 'some_value'}
        obj = TestObjectList()
        obj.data = data
        obj.other_object = 3
        obj.other_objects = [3]
        obj.save()

        obj.delete()

    def test_get_by_id_save(self):
        obj = TestObjectList()
        obj.save()

        obj = TestObjectList.get_by_id(1)
        with redis_session() as pipeline:
            obj.other_object = 3
            obj.save(p=pipeline)

        self.assertEqual(b'3', redis.get('object:1:other_object'))
        redis.delete('object:1:other_object')
