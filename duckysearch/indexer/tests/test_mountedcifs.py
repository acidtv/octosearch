import unittest
from ..mountedcifs import Mountedcifs

class TestMountedcifs (unittest.TestCase):

	_instance = None

	def setUp(self):
		self._instance = Mountedcifs(None, None, None)

	def test_parse_cifsacl_allok(self):
		acl = ("REVISION:0x1\n"
			"CONTROL:0x8404\n"
			"OWNER:S-1-5-32-544\n"
			"GROUP:S-1-5-21-4227689985-3459864422-41629276-513\n"
			"ACL:S-1-5-18:0x0/0x10/0x1f01ff\n"
			"ACL:S-1-5-21-4227689985-3459864422-41629276-1126:0x0/0x10/0x1f01ff\n")

		self.assertEqual(
			self._instance.parse_cifsacl(acl),
			['S-1-5-18', 'S-1-5-21-4227689985-3459864422-41629276-1126']
		)

	def test_parse_cifsacl_onedenied(self):
		acl = ("REVISION:0x1\n"
			"CONTROL:0x8404\n"
			"OWNER:S-1-5-32-544\n"
			"GROUP:S-1-5-21-4227689985-3459864422-41629276-513\n"
			"ACL:S-1-5-18:0x0/0x10/0x1f01ff\n"
			"ACL:S-1-5-21-4227689985-3459864422-41629276-1126:0x1/0x10/0x1f01ff\n")

		self.assertEqual(
			self._instance.parse_cifsacl(acl),
			['S-1-5-18']
		)
