"""Main application window."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any
from ..services.quiz_service import QuizService
from ..services.admin_service import AdminService
from ..config.settings import Config
from ..utils.logger import Logger
from .components.dialogs import LoginDialog
from .quiz_window import QuizWindow
from .admin_window import AdminWindow

class MainWindow:
    """Main application window class."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize main window.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.quiz_service = QuizService()
        self.admin_service = AdminService()
        self.logger = Logger(__name__)
        
        # Window setup
        self._setup_window()
        self._create_widgets()
        self._load_initial_data()
        
        self.logger.info("Main window initialized")
    
    def _setup_window(self):
        """Setup window properties."""
        self.root.title("🎯 Quiz Application")
        self.root.configure(bg='#f5f5f5')
        
        # Set minimum size
        self.root.minsize(600, 500)
        
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create and layout widgets."""
        # Header frame
        self._create_header()
        
        # Main content frame
        self._create_main_content()
        
        # Footer frame
        self._create_footer()
    
    def _create_header(self):
        """Create header with title and navigation."""
        header_frame = tk.Frame(self.root, bg='#2196F3', height=80)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # App icon/logo (placeholder)
        icon_label = tk.Label(
            header_frame, 
            text="🎯", 
            font=("Arial", 24),
            bg='#2196F3',
            fg='white'
        )
        icon_label.grid(row=0, column=0, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="Quiz Application",
            font=("Arial", 20, "bold"),
            bg='#2196F3',
            fg='white'
        )
        title_label.grid(row=0, column=1, sticky='w', pady=20)
        
        # Admin button
        admin_btn = tk.Button(
            header_frame,
            text="🔑 Admin Le Van Hung",
            font=("Arial", 10),
            bg='#FF9800',
            fg='white',
            padx=45,
            pady=5,
            cursor='hand2',
            command=self._open_admin_panel
        )
        admin_btn.grid(row=0, column=2, padx=20, pady=20)
    
    def _create_main_content(self):
        """Create main content area."""
        main_frame = tk.Frame(self.root, bg='#f5f5f5')
        main_frame.grid(row=1, column=0, sticky='nsew', padx=20, pady=20)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Welcome section
        self._create_welcome_section(main_frame)
        
        # Quiz configuration section
        self._create_quiz_config_section(main_frame)
        
        # Statistics section
        self._create_statistics_section(main_frame)
    
    def _create_welcome_section(self, parent):
        """Create welcome section."""
        welcome_frame = tk.LabelFrame(
            parent,
            text="🎓 Chào mừng",
            font=("Arial", 12, "bold"),
            bg='#f5f5f5',
            padx=10,
            pady=10
        )
        welcome_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        welcome_text = (
            "Chào mừng bạn đến với ứng dụng Quiz!\n"
            "Hãy cấu hình quiz bên dưới và bắt đầu kiểm tra kiến thức của bạn."
        )
        
        welcome_label = tk.Label(
            welcome_frame,
            text=welcome_text,
            font=("Arial", 11),
            bg='#f5f5f5',
            justify=tk.LEFT
        )
        welcome_label.pack(anchor='w')
    
    def _create_quiz_config_section(self, parent):
        """Create quiz configuration section."""
        config_frame = tk.LabelFrame(
            parent,
            text="⚙️ Cấu hình Quiz",
            font=("Arial", 12, "bold"),
            bg='#f5f5f5',
            padx=15,
            pady=15
        )
        config_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10))
        config_frame.grid_columnconfigure(1, weight=1)
        
        # Number of questions
        tk.Label(
            config_frame,
            text="Số câu hỏi:",
            font=("Arial", 10),
            bg='#f5f5f5'
        ).grid(row=0, column=0, sticky='w', pady=5)
        
        self.questions_var = tk.StringVar(value="5")
        questions_spinbox = tk.Spinbox(
            config_frame,
            from_=1,
            to=20,
            textvariable=self.questions_var,
            width=10,
            font=("Arial", 10)
        )
        questions_spinbox.grid(row=0, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Category selection
        tk.Label(
            config_frame,
            text="Danh mục:",
            font=("Arial", 10),
            bg='#f5f5f5'
        ).grid(row=1, column=0, sticky='w', pady=5)
        
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            config_frame,
            textvariable=self.category_var,
            state="readonly",
            font=("Arial", 10),
            width=20
        )
        self.category_combo.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Difficulty selection
        tk.Label(
            config_frame,
            text="Độ khó:",
            font=("Arial", 10),
            bg='#f5f5f5'
        ).grid(row=2, column=0, sticky='w', pady=5)
        
        self.difficulty_var = tk.StringVar()
        difficulty_combo = ttk.Combobox(
            config_frame,
            textvariable=self.difficulty_var,
            values=["Tất cả", "Easy", "Medium", "Hard"],
            state="readonly",
            font=("Arial", 10),
            width=20
        )
        difficulty_combo.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        difficulty_combo.set("Tất cả")
        
        # Start quiz button
        start_btn = tk.Button(
            config_frame,
            text="🚀 Bắt đầu Quiz",
            font=("Arial", 12, "bold"),
            bg='#4CAF50',
            fg='white',
            padx=30,
            pady=10,
            cursor='hand2',
            command=self._start_quiz
        )
        start_btn.grid(row=3, column=0, columnspan=2, pady=20)
    
    def _create_statistics_section(self, parent):
        """Create statistics section."""
        stats_frame = tk.LabelFrame(
            parent,
            text="📊 Thống kê",
            font=("Arial", 12, "bold"),
            bg='#f5f5f5',
            padx=15,
            pady=15
        )
        stats_frame.grid(row=2, column=0, sticky='nsew')
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
    
        # Statistics cards
        self._create_stat_card(stats_frame, "📝 Tổng câu hỏi", "0", 0, 0)
        self._create_stat_card(stats_frame, "📂 Danh mục", "0", 0, 1)
        self._create_stat_card(stats_frame, "🎯 Quiz đã làm", "0", 0, 2)
    
        self._create_stat_card(stats_frame, "⭐ Điểm trung bình", "0%", 1, 0)
        self._create_stat_card(stats_frame, "🏆 Điểm cao nhất", "0%", 1, 1)
        self._create_stat_card(stats_frame, "📈 Điểm gần nhất", "0%", 1, 2)  # Hiển thị %
    
        # Refresh stats button
        refresh_btn = tk.Button(
            stats_frame,
            text="🔄 Cập nhật",
            font=("Arial", 10),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=5,
            cursor='hand2',
            command=self._refresh_statistics
        )
        refresh_btn.grid(row=2, column=0, columnspan=3, pady=10)
    
    def _create_stat_card(self, parent, title: str, value: str, row: int, col: int):
        """Create a statistics card."""
        card_frame = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='ew')
        
        # Title
        title_label = tk.Label(
            card_frame,
            text=title,
            font=("Arial", 9),
            bg='white',
            fg='#666'
        )
        title_label.pack(pady=(10, 0))
        
        # Value
        value_label = tk.Label(
            card_frame,
            text=value,
            font=("Arial", 16, "bold"),
            bg='white',
            fg='#333'
        )
        value_label.pack(pady=(0, 10))
        
        # Store reference for updating
        setattr(self, f"stat_{row}_{col}_label", value_label)
    
    def _create_footer(self):
        """Create footer with app info."""
        footer_frame = tk.Frame(self.root, bg='#e0e0e0', height=30)
        footer_frame.grid(row=2, column=0, sticky='ew')
        footer_frame.grid_propagate(False)
        
        footer_label = tk.Label(
            footer_frame,
            text="Quiz Application v1.0.0 | Built with Python & Tkinter",
            font=("Arial", 8),
            bg='#e0e0e0',
            fg='#666'
        )
        footer_label.pack(side=tk.LEFT, padx=10, pady=8)
        
        # Question count info
        self.question_count_label = tk.Label(
            footer_frame,
            text="Đang tải...",
            font=("Arial", 8),
            bg='#e0e0e0',
            fg='#666'
        )
        self.question_count_label.pack(side=tk.RIGHT, padx=10, pady=8)
    
    def _load_initial_data(self):
        """Load initial data for the application."""
        try:
            # Load categories
            categories = self.quiz_service.get_available_categories()
            category_values = ["Tất cả"] + categories
            self.category_combo['values'] = category_values
            if category_values:
                self.category_combo.set(category_values[0])
            
            # Update statistics
            self._refresh_statistics()
            
            # Update question count
            self._update_question_count()
            
        except Exception as e:
            self.logger.error(f"Error loading initial data: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu ban đầu:\n{str(e)}")
    
    def _refresh_statistics(self):
        """Refresh statistics display."""
        try:
            # Get quiz statistics
            quiz_stats = self.quiz_service.get_quiz_statistics()
        
            # Get question counts
            question_counts = self.quiz_service.get_question_counts_by_criteria()
        
            # Get latest quiz score
            latest_score = self.quiz_service.get_latest_quiz_score()
        
            # Update statistics cards
            self.stat_0_0_label.config(text=str(question_counts.get('total', 0)))
            self.stat_0_1_label.config(text=str(len(question_counts.get('by_category', {}))))
            self.stat_0_2_label.config(text=str(quiz_stats.get('total_quizzes', 0)))
        
            self.stat_1_0_label.config(text=f"{quiz_stats.get('average_score', 0):.1f}%")
            self.stat_1_1_label.config(text=f"{quiz_stats.get('best_score', 0):.1f}%")
        
            # Update latest score - CHỈ HIỂN THỊ PHẦN TRĂM
            if latest_score['has_result']:
                percentage = latest_score['percentage']
                self.stat_1_2_label.config(text=f"{percentage:.1f}%")
            else:
                self.stat_1_2_label.config(text="0%")
        
            self.logger.debug("Statistics refreshed")
        
        except Exception as e:
            self.logger.error(f"Error refreshing statistics: {e}")
    
    def _update_question_count(self):
        """Update question count in footer."""
        try:
            question_counts = self.quiz_service.get_question_counts_by_criteria()
            total = question_counts.get('total', 0)
            self.question_count_label.config(text=f"Tổng số câu hỏi: {total}")
        except Exception as e:
            self.logger.error(f"Error updating question count: {e}")
            self.question_count_label.config(text="Lỗi tải dữ liệu")
    
    def _start_quiz(self):
        """Start a new quiz with selected configuration."""
        try:
            # Get configuration
            num_questions = int(self.questions_var.get())
            category = self.category_var.get()
            difficulty = self.difficulty_var.get()
            
            # Convert "Tất cả" to None
            if category == "Tất cả":
                category = None
            if difficulty == "Tất cả":
                difficulty = None
            
            # Validate configuration
            is_valid, error_msg = self.quiz_service.validate_quiz_settings(
                num_questions, category, difficulty
            )
            
            if not is_valid:
                messagebox.showerror("Cấu hình không hợp lệ", error_msg)
                return
            
            # Get questions
            questions = self.quiz_service.get_quiz_questions(num_questions, category, difficulty)
            
            if not questions:
                messagebox.showerror("Lỗi", "Không thể tạo quiz. Vui lòng thử lại!")
                return
            
            # Open quiz window
            quiz_window = QuizWindow(self.root, questions, self.quiz_service)
            self.logger.info(f"Quiz started: {len(questions)} questions, category={category}, difficulty={difficulty}")
            
        except ValueError:
            messagebox.showerror("Lỗi", "Số câu hỏi phải là một số nguyên!")
        except Exception as e:
            self.logger.error(f"Error starting quiz: {e}")
            messagebox.showerror("Lỗi", f"Không thể bắt đầu quiz:\n{str(e)}")
    
    def _open_admin_panel(self):
        """Open admin panel with authentication."""
        try:
            # Show login dialog
            login_dialog = LoginDialog(self.root)
            credentials = login_dialog.show()
            
            if not credentials:
                return  # User cancelled
            
            username, password = credentials
            
            # Authenticate
            user = self.admin_service.authenticate_admin(username, password)
            
            if not user:
                messagebox.showerror("Đăng nhập thất bại", "Tên đăng nhập hoặc mật khẩu không đúng!")
                return
            
            # Open admin window - Fix: chỉ truyền 2 tham số
            admin_window = AdminWindow(self.root, user)
            self.logger.info(f"Admin panel opened by {username}")
            
            # Refresh data after admin panel closes
            self.root.after(1000, self._load_initial_data)
            
        except Exception as e:
            self.logger.error(f"Error opening admin panel: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở panel admin:\n{str(e)}")
    
    def refresh_data(self):
        """Public method to refresh all data (called after admin changes)."""
        self._load_initial_data()