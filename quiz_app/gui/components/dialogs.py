"""Dialog components for the GUI."""
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from typing import Optional, List, Dict, Any, Tuple, Callable
from ...models.question import Question

class LoginDialog:
    """Login dialog for admin authentication."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[Tuple[str, str]]:
        """
        Show login dialog.
        
        Returns:
            Tuple of (username, password) if successful, None if cancelled
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Đăng nhập Admin")
        self.dialog.geometry("300x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"300x200+{x}+{y}")
        
        # Create widgets
        self._create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Title
        title_label = tk.Label(self.dialog, text="Đăng nhập quản trị", font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        # Username
        tk.Label(self.dialog, text="Tên đăng nhập:").pack()
        self.username_entry = tk.Entry(self.dialog, width=25)
        self.username_entry.pack(pady=5)
        self.username_entry.focus()
        
        # Password
        tk.Label(self.dialog, text="Mật khẩu:").pack()
        self.password_entry = tk.Entry(self.dialog, width=25, show="*")
        self.password_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        login_btn = tk.Button(button_frame, text="Đăng nhập", command=self._on_login)
        login_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Hủy", command=self._on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self._on_login())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _on_login(self):
        """Handle login button click."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return
        
        self.result = (username, password)
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()

class QuestionDialog:
    """Dialog for creating/editing questions."""
    
    def __init__(self, parent, question: Optional[Question] = None, categories: List[str] = None):
        self.parent = parent
        self.question = question
        self.categories = categories or ["General", "Python", "Programming", "Math"]
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[Question]:
        """
        Show question dialog.
        
        Returns:
            Question object if successful, None if cancelled
        """
        self.dialog = tk.Toplevel(self.parent)
        title = "Chỉnh sửa câu hỏi" if self.question else "Thêm câu hỏi mới"
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"600x500+{x}+{y}")
        
        # Create widgets
        self._create_widgets()
        
        # Populate fields if editing
        if self.question:
            self._populate_fields()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame with scrollbar
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Question prompt
        tk.Label(main_frame, text="Câu hỏi:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.prompt_text = tk.Text(main_frame, height=4, wrap=tk.WORD)
        self.prompt_text.pack(fill=tk.X, pady=(0, 10))
        
        # Options frame
        options_frame = tk.LabelFrame(main_frame, text="Lựa chọn", font=("Arial", 10, "bold"))
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.option_entries = []
        for i, label in enumerate(["A", "B", "C"]):
            tk.Label(options_frame, text=f"Lựa chọn {label}:").pack(anchor=tk.W)
            entry = tk.Entry(options_frame, width=60)
            entry.pack(fill=tk.X, padx=5, pady=(0, 5))
            self.option_entries.append(entry)
        
        # Answer frame
        answer_frame = tk.Frame(main_frame)
        answer_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(answer_frame, text="Đáp án đúng:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        self.answer_var = tk.StringVar(value="A")
        for answer in ["A", "B", "C"]:
            tk.Radiobutton(answer_frame, text=answer, variable=self.answer_var, value=answer).pack(side=tk.LEFT, padx=5)
        
        # Category and difficulty frame
        meta_frame = tk.Frame(main_frame)
        meta_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Category
        tk.Label(meta_frame, text="Danh mục:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(meta_frame, textvariable=self.category_var, values=self.categories, width=15)
        category_combo.pack(side=tk.LEFT, padx=(5, 20))
        category_combo.set("General")
        
        # Difficulty
        tk.Label(meta_frame, text="Độ khó:").pack(side=tk.LEFT)
        self.difficulty_var = tk.StringVar()
        difficulty_combo = ttk.Combobox(meta_frame, textvariable=self.difficulty_var, 
                                       values=["Easy", "Medium", "Hard"], width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=5)
        difficulty_combo.set("Medium")
        
        # Tags
        tk.Label(main_frame, text="Tags (phân cách bằng dấu phẩy):", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.tags_entry = tk.Entry(main_frame, width=60)
        self.tags_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        save_btn = tk.Button(button_frame, text="Lưu", command=self._on_save, bg="#4CAF50", fg="white")
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Hủy", command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        preview_btn = tk.Button(button_frame, text="Xem trước", command=self._on_preview)
        preview_btn.pack(side=tk.LEFT)
    
    def _populate_fields(self):
        """Populate fields with existing question data."""
        if not self.question:
            return
        
        # Prompt
        self.prompt_text.delete(1.0, tk.END)
        self.prompt_text.insert(1.0, self.question.prompt)
        
        # Options
        options = [self.question.option_a, self.question.option_b, self.question.option_c]
        for i, option in enumerate(options):
            self.option_entries[i].delete(0, tk.END)
            self.option_entries[i].insert(0, option)
        
        # Answer
        self.answer_var.set(self.question.answer)
        
        # Category and difficulty
        self.category_var.set(self.question.category)
        self.difficulty_var.set(self.question.difficulty)
        
        # Tags
        if self.question.tags:
            self.tags_entry.delete(0, tk.END)
            self.tags_entry.insert(0, ", ".join(self.question.tags))
    
    def _on_save(self):
        """Handle save button click."""
        # Validate inputs
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showerror("Lỗi", "Vui lòng nhập câu hỏi!")
            return
        
        options = [entry.get().strip() for entry in self.option_entries]
        if not all(options):
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ các lựa chọn!")
            return
        
        # Create/update question
        if self.question:
            # Update existing question
            self.question.prompt = prompt
            self.question.option_a = options[0]
            self.question.option_b = options[1]
            self.question.option_c = options[2]
            self.question.answer = self.answer_var.get()
            self.question.category = self.category_var.get() or "General"
            self.question.difficulty = self.difficulty_var.get() or "Medium"
            
            # Parse tags
            tags_text = self.tags_entry.get().strip()
            self.question.tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()] if tags_text else []
            
            self.result = self.question
        else:
            # Create new question
            tags_text = self.tags_entry.get().strip()
            tags = [tag.strip() for tag in tags_text.split(",") if tag.strip()] if tags_text else []
            
            self.result = Question(
                prompt=prompt,
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                answer=self.answer_var.get(),
                category=self.category_var.get() or "General",
                difficulty=self.difficulty_var.get() or "Medium",
                tags=tags
            )
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def _on_preview(self):
        """Show preview of the question."""
        prompt = self.prompt_text.get(1.0, tk.END).strip()
        options = [entry.get().strip() for entry in self.option_entries]
        answer = self.answer_var.get()
        
        if not prompt or not all(options):
            messagebox.showwarning("Lỗi", "Vui lòng điền đầy đủ thông tin để xem trước!")
            return
        
        preview_text = f"Câu hỏi: {prompt}\n\n"
        for i, option in enumerate(options):
            preview_text += f"{chr(65+i)}. {option}\n"
        preview_text += f"\nĐáp án đúng: {answer}"
        
        messagebox.showinfo("Xem trước câu hỏi", preview_text)

class ConfirmDialog:
    """Custom confirmation dialog."""
    
    @staticmethod
    def show(parent, title: str, message: str, icon: str = "question") -> bool:
        """
        Show confirmation dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
            message: Dialog message
            icon: Dialog icon
            
        Returns:
            True if user clicked Yes, False otherwise
        """
        return messagebox.askyesno(title, message, icon=icon, parent=parent)

class ProgressDialog:
    """Progress dialog for long operations."""
    
    def __init__(self, parent, title: str, message: str):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x120")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (120 // 2)
        self.dialog.geometry(f"400x120+{x}+{y}")
        
        # Message
        self.message_label = tk.Label(self.dialog, text=message, font=("Arial", 10))
        self.message_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.dialog, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=20, pady=10)
        self.progress.start()
        
        # Update dialog
        self.dialog.update()
    
    def update_message(self, message: str):
        """Update progress message."""
        self.message_label.config(text=message)
        self.dialog.update()
    
    def close(self):
        """Close progress dialog."""
        self.progress.stop()
        self.dialog.destroy()

class SearchDialog:
    """Advanced search dialog."""
    
    def __init__(self, parent, categories: List[str]):
        self.parent = parent
        self.categories = categories
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[Dict[str, Any]]:
        """
        Show search dialog.
        
        Returns:
            Search criteria dict if successful, None if cancelled
        """
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Tìm kiếm nâng cao")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (300 // 2)
        self.dialog.geometry(f"400x300+{x}+{y}")
        
        # Create widgets
        self._create_widgets()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create search dialog widgets."""
        main_frame = tk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Search term
        tk.Label(main_frame, text="Từ khóa tìm kiếm:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.search_entry = tk.Entry(main_frame, width=40)
        self.search_entry.pack(fill=tk.X, pady=(0, 10))
        self.search_entry.focus()
        
        # Category
        tk.Label(main_frame, text="Danh mục:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.category_var = tk.StringVar()
        category_combo = ttk.Combobox(main_frame, textvariable=self.category_var, 
                                     values=["Tất cả"] + self.categories, state="readonly")
        category_combo.pack(fill=tk.X, pady=(0, 10))
        category_combo.set("Tất cả")
        
        # Difficulty
        tk.Label(main_frame, text="Độ khó:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        self.difficulty_var = tk.StringVar()
        difficulty_combo = ttk.Combobox(main_frame, textvariable=self.difficulty_var,
                                       values=["Tất cả", "Easy", "Medium", "Hard"], state="readonly")
        difficulty_combo.pack(fill=tk.X, pady=(0, 20))
        difficulty_combo.set("Tất cả")
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        search_btn = tk.Button(button_frame, text="Tìm kiếm", command=self._on_search, bg="#2196F3", fg="white")
        search_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Hủy", command=self._on_cancel)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = tk.Button(button_frame, text="Xóa", command=self._on_clear)
        clear_btn.pack(side=tk.LEFT)
        
        # Bind Enter key
        self.dialog.bind('<Return>', lambda e: self._on_search())
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
    
    def _on_search(self):
        """Handle search button click."""
        search_term = self.search_entry.get().strip()
        category = self.category_var.get()
        difficulty = self.difficulty_var.get()
        
        self.result = {
            'search_term': search_term,
            'category': category if category != "Tất cả" else None,
            'difficulty': difficulty if difficulty != "Tất cả" else None
        }
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def _on_clear(self):
        """Clear all search fields."""
        self.search_entry.delete(0, tk.END)
        self.category_var.set("Tất cả")
        self.difficulty_var.set("Tất cả")