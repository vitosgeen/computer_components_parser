import unittest
import os
import json
from utils.cache import get_json_cache, set_json_cache, delete_cache

class TestCache(unittest.TestCase):

    def setUp(self):
        self.test_key = 'testkey123'
        self.test_value = {'name': 'test', 'value': 123}
        set_json_cache(self.test_key, self.test_value)

    def tearDown(self):
        delete_cache(self.test_key)
        cache_dir = './cache'
        if os.path.exists(cache_dir):
            for root, dirs, files in os.walk(cache_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(cache_dir)

    def test_get_json_cache_existing_key(self):
        result = get_json_cache(self.test_key)
        self.assertEqual(result, self.test_value)

    def test_get_json_cache_non_existing_key(self):
        result = get_json_cache('nonexistingkey')
        self.assertIsNone(result)

    def test_set_and_get_json_cache(self):
        # Integration test for setting and getting cache
        new_key = 'integrationkey'
        new_value = {'name': 'integration', 'value': 456}
        set_json_cache(new_key, new_value)
        result = get_json_cache(new_key)
        self.assertEqual(result, new_value)
        delete_cache(new_key)

    def test_set_and_delete_json_cache(self):
        # Integration test for setting and deleting cache
        new_key = 'integrationkey'
        new_value = {'name': 'integration', 'value': 456}
        set_json_cache(new_key, new_value)
        delete_cache(new_key)
        result = get_json_cache(new_key)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()