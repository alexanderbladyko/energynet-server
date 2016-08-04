from test.base import BaseTest


CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["serverUrl", "gameApi", "authApi"],
    "properties": {
        "serverUrl": {"type": "string"},
        "gameApi": {"type": "string"},
        "authApi": {"type": "string"},
    }
}


class ConfigApiTestCase(BaseTest):
    URL = '/config'

    def test_success_get(self):
        response = self.client_get(self.URL)

        self.assertEqual(response.status_code, 200)
        self.assertResponseSchema(response.json, CONFIG_SCHEMA)
