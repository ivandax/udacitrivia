import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format('postgres@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
        self.search = {"searchTerm": "what"}
        self.newQuestion = {"question":"test999", "category":4, "difficulty":2, "answer":"tesla"}
        self.newQuestionWrong = {}
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        res = self.client().get("/categories")
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["categories"])

    def test_get_questions(self):
        res = self.client().get("/questions")
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])

    def test_get_questions_by_correct_page(self):
        res = self.client().get("/questions?page=1")
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["questions"])

    def test_get_questions_empty(self):
        res = self.client().get("/questions?page=1000")
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 0)

    def test_failure(self):
        res = self.client().get("/questionsx")
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_delete_question_success(self):
        before = Question.query.count()
        res = self.client().delete("/questions/9")
        after = Question.query.count()
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 204)
        self.assertEqual(before - 1, after)

    def test_delete_question_failure(self):
        res = self.client().delete("/questions/TTTT")
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_post_question_search(self):
        res = self.client().post("/questions", json=self.search)
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_post_question_new(self):
        res = self.client().post("/questions", json=self.newQuestion)
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_post_question_new_failure(self):
        res = self.client().post("/questions/5", json=self.newQuestionWrong)
        data =json.loads(res.data)
        self.assertEqual(res.status_code, 405)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()