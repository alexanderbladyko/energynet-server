# from test.base import BaseTest
#
# from utils.server import app
# from utils.socket_server import io
#
#
# class SocketApiTestCase(BaseTest):
#     def setUp(self):
#         self.username = 'test_user'
#         self.password = 'test_password'
#         self.user = self.create_user(self.username, self.password)
#
#         super(SocketApiTestCase, self).setUp()
#
#     def tearDown(self):
#         with self.db.cursor() as cursor:
#             cursor.execute('delete from public.user *;')
#             self.db.commit()
#
#         super(SocketApiTestCase, self).tearDown()
#
#     def test_connect(self):
#         client = io.test_client(app)
#         self.authenticate_client(client, self.user)
#         received = client.get_received()
#
#         self.assertEqual(len(received), 1)
#         self.assertEqual(received[0]['args'], 'connected')
#         client.disconnect()
