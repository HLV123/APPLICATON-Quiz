"""Quiz taking window with timer and scoring."""
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Optional, Dict, Any
import time
from threading import Timer
from ..models.question import Question
from ..services.quiz_service import QuizService
from ..utils.logger import Logger
from ..config.settings import Config

class QuizWindow:
    """Quiz taking window class."""
    
    def __init__(self, parent: tk.Tk, questions: List[Question], quiz_service: QuizService):
        """
        Initialize quiz window.
        
        Args:
            parent: Parent window
            questions: List of quiz questions
            quiz_service: Quiz service instance
        """
        self.parent = parent
        self.questions = questions
        self.quiz_service = quiz_service
        self.logger = Logger(__name__)
        
        # Load timer settings
        self.show_timer = Config.SHOW_TIMER
        self.auto_submit = Config.AUTO_SUBMIT
        self.total_time_limit = Config.TOTAL_QUIZ_TIME
        
        # Quiz state
        self.current_question_index = 0
        self.user_answers = []
        self.start_time = time.time()
        self.timer = None
        self.time_remaining = self.total_time_limit
        self.quiz_completed = False
        
        # Create window
        self._create_window()
        self._create_widgets()  # PHƯƠNG THỨC NÀY PHẢI CÓ
        self._load_question()
        
        if self.show_timer:
            self._start_timer()
        
        self.logger.info(f"Quiz started: {len(questions)} questions, time limit: {self.total_time_limit}s")
    
    def _create_window(self):
        """Create and configure quiz window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("🎯 Quiz - Đang làm bài")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.window.winfo_screenheight() // 2) - (600 // 2)
        self.window.geometry(f"800x600+{x}+{y}")
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_window_close)
        
        # Configure grid
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
    
    def _create_widgets(self):  # PHƯƠNG THỨC NÀY BỊ THIẾU
        """Create and layout widgets."""
        # Header with progress and timer
        self._create_header()
        
        # Question display area
        self._create_question_area()
        
        # Options area
        self._create_options_area()
        
        # Navigation buttons
        self._create_navigation()
    
    def _create_header(self):
        """Create header with progress and timer."""
        header_frame = tk.Frame(self.window, bg='#2196F3', height=80)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Progress info
        self.progress_label = tk.Label(
            header_frame,
            text="",
            font=("Arial", 14, "bold"),
            bg='#2196F3',
            fg='white'
        )
        self.progress_label.grid(row=0, column=0, padx=20, pady=20, sticky='w')
        
        # Progress bar
        progress_container = tk.Frame(header_frame, bg='#2196F3')
        progress_container.grid(row=0, column=1, padx=20, pady=20, sticky='ew')
        
        self.progress_bar = ttk.Progressbar(
            progress_container,
            mode='determinate',
            length=300
        )
        self.progress_bar.pack(side=tk.TOP, pady=(0, 5))
        
        self.progress_text = tk.Label(
            progress_container,
            text="",
            font=("Arial", 10),
            bg='#2196F3',
            fg='white'
        )
        self.progress_text.pack()
        
        # Timer (only show if enabled)
        if self.show_timer:
            timer_frame = tk.Frame(header_frame, bg='#FF5722', relief='solid', bd=2)
            timer_frame.grid(row=0, column=2, padx=20, pady=20)
            
            tk.Label(
                timer_frame,
                text="⏰ Thời gian còn lại",
                font=("Arial", 10),
                bg='#FF5722',
                fg='white'
            ).pack(pady=(5, 0))
            
            self.timer_label = tk.Label(
                timer_frame,
                text="",
                font=("Arial", 16, "bold"),
                bg='#FF5722',
                fg='white'
            )
            self.timer_label.pack(pady=(0, 5))
            
            # Initial timer display
            self._update_timer_display()
    
    def _create_question_area(self):
        """Create question display area."""
        question_frame = tk.Frame(self.window, bg='#f5f5f5', relief='solid', bd=1)
        question_frame.grid(row=1, column=0, sticky='ew', padx=20, pady=(20, 10))
        question_frame.grid_columnconfigure(0, weight=1)
        
        # Question label
        tk.Label(
            question_frame,
            text="📝 Câu hỏi:",
            font=("Arial", 12, "bold"),
            bg='#f5f5f5',
            anchor='w'
        ).grid(row=0, column=0, sticky='ew', padx=15, pady=(15, 5))
        
        # Question text
        self.question_label = tk.Label(
            question_frame,
            text="",
            font=("Arial", 14),
            bg='#f5f5f5',
            wraplength=750,
            justify=tk.LEFT,
            anchor='w'
        )
        self.question_label.grid(row=1, column=0, sticky='ew', padx=15, pady=(5, 15))
    
    def _create_options_area(self):
        """Create options selection area."""
        options_frame = tk.Frame(self.window, bg='white', relief='solid', bd=1)
        options_frame.grid(row=2, column=0, sticky='nsew', padx=20, pady=(0, 10))
        options_frame.grid_columnconfigure(0, weight=1)
        
        # Options label
        tk.Label(
            options_frame,
            text="🎯 Chọn đáp án:",
            font=("Arial", 12, "bold"),
            bg='white',
            anchor='w'
        ).grid(row=0, column=0, sticky='ew', padx=15, pady=(15, 10))
        
        # Answer variable
        self.answer_var = tk.StringVar(value="")
        
        # Option buttons
        self.option_buttons = []
        for i in range(3):
            btn_frame = tk.Frame(options_frame, bg='white')
            btn_frame.grid(row=i+1, column=0, sticky='ew', padx=15, pady=5)
            btn_frame.grid_columnconfigure(1, weight=1)
            
            # Radio button
            radio = tk.Radiobutton(
                btn_frame,
                variable=self.answer_var,
                value=chr(65 + i),  # A, B, C
                font=("Arial", 12),
                bg='white',
                activebackground='#e3f2fd'
            )
            radio.grid(row=0, column=0, sticky='w')
            
            # Option text
            option_label = tk.Label(
                btn_frame,
                text="",
                font=("Arial", 12),
                bg='white',
                anchor='w',
                wraplength=650,
                justify=tk.LEFT
            )
            option_label.grid(row=0, column=1, sticky='ew', padx=(5, 0))
            
            self.option_buttons.append((radio, option_label))
    
    def _create_navigation(self):
        """Create navigation buttons."""
        nav_frame = tk.Frame(self.window, bg='#f5f5f5')
        nav_frame.grid(row=3, column=0, sticky='ew', padx=20, pady=20)
        nav_frame.grid_columnconfigure(1, weight=1)
        
        # Previous button
        self.prev_btn = tk.Button(
            nav_frame,
            text="⬅️ Câu trước",
            font=("Arial", 11),
            bg='#757575',
            fg='white',
            padx=20,
            pady=8,
            state=tk.DISABLED,
            command=self._previous_question
        )
        self.prev_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Question info
        self.nav_info_label = tk.Label(
            nav_frame,
            text="",
            font=("Arial", 11),
            bg='#f5f5f5'
        )
        self.nav_info_label.grid(row=0, column=1)
        
        # Next/Submit button
        self.next_btn = tk.Button(
            nav_frame,
            text="Câu tiếp ➡️",
            font=("Arial", 11),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=8,
            command=self._next_question
        )
        self.next_btn.grid(row=0, column=2, padx=(10, 0))
    
    def _update_timer_display(self):
        """Update timer display format MM:SS."""
        if not self.show_timer:
            return
        
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        # Change color based on remaining time percentage
        total_percentage = (self.time_remaining / self.total_time_limit) * 100
        
        if total_percentage <= 10:  # Less than 10% time left
            self.timer_label.master.config(bg='#F44336')  # Red
            self.timer_label.config(bg='#F44336')
        elif total_percentage <= 25:  # Less than 25% time left
            self.timer_label.master.config(bg='#FF9800')  # Orange
            self.timer_label.config(bg='#FF9800')
        else:
            self.timer_label.master.config(bg='#FF5722')  # Default
            self.timer_label.config(bg='#FF5722')
    
    def _start_timer(self):
        """Start quiz timer."""
        if not self.show_timer:
            return
        
        self._stop_timer()
        self._update_timer()
    
    def _stop_timer(self):
        """Stop current timer."""
        if self.timer:
            self.timer.cancel()
            self.timer = None
    
    def _update_timer(self):
        """Update timer and handle timeout."""
        if self.quiz_completed or not self.show_timer:
            return
        
        # Update display
        self._update_timer_display()
        
        if self.time_remaining <= 0:
            # Time's up for entire quiz
            if self.auto_submit:
                messagebox.showwarning(
                    "Hết giờ!", 
                    "Thời gian làm bài đã hết.\nBài thi sẽ được nộp tự động."
                )
                self._finish_quiz()
            else:
                messagebox.showwarning(
                    "Hết giờ!", 
                    "Thời gian làm bài đã hết!"
                )
                self.quiz_completed = True
        else:
            # Schedule next update
            self.time_remaining -= 1
            self.timer = Timer(1.0, self._update_timer)
            self.timer.daemon = True
            self.timer.start()
    
    def _load_question(self):
        """Load current question into the interface."""
        if self.current_question_index >= len(self.questions):
            self._finish_quiz()
            return
        
        question = self.questions[self.current_question_index]
        
        # Update question text
        self.question_label.config(text=question.prompt)
        
        # Update options
        options = [question.option_a, question.option_b, question.option_c]
        for i, (radio, label) in enumerate(self.option_buttons):
            label.config(text=f"{chr(65 + i)}. {options[i]}")
            radio.config(text="", value=chr(65 + i))
        
        # Update progress
        self._update_progress()
        
        # Update navigation
        self._update_navigation()
        
        # Clear previous answer
        self.answer_var.set("")
        
        # Load previous answer if exists
        if self.current_question_index < len(self.user_answers):
            self.answer_var.set(self.user_answers[self.current_question_index])
    
    def _update_progress(self):
        """Update progress indicators."""
        current = self.current_question_index + 1
        total = len(self.questions)
        
        # Progress label
        self.progress_label.config(text=f"Câu {current}/{total}")
        
        # Progress bar
        progress_percent = (current / total) * 100
        self.progress_bar['value'] = progress_percent
        
        # Progress text
        self.progress_text.config(text=f"{current}/{total} câu hỏi")
    
    def _update_navigation(self):
        """Update navigation button states."""
        # Previous button
        if self.current_question_index > 0:
            self.prev_btn.config(state=tk.NORMAL)
        else:
            self.prev_btn.config(state=tk.DISABLED)
        
        # Next/Submit button
        if self.current_question_index == len(self.questions) - 1:
            self.next_btn.config(text="📝 Hoàn thành", bg='#FF5722')
        else:
            self.next_btn.config(text="Câu tiếp ➡️", bg='#4CAF50')
        
        # Navigation info
        answered = len([a for a in self.user_answers if a])
        self.nav_info_label.config(text=f"Đã trả lời: {answered}/{len(self.questions)}")
    
    def _save_current_answer(self):
        """Save current answer to user_answers list."""
        # Extend list if necessary
        while len(self.user_answers) <= self.current_question_index:
            self.user_answers.append("")
        
        # Save current answer
        self.user_answers[self.current_question_index] = self.answer_var.get()
    
    def _previous_question(self):
        """Go to previous question."""
        if self.current_question_index > 0:
            self._save_current_answer()
            self.current_question_index -= 1
            self._load_question()
    
    def _next_question(self):
        """Go to next question or finish quiz."""
        # Save current answer
        self._save_current_answer()
        
        if self.current_question_index == len(self.questions) - 1:
            # Last question - finish quiz
            self._finish_quiz()
        else:
            # Move to next question
            self.current_question_index += 1
            self._load_question()
    
    def _finish_quiz(self):
        """Finish quiz and show results."""
        try:
            self.quiz_completed = True
        
            # Stop timer
            if self.timer:
                self.timer.cancel()
        
            # Calculate time taken
            total_time = int(time.time() - self.start_time)
        
            # Ensure all answers are saved
            while len(self.user_answers) < len(self.questions):
                self.user_answers.append("")
        
            # Calculate score
            score, correct_results = self.quiz_service.calculate_score(self.questions, self.user_answers)
        
            # Generate detailed report (vẫn giữ để lưu vào database)
            report = self.quiz_service.generate_quiz_report(
                self.questions, self.user_answers, correct_results, total_time
            )
        
            # Save result
            question_ids = [q.id for q in self.questions if q.id]
            self.quiz_service.save_quiz_result(None, score, len(self.questions), total_time, question_ids)
        
            # Hiển thị thông báo thành công thay vì show results window
            percentage = (score / len(self.questions) * 100) if len(self.questions) > 0 else 0
        
            message = f"🎯 Quiz đã hoàn thành!\n\n"
            message += f"Điểm số: {score}/{len(self.questions)}\n"
            message += f"Tỷ lệ đúng: {percentage:.1f}%\n"
            message += f"Thời gian: {total_time} giây"
        
            messagebox.showinfo("Hoàn thành Quiz", message)
        
            self.logger.info(f"Quiz completed: {score}/{len(self.questions)} in {total_time}s")
        
            # Đóng quiz window
            self.window.destroy()
        
        except Exception as e:
            self.logger.error(f"Error finishing quiz: {e}")
            messagebox.showerror("Lỗi", f"Không thể hoàn thành quiz:\n{str(e)}")
    

    def _on_window_close(self):
        """Handle window close event."""
        if self.quiz_completed:
            self.window.destroy()
            return
        
        # Confirm exit if quiz not completed
        if messagebox.askyesno(
            "Xác nhận thoát", 
            "Bạn có chắc chắn muốn thoát? Tiến trình quiz sẽ bị mất!",
            icon='warning'
        ):
            if self.timer:
                self.timer.cancel()
            self.window.destroy()


