import socket
import json

class QuizClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect(('localhost', 5555))
        except ConnectionError as e:
            print(f"Connection failed: {e}")
            exit(1)

    def _show_error(self, message):
        print("\n" + "!" * 50)
        print("SERVER NOTIFICATION:")
        print(message)
        print("!" * 50 + "\n")

    def take_quiz(self):
        username = input("Enter your username: ").strip()
        selected_topic = "General Knowledge"

        # Request questions
        self.sock.send(f"GET_QUESTIONS:{selected_topic}".encode())
        response = self.sock.recv(4096).decode()

        if response.startswith("DB_BUSY"):
            self._show_error(response.split(":", 1)[1])
            return
        elif response.startswith("DB_ERROR"):
            self._show_error(f"Database error: {response.split(':', 1)[1]}")
            return

        try:
            questions = json.loads(response)
        except json.JSONDecodeError:
            self._show_error("Invalid response from server")
            return

        if not questions:
            print("No questions available for this topic.")
            return

        score = 0
        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}: {q['content']}")
            options = json.loads(q['options'])
            for j, option in enumerate(options, 1):
                print(f"{j}. {option}")

            while True:
                try:
                    answer = int(input("Your choice (1-3): "))
                    if 1 <= answer <= 3:
                        break
                    print("Please enter 1, 2, or 3")
                except ValueError:
                    print("Please enter a number")

            if answer == q['correct_answer']:
                score += 10
                print("✓ Correct!")
            else:
                print(f"✗ Wrong! Correct answer was {q['correct_answer']}")

        # Send score
        self.sock.send(f"UPDATE_SCORE:{username}:{score}".encode())
        reply = self.sock.recv(1024).decode()
        
        if reply.startswith("SCORE_UPDATED"):
            print(f"\nYour final score: {score}/{(i)*10}")
            print(reply.split(":", 1)[1])
        else:
            self._show_error(reply)

if __name__ == "__main__":
    print("Quiz Client Starting...")
    client = QuizClient()
    client.take_quiz()
