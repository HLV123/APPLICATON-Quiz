"""Admin window with full CRUD operations for questions."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Dict, Any
from ..models.question import Question
from ..models.user import User
from ..services.admin_service import AdminService
from ..utils.logger import Logger
from .components.dialogs import QuestionDialog, SearchDialog, ConfirmDialog, ProgressDialog

class AdminWindow:
    """Admin panel window with full CRUD functionality."""
    
    def __init__(self, parent: tk.Tk, user: User):
        """
        Initialize admin window.
        
        Args:
            parent: Parent window
            user: Authenticated admin user
        """
        self.parent = parent
        self.user = user
        self.admin_service = AdminService()
        self.logger = Logger(__name__)
        
        # Window state
        self.questions = []
        self.filtered_questions = []
        self.current_page = 1
        self.items_per_page = 20
        self.total_pages = 1
        self.selected_items = set()
        
        # Create window
        self._create_window()
        self._create_widgets()
        self._load_data()
        
        self.logger.info(f"Admin window opened for user: {user.username}")
    
    def _create_window(self):
        """Create and configure admin window."""
        self.window = tk.Toplevel(self.parent)
        self.window.title("🔒 Admin Panel - Question Management")
        self.window.geometry("1200x800")
        self.window.resizable(True, True)
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.window.winfo_screenheight() // 2) - (800 // 2)
        self.window.geometry(f"1200x800+{x}+{y}")
        
        # Configure grid
        self.window.grid_rowconfigure(2, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Create and layout widgets."""
        # Header with user info and stats
        self._create_header()
        
        # Toolbar with actions
        self._create_toolbar()
        
        # Main content area with questions list
        self._create_main_content()
        
        # Status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create header with admin info and dashboard stats."""
        header_frame = tk.Frame(self.window, bg='#1976D2', height=100)
        header_frame.grid(row=0, column=0, sticky='ew')
        header_frame.grid_propagate(False)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Admin info
        admin_frame = tk.Frame(header_frame, bg='#1976D2')
        admin_frame.grid(row=0, column=0, sticky='w', padx=20, pady=20)
        
        admin_icon = tk.Label(
            admin_frame,
            text="👤",
            font=("Arial", 24),
            bg='#1976D2',
            fg='white'
        )
        admin_icon.pack(side=tk.LEFT, padx=(0, 10))
        
        admin_info = tk.Frame(admin_frame, bg='#1976D2')
        admin_info.pack(side=tk.LEFT)
        
        welcome_label = tk.Label(
            admin_info,
            text=f"Chào mừng, {self.user.username}",
            font=("Arial", 16, "bold"),
            bg='#1976D2',
            fg='white'
        )
        welcome_label.pack(anchor='w')
        
        role_label = tk.Label(
            admin_info,
            text="Quản trị viên | Panel quản lý câu hỏi",
            font=("Arial", 11),
            bg='#1976D2',
            fg='#BBDEFB'
        )
        role_label.pack(anchor='w')
        
        # Dashboard stats
        self.stats_frame = tk.Frame(header_frame, bg='#1976D2')
        self.stats_frame.grid(row=0, column=1, sticky='e', padx=20, pady=20)
        
        # Stats will be loaded later
        self._create_stats_display()
    
    def _create_stats_display(self):
        """Create dashboard statistics display."""
        stats_container = tk.Frame(self.stats_frame, bg='#1976D2')
        stats_container.pack()
        
        # Create stat cards
        self.stat_cards = {}
        stats_data = [
            ("total_questions", "📝 Tổng câu hỏi", "0"),
            ("total_categories", "📂 Danh mục", "0"),
            ("total_quizzes", "🎯 Quiz đã làm", "0")
        ]
        
        for i, (key, label, default_value) in enumerate(stats_data):
            card = tk.Frame(stats_container, bg='white', relief='solid', bd=1)
            card.grid(row=i//3, column=i%3, padx=5, pady=2, sticky='ew')
            
            title_label = tk.Label(
                card,
                text=label,
                font=("Arial", 8),
                bg='white',
                fg='#666'
            )
            title_label.pack(pady=(5, 0))
            
            value_label = tk.Label(
                card,
                text=default_value,
                font=("Arial", 12, "bold"),
                bg='white',
                fg='#333'
            )
            value_label.pack(pady=(0, 5))
            
            self.stat_cards[key] = value_label
    
    def _create_toolbar(self):
        """Create toolbar with action buttons."""
        toolbar_frame = tk.Frame(self.window, bg='#f5f5f5', relief='solid', bd=1)
        toolbar_frame.grid(row=1, column=0, sticky='ew')
        toolbar_frame.grid_columnconfigure(2, weight=1)
        
        # Left side buttons (CRUD operations)
        left_buttons = tk.Frame(toolbar_frame, bg='#f5f5f5')
        left_buttons.grid(row=0, column=0, sticky='w', padx=10, pady=8)
        
        # Add button
        add_btn = tk.Button(
            left_buttons,
            text="➕ Thêm câu hỏi",
            font=("Arial", 10),
            bg='#4CAF50',
            fg='white',
            padx=15,
            pady=5,
            command=self._add_question
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Edit button
        self.edit_btn = tk.Button(
            left_buttons,
            text="✏️ Sửa",
            font=("Arial", 10),
            bg='#FF9800',
            fg='white',
            padx=15,
            pady=5,
            state=tk.DISABLED,
            command=self._edit_question
        )
        self.edit_btn.pack(side=tk.LEFT, padx=5)
        
        # Delete button
        self.delete_btn = tk.Button(
            left_buttons,
            text="🗑️ Xóa",
            font=("Arial", 10),
            bg='#F44336',
            fg='white',
            padx=15,
            pady=5,
            state=tk.DISABLED,
            command=self._delete_selected
        )
        self.delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Duplicate button
        self.duplicate_btn = tk.Button(
            left_buttons,
            text="📋 Sao chép",
            font=("Arial", 10),
            bg='#9C27B0',
            fg='white',
            padx=15,
            pady=5,
            state=tk.DISABLED,
            command=self._duplicate_question
        )
        self.duplicate_btn.pack(side=tk.LEFT, padx=5)
        
        # Search section
        search_frame = tk.Frame(toolbar_frame, bg='#f5f5f5')
        search_frame.grid(row=0, column=1, padx=20, pady=8)
        
        tk.Label(
            search_frame,
            text="🔍",
            font=("Arial", 12),
            bg='#f5f5f5'
        ).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=("Arial", 10),
            width=25
        )
        self.search_entry.pack(side=tk.LEFT, padx=(5, 0))
        self.search_entry.bind('<Return>', lambda e: self._search_questions())
        
        search_btn = tk.Button(
            search_frame,
            text="Tìm",
            font=("Arial", 10),
            bg='#2196F3',
            fg='white',
            padx=10,
            pady=3,
            command=self._search_questions
        )
        search_btn.pack(side=tk.LEFT, padx=5)
        
        # Advanced search
        advanced_search_btn = tk.Button(
            search_frame,
            text="🔧",
            font=("Arial", 10),
            bg='#607D8B',
            fg='white',
            padx=8,
            pady=3,
            command=self._advanced_search
        )
        advanced_search_btn.pack(side=tk.LEFT, padx=2)
        
        # Right side buttons (utility)
        right_buttons = tk.Frame(toolbar_frame, bg='#f5f5f5')
        right_buttons.grid(row=0, column=2, sticky='e', padx=10, pady=8)
        
        # Refresh button
        refresh_btn = tk.Button(
            right_buttons,
            text="🔄 Làm mới",
            font=("Arial", 10),
            bg='#607D8B',
            fg='white',
            padx=15,
            pady=5,
            command=self._refresh_data
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Clear filters
        clear_btn = tk.Button(
            right_buttons,
            text="🧹 Xóa filter",
            font=("Arial", 10),
            bg='#795548',
            fg='white',
            padx=15,
            pady=5,
            command=self._clear_filters
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)

        timer_settings_btn = tk.Button(
            right_buttons,
            text="⏰ Cài đặt thời gian",
            font=("Arial", 10),
            bg='#9C27B0',
            fg='white',
            padx=15,
            pady=5,
            command=self._open_timer_settings
        )
        timer_settings_btn.pack(side=tk.RIGHT, padx=5)

    # Thêm phương thức mới:
    def _open_timer_settings(self):
        """Open timer settings dialog."""
        try:
            from .components.timer_settings_dialog import TimerSettingsDialog
            from ..config.settings import Config
        
            # Get current settings
            current_settings = {
                'total_quiz_time': Config.TOTAL_QUIZ_TIME,
                'show_timer': Config.SHOW_TIMER,
                'auto_submit': Config.AUTO_SUBMIT
            }
        
            dialog = TimerSettingsDialog(self.window)
            settings = dialog.show(current_settings)
        
            if settings:
            # Save settings
                success = Config.save_timer_settings(
                    total_quiz_time=settings['total_quiz_time'],
                    show_timer=settings['show_timer'],
                    auto_submit=settings['auto_submit']
                )
            
                if success:
                    messagebox.showinfo("Thành công", f"Đã lưu cài đặt thời gian: {settings['total_quiz_time']//60} phút!")
                    self.logger.info(f"Timer settings updated: {settings}")
                else:
                    messagebox.showerror("Lỗi", "Không thể lưu cài đặt!")

        except Exception as e:
            self.logger.error(f"Error opening timer settings: {e}")
            messagebox.showerror("Lỗi", f"Không thể mở cài đặt thời gian: {str(e)}")

    def _create_main_content(self):
        """Create main content area with questions list."""
        main_frame = tk.Frame(self.window)
        main_frame.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Create treeview for questions
        columns = ('ID', 'Prompt', 'Category', 'Difficulty', 'Answer', 'Created')
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=20)
        
        # Define column headings and widths
        self.tree.heading('ID', text='ID')
        self.tree.heading('Prompt', text='Câu hỏi')
        self.tree.heading('Category', text='Danh mục')
        self.tree.heading('Difficulty', text='Độ khó')
        self.tree.heading('Answer', text='Đáp án')
        self.tree.heading('Created', text='Ngày tạo')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Prompt', width=400)
        self.tree.column('Category', width=120, anchor='center')
        self.tree.column('Difficulty', width=100, anchor='center')
        self.tree.column('Answer', width=80, anchor='center')
        self.tree.column('Created', width=120, anchor='center')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        # Bind selection events
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        self.tree.bind('<Double-Button-1>', self._on_double_click)
        
        # Pagination frame
        pagination_frame = tk.Frame(main_frame)
        pagination_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.prev_page_btn = tk.Button(
            pagination_frame,
            text="← Trang trước",
            command=self._prev_page,
            state=tk.DISABLED
        )
        self.prev_page_btn.pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(pagination_frame, text="Trang 1 / 1")
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        self.next_page_btn = tk.Button(
            pagination_frame,
            text="Trang sau →",
            command=self._next_page,
            state=tk.DISABLED
        )
        self.next_page_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_status_bar(self):
        """Create status bar."""
        status_frame = tk.Frame(self.window, bg='#e0e0e0', relief='sunken', bd=1)
        status_frame.grid(row=3, column=0, sticky='ew')
        
        self.status_label = tk.Label(
            status_frame,
            text="Sẵn sàng",
            bg='#e0e0e0',
            anchor='w'
        )
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.selection_label = tk.Label(
            status_frame,
            text="",
            bg='#e0e0e0',
            anchor='e'
        )
        self.selection_label.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def _load_data(self):
        """Load questions data."""
        try:
            # Get paginated questions
            result = self.admin_service.get_all_questions(
                page=self.current_page,
                per_page=self.items_per_page
            )
            
            self.questions = result['questions']
            self.total_pages = result['total_pages']
            
            # Update tree
            self._update_tree()
            
            # Update pagination
            self._update_pagination()
            
            # Update stats
            self._update_stats()
            
            self.status_label.config(text=f"Đã tải {len(self.questions)} câu hỏi")
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu: {str(e)}")
    
    def _update_tree(self):
        """Update treeview with questions."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add questions
        for question in self.questions:
            created_date = question.created_at.strftime("%Y-%m-%d") if question.created_at else ""
            self.tree.insert('', 'end', values=(
                question.id,
                question.prompt[:80] + "..." if len(question.prompt) > 80 else question.prompt,
                question.category,
                question.difficulty,
                question.answer,
                created_date
            ))
    
    def _update_pagination(self):
        """Update pagination controls."""
        self.page_label.config(text=f"Trang {self.current_page} / {self.total_pages}")
        
        # Update button states
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
    
    def _update_stats(self):
        """Update dashboard statistics."""
        try:
            stats = self.admin_service.get_dashboard_stats()
            
            self.stat_cards['total_questions'].config(text=str(stats.get('total_questions', 0)))
            self.stat_cards['total_categories'].config(text=str(stats.get('total_categories', 0)))
            self.stat_cards['total_quizzes'].config(text=str(stats.get('total_quizzes', 0)))
            
        except Exception as e:
            self.logger.error(f"Error updating stats: {e}")
    
    def _on_selection_change(self, event):
        """Handle treeview selection change."""
        selected_items = self.tree.selection()
        self.selected_items = set(selected_items)
        
        # Update button states
        has_selection = len(selected_items) > 0
        single_selection = len(selected_items) == 1
        
        self.edit_btn.config(state=tk.NORMAL if single_selection else tk.DISABLED)
        self.delete_btn.config(state=tk.NORMAL if has_selection else tk.DISABLED)
        self.duplicate_btn.config(state=tk.NORMAL if single_selection else tk.DISABLED)
        
        # Update status
        if has_selection:
            self.selection_label.config(text=f"Đã chọn: {len(selected_items)} câu hỏi")
        else:
            self.selection_label.config(text="")
    
    def _on_double_click(self, event):
        """Handle double-click on tree item."""
        if self.tree.selection():
            self._edit_question()
    
    def _add_question(self):
        """Add new question."""
        try:
            categories = self.admin_service.get_categories()
            dialog = QuestionDialog(self.window, categories=categories)
            question = dialog.show()
            
            if question:
                success, message, question_id = self.admin_service.create_question(
                    prompt=question.prompt,
                    options=[question.option_a, question.option_b, question.option_c],
                    answer=question.answer,
                    category=question.category,
                    difficulty=question.difficulty,
                    tags=question.tags
                )
                
                if success:
                    messagebox.showinfo("Thành công", message)
                    self._refresh_data()
                else:
                    messagebox.showerror("Lỗi", message)
                    
        except Exception as e:
            self.logger.error(f"Error adding question: {e}")
            messagebox.showerror("Lỗi", f"Không thể thêm câu hỏi: {str(e)}")
    
    def _edit_question(self):
        """Edit selected question."""
        try:
            selected = self.tree.selection()
            if not selected:
                return
            
            # Get question ID from first column
            item = selected[0]
            values = self.tree.item(item, 'values')
            question_id = int(values[0])
            
            # Find question in current list
            question = None
            for q in self.questions:
                if q.id == question_id:
                    question = q
                    break
            
            if not question:
                messagebox.showerror("Lỗi", "Không tìm thấy câu hỏi!")
                return
            
            categories = self.admin_service.get_categories()
            dialog = QuestionDialog(self.window, question=question, categories=categories)
            updated_question = dialog.show()
            
            if updated_question:
                success, message = self.admin_service.update_question(
                    question_id=updated_question.id,
                    prompt=updated_question.prompt,
                    options=[updated_question.option_a, updated_question.option_b, updated_question.option_c],
                    answer=updated_question.answer,
                    category=updated_question.category,
                    difficulty=updated_question.difficulty,
                    tags=updated_question.tags
                )
                
                if success:
                    messagebox.showinfo("Thành công", message)
                    self._refresh_data()
                else:
                    messagebox.showerror("Lỗi", message)
                    
        except Exception as e:
            self.logger.error(f"Error editing question: {e}")
            messagebox.showerror("Lỗi", f"Không thể sửa câu hỏi: {str(e)}")
    
    def _delete_selected(self):
        """Delete selected questions."""
        try:
            selected = self.tree.selection()
            if not selected:
                return
            
            # Confirm deletion
            count = len(selected)
            if not ConfirmDialog.show(
                self.window,
                "Xác nhận xóa",
                f"Bạn có chắc chắn muốn xóa {count} câu hỏi đã chọn?\nHành động này không thể hoàn tác!"
            ):
                return
            
            # Get question IDs
            question_ids = []
            for item in selected:
                values = self.tree.item(item, 'values')
                question_ids.append(int(values[0]))
            
            # Delete questions
            if len(question_ids) == 1:
                success, message = self.admin_service.delete_question(question_ids[0])
            else:
                success, message, deleted_count = self.admin_service.delete_multiple_questions(question_ids)
            
            if success:
                messagebox.showinfo("Thành công", message)
                self._refresh_data()
            else:
                messagebox.showerror("Lỗi", message)
                
        except Exception as e:
            self.logger.error(f"Error deleting questions: {e}")
            messagebox.showerror("Lỗi", f"Không thể xóa câu hỏi: {str(e)}")
    
    def _duplicate_question(self):
        """Duplicate selected question."""
        try:
            selected = self.tree.selection()
            if not selected:
                return
            
            # Get question ID
            item = selected[0]
            values = self.tree.item(item, 'values')
            question_id = int(values[0])
            
            success, message, new_id = self.admin_service.duplicate_question(question_id)
            
            if success:
                messagebox.showinfo("Thành công", message)
                self._refresh_data()
            else:
                messagebox.showerror("Lỗi", message)
                
        except Exception as e:
            self.logger.error(f"Error duplicating question: {e}")
            messagebox.showerror("Lỗi", f"Không thể sao chép câu hỏi: {str(e)}")
    
    def _search_questions(self):
        """Search questions."""
        try:
            search_term = self.search_var.get().strip()
            if not search_term:
                self._refresh_data()
                return
            
            questions = self.admin_service.search_questions(search_term)
            self.questions = questions
            self._update_tree()
            
            self.status_label.config(text=f"Tìm thấy {len(questions)} câu hỏi")
            
        except Exception as e:
            self.logger.error(f"Error searching questions: {e}")
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm: {str(e)}")
    
    def _advanced_search(self):
        """Show advanced search dialog."""
        try:
            categories = self.admin_service.get_categories()
            dialog = SearchDialog(self.window, categories)
            criteria = dialog.show()
            
            if criteria:
                questions = self.admin_service.search_questions(
                    search_term=criteria['search_term'],
                    category=criteria['category'],
                    difficulty=criteria['difficulty']
                )
                
                self.questions = questions
                self._update_tree()
                
                self.status_label.config(text=f"Tìm thấy {len(questions)} câu hỏi với bộ lọc")
                
        except Exception as e:
            self.logger.error(f"Error in advanced search: {e}")
            messagebox.showerror("Lỗi", f"Không thể tìm kiếm nâng cao: {str(e)}")
    
    def _refresh_data(self):
        """Refresh data."""
        self.current_page = 1
        self._clear_filters()
        self._load_data()
    
    def _clear_filters(self):
        """Clear all filters."""
        self.search_var.set("")
        self.status_label.config(text="Đã xóa bộ lọc")
    
    def _prev_page(self):
        """Go to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self._load_data()
    
    def _next_page(self):
        """Go to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self._load_data()