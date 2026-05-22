import tempfile
import unittest
from pathlib import Path

from tinydb import TinyDB

from app import create_app


class TinySocialAppTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tempdir.name) / "test-db.json"
        self.app = create_app({"TESTING": True, "DATABASE_PATH": self.db_path})
        self.client = self.app.test_client()

    def tearDown(self):
        self.tempdir.cleanup()

    def test_homepage_shows_empty_state_when_no_posts_exist(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No posts yet. Be the first to share an update.", response.data)

    def test_post_submission_is_saved_and_rendered_on_feed(self):
        response = self.client.post(
            "/posts",
            data={"author": "Alice", "content": "Hello TinySocial!"},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Alice", response.data)
        self.assertIn(b"Hello TinySocial!", response.data)

        with TinyDB(self.db_path) as db:
            posts = db.all()

        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]["author"], "Alice")
        self.assertEqual(posts[0]["content"], "Hello TinySocial!")

    def test_feed_shows_newest_posts_first(self):
        with TinyDB(self.db_path) as db:
            db.insert(
                {
                    "author": "Bob",
                    "content": "Earlier post",
                    "created_at": "2024-01-01T09:00:00+00:00",
                    "created_at_label": "2024-01-01 09:00 UTC",
                }
            )

        response = self.client.post(
            "/posts",
            data={"author": "Carol", "content": "Latest post"},
            follow_redirects=True,
        )

        page = response.get_data(as_text=True)
        self.assertLess(page.index("Latest post"), page.index("Earlier post"))

    def test_post_submission_rejects_values_longer_than_form_limits(self):
        response = self.client.post(
            "/posts",
            data={"author": "A" * 41, "content": "B" * 281},
            follow_redirects=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(("A" * 41).encode(), response.data)

        with TinyDB(self.db_path) as db:
            self.assertEqual(db.all(), [])

    def test_feed_handles_posts_without_created_at(self):
        with TinyDB(self.db_path) as db:
            db.insert({"author": "Legacy", "content": "Older schema"})

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Legacy", response.data)
        self.assertIn(b"Unknown time", response.data)


if __name__ == "__main__":
    unittest.main()
