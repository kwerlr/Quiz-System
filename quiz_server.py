import socket
import mysql.connector
import mysql.connector.pooling
import json
import multiprocessing
from multiprocessing import Semaphore
from datetime import datetime
import sys
import time

class QuizServer:
    def __init__(self):
        self.semaphore = Semaphore(1)  # Only one client can access DB at a time
        self.db_pool = self._create_connection_pool()
        
    def _create_connection_pool(self):
        try:
            return mysql.connector.pooling.MySQLConnectionPool(
                pool_name="quiz_pool",
                pool_size=5,
                host='localhost',
                user='quiz_user',
                password='Danger@123',
                database='quiz_db',
                autocommit=True
            )
        except mysql.connector.Error as err:
            print(f"[FATAL] Could not create connection pool: {err}")
            sys.exit(1)

    def _handle_db_operation(self, conn, addr, operation, *args):
        try:
            if not self.semaphore.acquire(block=False):
                conn.sendall(b"DB_BUSY:Database is currently in use. Please try again in a few seconds.")
                print(f"[{datetime.now()}] Client {addr} blocked by semaphore")
                return None
            
            print(f"[{datetime.now()}] Semaphore acquired by {addr}")
            time.sleep(10)
            db_conn = self.db_pool.get_connection()
            cursor = db_conn.cursor(dictionary=True)
            
            try:
                cursor.execute(*args)
                if operation == 'fetch':
                    result = cursor.fetchall()
                    # Convert datetime objects to strings
                    for item in result:
                        if 'created_at' in item and isinstance(item['created_at'], datetime):
                            item['created_at'] = item['created_at'].isoformat()
                else:
                    result = None
                return result
            finally:
                cursor.close()
                db_conn.close()
                
        except mysql.connector.Error as err:
            print(f"[DB ERROR] {err}")
            conn.sendall(f"DB_ERROR:{err}".encode())
            return None
        finally:
            self.semaphore.release()
            print(f"[{datetime.now()}] Semaphore released by {addr}")

    def handle_client(self, conn, addr):
        print(f"[{datetime.now()}] Connected to client: {addr}")
        try:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break

                if data.startswith("GET_QUESTIONS"):
                    topic = data.split(":")[1]
                    print(f"[{datetime.now()}] Client {addr} requested topic: {topic}")
                    
                    questions = self._handle_db_operation(
                        conn, addr, 
                        'fetch', 
                        "SELECT * FROM questions WHERE topic=%s", 
                        (topic,)
                    )
                    
                    if questions is not None:
                        conn.sendall(json.dumps(questions).encode())

                elif data.startswith("UPDATE_SCORE"):
                    _, username, score = data.split(":")
                    print(f"[{datetime.now()}] Updating score for {username}")
                    
                    self._handle_db_operation(
                        conn, addr,
                        'update',
                        """
                        INSERT INTO leaderboard (username, score) 
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE 
                        score = score + VALUES(score)
                        """,
                        (username, int(score))
                    )
                    conn.sendall(b"SCORE_UPDATED:Your score has been recorded")

        except Exception as e:
            print(f"[ERROR] Client {addr} error: {e}")
        finally:
            conn.close()
            print(f"[{datetime.now()}] Client {addr} disconnected")

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            server.bind(('0.0.0.0', 5555))
            server.listen(10)
            print(f"[{datetime.now()}] Server started on port 5555")
            
            while True:
                conn, addr = server.accept()
                process = multiprocessing.Process(
                    target=self.handle_client, 
                    args=(conn, addr),
                    daemon=True
                )
                process.start()
                print(f"[{datetime.now()}] Started client handler PID:{process.pid}")

        except Exception as e:
            print(f"[FATAL] Server error: {e}")
        finally:
            server.close()

if __name__ == "__main__":
    print("Starting Quiz Server...")
    QuizServer().start()
