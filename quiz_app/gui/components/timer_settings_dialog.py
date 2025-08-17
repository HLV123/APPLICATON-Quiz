"""Timer settings dialog for admin."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Dict, Any

class TimerSettingsDialog:
    """Dialog for configuring quiz timer settings."""
    
    def __init__(self, parent):
        self.parent = parent
        self.result = None
        self.dialog = None
    
    def show(self, current_settings: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Show timer settings dialog.
        
        Args:
            current_settings: Current timer settings
            
        Returns:
            Dictionary with timer settings if saved, None if cancelled
        """
        self.current_settings = current_settings or {}
        
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("⏰ Cài đặt thời gian Quiz")
        self.dialog.geometry("800x550")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"800x550+{x}+{y}")
        
        # Create widgets
        self._create_widgets()
        
        # Load current settings
        self._load_current_settings()
        
        # Wait for dialog to close
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = tk.Frame(self.dialog, padx=30, pady=25)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Cài đặt thời gian làm bài",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 25))
        
        # Time settings frame
        time_frame = tk.LabelFrame(
            main_frame, 
            text="⏰ Thời gian tổng cho bài thi", 
            font=("Arial", 11, "bold"),
            padx=20,
            pady=15
        )
        time_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Total time input
        time_input_frame = tk.Frame(time_frame)
        time_input_frame.pack()
        
        tk.Label(
            time_input_frame, 
            text="Tổng thời gian:",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)
        
        self.total_time_var = tk.StringVar(value="5")
        self.total_time_spinbox = tk.Spinbox(
            time_input_frame,
            from_=1,
            to=120,
            textvariable=self.total_time_var,
            width=10,
            font=("Arial", 11)
        )
        self.total_time_spinbox.pack(side=tk.LEFT, padx=(10, 5))
        
        tk.Label(
            time_input_frame, 
            text="phút",
            font=("Arial", 11)
        ).pack(side=tk.LEFT)
        
        # Info label
        info_text = "💡 Thí sinh có tổng thời gian cho toàn bộ bài thi.\nCó thể chuyển câu tự do trong thời gian cho phép."
        info_label = tk.Label(
            time_frame,
            text=info_text,
            font=("Arial", 9),
            fg="blue",
            justify=tk.LEFT
        )
        info_label.pack(pady=(10, 0))
        
        # Additional options
        options_frame = tk.LabelFrame(
            main_frame, 
            text="Tùy chọn khác", 
            font=("Arial", 11, "bold"),
            padx=20,
            pady=10
        )
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.show_timer_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Hiển thị đồng hồ đếm ngược",
            variable=self.show_timer_var,
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=5)
        
        self.auto_submit_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            options_frame,
            text="Tự động nộp bài khi hết giờ",
            variable=self.auto_submit_var,
            font=("Arial", 10)
        ).pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Lưu cài đặt",
            command=self._on_save,
            bg="#4CAF50",
            fg="white",
            padx=20,
            pady=8,
            font=("Arial", 11, "bold")
        )
        save_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        cancel_btn = tk.Button(
            button_frame,
            text="Hủy",
            command=self._on_cancel,
            padx=20,
            pady=8,
            font=("Arial", 10)
        )
        cancel_btn.pack(side=tk.RIGHT)
        
        default_btn = tk.Button(
            button_frame,
            text="🔄 Mặc định",
            command=self._reset_to_default,
            padx=20,
            pady=8,
            font=("Arial", 10)
        )
        default_btn.pack(side=tk.LEFT)
    
    def _load_current_settings(self):
        """Load current settings into the dialog."""
        if self.current_settings:
            self.total_time_var.set(str(self.current_settings.get('total_quiz_time', 300) // 60))
            self.show_timer_var.set(self.current_settings.get('show_timer', True))
            self.auto_submit_var.set(self.current_settings.get('auto_submit', True))
    
    def _on_save(self):
        """Handle save button click."""
        try:
            total_minutes = int(self.total_time_var.get())
            if total_minutes < 1 or total_minutes > 120:
                messagebox.showerror("Lỗi", "Tổng thời gian phải từ 1-120 phút!")
                return
            
            total_quiz_time = total_minutes * 60
            
            self.result = {
                'total_quiz_time': total_quiz_time,
                'show_timer': self.show_timer_var.get(),
                'auto_submit': self.auto_submit_var.get()
            }
            
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số hợp lệ cho thời gian!")
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def _reset_to_default(self):
        """Reset to default settings."""
        self.total_time_var.set("5")
        self.show_timer_var.set(True)
        self.auto_submit_var.set(True)
        messagebox.showinfo("Thông báo", "Đã đặt lại cài đặt mặc định (5 phút)!")