import errno
import shutil
import unittest
import uuid
from unittest import mock

import _support
from _support import ProjectFixture, TEST_TEMP


class ProjectFixtureCleanupTests(unittest.TestCase):
    def setUp(self):
        self.real_rmtree = shutil.rmtree
        self.temp = TEST_TEMP / ("cleanup-" + uuid.uuid4().hex)
        self.temp.mkdir()
        (self.temp / "child").mkdir()
        self.fixture = ProjectFixture.__new__(ProjectFixture)
        self.fixture.temp = self.temp

    def tearDown(self):
        self.real_rmtree(self.temp, ignore_errors=True)

    def test_transient_nonempty_directory_is_retried(self):
        calls = []

        def flaky_rmtree(path, *, onerror):
            calls.append(path)
            if len(calls) == 1:
                raise OSError(errno.ENOTEMPTY, "directory changed during cleanup")
            return self.real_rmtree(path, onerror=onerror)

        with mock.patch.object(_support.shutil, "rmtree", side_effect=flaky_rmtree), mock.patch.object(_support.time, "sleep") as sleep:
            self.fixture.close()

        self.assertFalse(self.temp.exists())
        self.assertEqual(len(calls), 2)
        sleep.assert_called_once_with(0.05)

    def test_persistent_nonempty_directory_exhausts_retries(self):
        failure = OSError(errno.ENOTEMPTY, "directory remains busy")
        with mock.patch.object(_support.shutil, "rmtree", side_effect=failure) as remove, mock.patch.object(_support.time, "sleep") as sleep:
            with self.assertRaises(OSError) as raised:
                self.fixture.close()

        self.assertEqual(raised.exception.errno, errno.ENOTEMPTY)
        self.assertEqual(remove.call_count, 8)
        self.assertEqual(sleep.call_count, 7)

    def test_nontransient_cleanup_error_is_not_retried(self):
        failure = OSError(errno.EIO, "storage error")
        with mock.patch.object(_support.shutil, "rmtree", side_effect=failure) as remove, mock.patch.object(_support.time, "sleep") as sleep:
            with self.assertRaises(OSError) as raised:
                self.fixture.close()

        self.assertEqual(raised.exception.errno, errno.EIO)
        remove.assert_called_once()
        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
