# quiz_app.py (Chỉ thay đổi phần đầu)

import tkinter as tk
from tkinter import messagebox
from question import get_questions_from_db # Thay đổi import

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ứng dụng đố vui Python")
        self.root.geometry("400x300")

        self.score = 0
        self.question_index = 0
        self.user_answer = tk.StringVar(value="")

        # Lấy câu hỏi từ cơ sở dữ liệu
        self.questions = get_questions_from_db() 
        
        self.create_widgets()
        self.show_question()

    # ... (Các phần còn lại của class QuizApp không đổi) ...
    def create_widgets(self):
        """Tạo các thành phần giao diện người dùng."""
        self.question_label = tk.Label(self.root, text="", wraplength=350, font=("Helvetica", 14))
        self.question_label.pack(pady=20)

        self.option_frame = tk.Frame(self.root)
        self.option_frame.pack()

        # Tạo các Radiobutton cho các lựa chọn
        self.radio_buttons = []
        for i in range(3):
            rb = tk.Radiobutton(self.option_frame, 
                                text="", 
                                variable=self.user_answer, 
                                value=chr(ord('A') + i))
            rb.pack(anchor="w")
            self.radio_buttons.append(rb)
        
        self.submit_button = tk.Button(self.root, text="Trả lời", command=self.check_answer)
        self.submit_button.pack(pady=20)
    
    def show_question(self):
        """Hiển thị câu hỏi hiện tại."""
        if self.question_index < len(self.questions): # Sử dụng self.questions
            current_question = self.questions[self.question_index]
            self.question_label.config(text=current_question.prompt)
            
            # Cập nhật text cho các Radiobutton
            for i, option_text in enumerate(current_question.options):
                self.radio_buttons[i].config(text=option_text, value=chr(ord('A') + i))
            
            # Reset lựa chọn người dùng
            self.user_answer.set("")
        else:
            self.show_final_score()

    def check_answer(self):
        """Kiểm tra câu trả lời của người dùng và cập nhật điểm."""
        if not self.user_answer.get():
            messagebox.showwarning("Lỗi", "Vui lòng chọn một đáp án!")
            return

        current_question = self.questions[self.question_index] # Sử dụng self.questions
        if self.user_answer.get() == current_question.answer:
            self.score += 1
            messagebox.showinfo("Kết quả", "Chính xác!")
        else:
            messagebox.showinfo("Kết quả", f"Sai rồi. Đáp án đúng là {current_question.answer}.")
        
        self.question_index += 1
        self.show_question()
    
    def show_final_score(self):
        """Hiển thị điểm số cuối cùng và kết thúc ứng dụng."""
        self.question_label.pack_forget()
        self.option_frame.pack_forget()
        self.submit_button.pack_forget()
        
        final_message = f"Hoàn thành!\nBạn đã trả lời đúng {self.score} trên tổng số {len(self.questions)} câu."
        final_label = tk.Label(self.root, text=final_message, font=("Helvetica", 16))
        final_label.pack(pady=50)

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()