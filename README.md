# 🧠 Quiz System - Client-Server E-Learning Platform

A Python-based client-server quiz application with MySQL integration, enabling users to take quizzes, submit scores, and manage questions in real-time. Supports concurrent users via multiprocessing and semaphore-based database access control.

---

## 📁 Project Structure

```
quiz_system/
├── quiz_server.py    # Server handling client connections and DB operations
├── quiz_client.py    # Client for attempting quizzes
├── quiz_admin.py     # Admin interface for adding/removing questions
```

---

## 🛠️ Technologies Used

- **Python 3**
- **Sockets** for client-server communication
- **MySQL** with connection pooling
- **Multiprocessing** with semaphores
- **JSON** for data exchange

---

## 🔌 Setup Instructions

### ✅ Prerequisites

- Python 3.6+
- MySQL Server
- Required Python packages:
  ```bash
  pip install mysql-connector-python
  ```

- MySQL Database setup:
  ```sql
  CREATE DATABASE quiz_db;
  CREATE USER 'quiz_user'@'localhost' IDENTIFIED BY 'Danger@123';
  GRANT ALL PRIVILEGES ON quiz_db.* TO 'quiz_user'@'localhost';

  CREATE TABLE questions (
      id INT AUTO_INCREMENT PRIMARY KEY,
      content TEXT,
      options JSON,
      correct_answer INT,
      topic VARCHAR(100),
      created_at DATETIME
  );

  CREATE TABLE leaderboard (
      id INT AUTO_INCREMENT PRIMARY KEY,
      username VARCHAR(50) UNIQUE,
      score INT
  );
  ```

---

## 🚀 How to Run

### 1. Start the Server
```bash
python3 quiz_server.py
```

### 2. Run the Client
```bash
python3 quiz_client.py
```

### 3. Admin Example (Add Question)
```bash
python3 quiz_admin.py
```

---

## 🧪 Sample Use

- User connects and chooses a quiz topic.
- Server fetches topic-specific questions.
- User answers multiple choice questions.
- Final score is updated in the leaderboard.

---

## 👤 Author

Vagisha Sharma

---

