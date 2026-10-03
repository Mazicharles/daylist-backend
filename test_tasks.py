"""Run with .venv/Scripts/python -m unittest -v."""
import tempfile
import unittest
from pathlib import Path
from fastapi import HTTPException
import main


class TaskTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='.test-temp-', dir=Path(__file__).parent)
        self.original = main.DB_PATH
        main.DB_PATH = Path(self.temp.name) / 'test.db'
        with main.database() as db:
            db.execute('CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, position INTEGER NOT NULL)')

    def tearDown(self):
        main.DB_PATH = self.original
        self.temp.cleanup()

    def test_task_lifecycle_and_persistence(self):
        first = main.create_task(main.TaskCreate(title=' First '))
        second = main.create_task(main.TaskCreate(title='Second'))
        self.assertEqual(first['title'], 'First')
        updated = main.update_task(first['id'], main.TaskUpdate(title='Edited', completed=True))
        self.assertTrue(updated['completed'])
        self.assertEqual(updated['title'], 'Edited')
        main.reorder_tasks(main.Reorder(ids=[second['id'], first['id']]))
        self.assertEqual([t['id'] for t in main.list_tasks()], [second['id'], first['id']])
        main.delete_task(first['id'])
        self.assertEqual(len(main.list_tasks()), 1)

    def test_invalid_operations(self):
        with self.assertRaises(HTTPException):
            main.create_task(main.TaskCreate(title='   '))
        task = main.create_task(main.TaskCreate(title='Task'))
        for ids in [[], [task['id'], task['id']], [999]]:
            with self.assertRaises(HTTPException):
                main.reorder_tasks(main.Reorder(ids=ids))
        self.assertEqual(main.list_tasks()[0]['position'], 0)
        with self.assertRaises(HTTPException):
            main.update_task(999, main.TaskUpdate(completed=True))
        with self.assertRaises(HTTPException):
            main.delete_task(999)


if __name__ == '__main__':
    unittest.main()
