# question.py

import sqlite3

def get_questions_from_db():
    """
    Kết nối tới cơ sở dữ liệu và lấy tất cả các câu hỏi.
    
    Returns:
        list: Danh sách các đối tượng câu hỏi.
    """
    conn = sqlite3.connect('quiz.db')
    cursor = conn.cursor()
    
    # Tạo bảng nếu chưa tồn tại
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    ''')
    conn.commit()
    
    # Thêm dữ liệu mẫu nếu bảng rỗng
    cursor.execute('SELECT COUNT(*) FROM questions')
    if cursor.fetchone()[0] == 0:
        sample_questions = [
            ("Python được phát hành vào năm nào?", "A. 1989", "B. 1991", "C. 1995", "B"),
            ("Ai là cha đẻ của Python?", "A. Guido van Rossum", "B. Bill Gates", "C. Linus Torvalds", "A"),
            ("Thư viện nào được sử dụng để làm việc với mảng trong Python?", "A. Pandas", "B. NumPy", "C. Matplotlib", "B"),
        ]
        cursor.executemany('INSERT INTO questions (prompt, option_a, option_b, option_c, answer) VALUES (?, ?, ?, ?, ?)', sample_questions)
        conn.commit()
    
    # Lấy dữ liệu từ bảng questions
    cursor.execute('SELECT * FROM questions')
    raw_questions = cursor.fetchall()
    
    conn.close()
    
    # Chuyển đổi dữ liệu thô thành danh sách các đối tượng Question
    class Question:
        def __init__(self, prompt, options, answer):
            self.prompt = prompt
            self.options = options
            self.answer = answer
    
    questions_list = []
    for row in raw_questions:
        prompt = row[1]
        options = [row[2], row[3], row[4]]
        answer = row[5]
        questions_list.append(Question(prompt, options, answer))
        
    return questions_list