import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate(request, selection):
    page = request.args.get('page', 1 , type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    items = [item.format() for item in selection]
    paginated = items[start:end]
    return paginated

def formatCategories(categories):
    body = {}
    for category in categories:
            body[category.id] = category.type
    return body

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers 
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
        return response

    @app.route("/categories", methods=["GET"])
    def get_categories():
        categories = Category.query.order_by(Category.id).all()
        body = formatCategories(categories)
        return jsonify(
            {
                "categories": body
            }
        )

    @app.route("/questions", methods=["GET"])
    def get_questions():
        questions = Question.query.order_by(Question.id).all()
        categories = Category.query.order_by(Category.id).all()
        categoriesResult = formatCategories(categories)
        paginated = paginate(request, questions)
        allQuestions = Question.query.all()
        result = jsonify(
            {
                "categories": categoriesResult,
                "questions": paginated,
                "total_questions": len(allQuestions),
                "current_category": "History"
            }
        )
        return result

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id):
        question = Question.query.filter(Question.id == question_id).one_or_none()

        if question is None:
            abort(404)

        question.delete()
            
        return jsonify({
                "success": True,
                "action": "Delete"
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):
        questions = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
        selected_category = Category.query.filter(Category.id == category_id).one_or_none()
        allQuestions = Question.query.all()
        result = jsonify(
            {
                "questions": [question.format() for question in questions],
                "total_questions": len(allQuestions),
                "current_category": selected_category.type
            }
        )
        return result

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    
    @app.route("/")
    def hello():
        return jsonify({"message": "Hello world"})

    return app

app = create_app()

if __name__ == '__main__':
    app.init_db()
    app.run(debug=True)