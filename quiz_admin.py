import mysql.connector
import json
from datetime import datetime

class QuizAdmin:
    def __init__(self):
        self.db = self._connect_db()

    def _connect_db(self):
        try:
            return mysql.connector.connect(
                host='localhost',
                user='quiz_user',
                password='Danger@123',
                database='quiz_db',
                autocommit=True
            )
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            exit(1)

    def add_question(self, content, options, correct, topic):
        try:
            cursor = self.db.cursor()
            cursor.execute(
                """INSERT INTO questions 
                (content, options, correct_answer, topic, created_at)
                VALUES (%s, %s, %s, %s, %s)""",
                (content, json.dumps(options), correct, topic, datetime.now())
            )
            print(f"Added question: {content}")
        except mysql.connector.Error as err:
            print(f"Error adding question: {err}")

    def remove_question(self, qid):
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM questions WHERE id = %s", (qid,))
            print(f"Removed question ID: {qid}")
        except mysql.connector.Error as err:
            print(f"Error removing question: {err}")

if __name__ == "__main__":
    admin = QuizAdmin()
    
    # Example usage:
    admin.add_question(
        "What is Python?",
        ["A snake", "Programming language", "A country"],
        2,
        "Programming"
    )
