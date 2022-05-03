import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
import sys

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
    app.config['CORS_HEADERS'] = 'Content-Type'
    setup_db(app)
    cors = CORS(app)

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

    @app.route("/questions", methods=["POST"])
    # @cross_origin
    def questions():
        body = request.get_json()
        search = body.get("searchTerm", None)
        if search is None:
            question = body.get("question", None)
            category = body.get("category", None)
            difficulty = body.get("difficulty", None)
            answer = body.get("answer", None)
            try:
                newQuestion = Question(question=question, category=category, difficulty=difficulty, answer=answer)
                newQuestion.insert()
                return jsonify({
                    "success": True
                })
            except:
                print(sys.exc_info())
                abort(404)
        else:
            questions = Question.query.filter(Question.question.ilike(f'%{search}%'))
            formatted = [q.format() for q in questions]
            return jsonify({
                "total_questions": len(formatted),
                "current_category": "Entertainment",
                "questions": formatted
            }
        )

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

    @app.route("/quizzes", methods=["POST"])
    def quizzes():
        body = request.get_json()
        previousList = body.get("previous_questions", None)
        category = body.get("quiz_category", None)
        try:
            questions = Question.query.filter(Question.category == category["id"], Question.id.notin_(previousList)).all()
            question = random.choice(questions)
            return jsonify({
                "question": question.format()
            })
        except:
            print(sys.exc_info())
            abort(404)

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

    return app

app = create_app()

if __name__ == '__main__':
    app.init_db()
    app.run(debug=True)