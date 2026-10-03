import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class VercelStorageTests(unittest.TestCase):
    def test_local_storage_unchanged(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(main.resolve_database_path(), Path(main.__file__).with_name('tasks.db'))

    def test_vercel_storage_is_temporary(self):
        with patch.dict(os.environ, {'VERCEL': '1'}, clear=True):
            self.assertEqual(main.resolve_database_path(), Path(tempfile.gettempdir()) / 'daylist' / 'tasks.db')

    def test_explicit_path_takes_precedence(self):
        with patch.dict(os.environ, {'VERCEL': '1', 'DB_PATH': 'custom/tasks.db'}, clear=True):
            self.assertEqual(main.resolve_database_path(), Path('custom/tasks.db'))


if __name__ == '__main__':
    unittest.main()
