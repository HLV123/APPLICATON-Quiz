#!/usr/bin/env python3
"""
Quiz Application - Main Entry Point

A comprehensive quiz application with admin panel for question management.
Features include timed quizzes, scoring, statistics, and full CRUD admin interface.

Usage:
    python main.py              # Run with GUI
    python main.py --admin      # Start in admin mode
    python main.py --help       # Show help
"""

import sys
import os
import argparse
import tkinter as tk
from tkinter import messagebox
import traceback

# Add the src directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir) 
sys.path.insert(0, src_dir)

try:
    from quiz_app import get_app_info, get_version
    from quiz_app.config.settings import Config
    from quiz_app.utils.logger import Logger
    from quiz_app.services.admin_service import AdminService
    from quiz_app.gui.components.dialogs import LoginDialog
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure you're running from the correct directory and all dependencies are installed.")
    sys.exit(1)

class QuizApplication:
    """Main application class."""
    
    def __init__(self, start_admin: bool = False):
        """
        Initialize application.
        
        Args:
            start_admin: Start directly in admin mode
        """
        self.start_admin = start_admin
        self.logger = Logger(__name__, Config.LOG_FILE, Config.LOG_LEVEL)
        self.root = None
        
        # Log application start
        app_info = get_app_info()
        self.logger.info(f"Starting {app_info['name']} v{app_info['version']}")
    
    def run(self):
        """Run the application."""
        try:
            # Initialize Tkinter root
            self.root = tk.Tk()
            self.root.withdraw()  # Hide root initially
            
            # Set application icon and basic properties
            self._setup_root_window()
            
            if self.start_admin:
                # Start in admin mode
                self._start_admin_mode()
            else:
                # Start with main window
                self._start_main_window()
            
            # Start the main event loop
            self.logger.info("Application GUI started successfully")
            self.root.mainloop()
            
        except Exception as e:
            self.logger.error(f"Application error: {e}")
            self.logger.error(traceback.format_exc())
            
            # Show error dialog if possible
            if self.root:
                messagebox.showerror(
                    "Application Error", 
                    f"An unexpected error occurred:\n{str(e)}\n\nCheck the log file for details."
                )
            else:
                print(f"❌ Critical Error: {e}")
            
            sys.exit(1)
        finally:
            self.logger.info("Application shutting down")
    
    def _setup_root_window(self):
        """Setup root window properties."""
        app_info = get_app_info()
        self.root.title(app_info['name'])
        
        # Set window icon (if available)
        try:
            # Try to set icon - this will fail gracefully if icon file doesn't exist
            icon_path = os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Icon not available, continue without it
        
        # Center window on screen
        window_width = Config.WINDOW_WIDTH
        window_height = Config.WINDOW_HEIGHT
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        
        # Set minimum window size
        self.root.minsize(600, 400)
    
    def _start_main_window(self):
        """Start with main application window."""
        try:
            # Import here to avoid circular imports
            from quiz_app.gui.main_window import MainWindow
            
            self.root.deiconify()  # Show root window
            main_window = MainWindow(self.root)
            self.logger.info("Main window initialized")
            
        except ImportError:
            # If main window not implemented yet, show placeholder
            self._show_placeholder_main()
    
    def _start_admin_mode(self):
        """Start in admin mode with login."""
        try:
            # Show login dialog
            login_dialog = LoginDialog(self.root)
            credentials = login_dialog.show()
            
            if not credentials:
                self.logger.info("Admin login cancelled")
                sys.exit(0)
            
            username, password = credentials
            
            # Authenticate admin
            admin_service = AdminService()
            user = admin_service.authenticate_admin(username, password)
            
            if not user:
                messagebox.showerror("Đăng nhập thất bại", "Tên đăng nhập hoặc mật khẩu không đúng!")
                self.logger.warning(f"Failed admin login attempt: {username}")
                sys.exit(1)
            
            self.logger.info(f"Admin {username} logged in successfully")
            
            # Start admin window
            try:
                from quiz_app.gui.admin_window import AdminWindow
                
                self.root.deiconify()  # Show root window
                admin_window = AdminWindow(self.root, user)
                self.logger.info("Admin window initialized")
                
            except ImportError:
                # If admin window not implemented yet, show placeholder
                self._show_placeholder_admin()
                
        except Exception as e:
            self.logger.error(f"Error starting admin mode: {e}")
            messagebox.showerror("Lỗi", f"Không thể khởi động chế độ admin:\n{str(e)}")
            sys.exit(1)
    
    def _show_placeholder_main(self):
        """Show placeholder main window (for development)."""
        self.root.deiconify()
        self.root.title("Quiz App - Main Window (Placeholder)")
        
        frame = tk.Frame(self.root, bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(frame, text="🎯 Quiz Application", font=("Arial", 24, "bold"), bg='#f0f0f0')
        title.pack(pady=20)
        
        # Info
        app_info = get_app_info()
        info_text = f"Version: {app_info['version']}\nStatus: Main window under development"
        info_label = tk.Label(frame, text=info_text, font=("Arial", 12), bg='#f0f0f0')
        info_label.pack(pady=10)
        
        # Buttons
        button_frame = tk.Frame(frame, bg='#f0f0f0')
        button_frame.pack(pady=20)
        
        admin_btn = tk.Button(
            button_frame, 
            text="🔑 Admin Mode", 
            font=("Arial", 12),
            bg='#2196F3',
            fg='white',
            padx=20,
            pady=10,
            command=self._launch_admin_mode
        )
        admin_btn.pack(side=tk.LEFT, padx=10)
        
        quiz_btn = tk.Button(
            button_frame, 
            text="📝 Take Quiz (Coming Soon)", 
            font=("Arial", 12),
            bg='#4CAF50',
            fg='white',
            padx=20,
            pady=10,
            state=tk.DISABLED
        )
        quiz_btn.pack(side=tk.LEFT, padx=10)
        
        # Status
        status_label = tk.Label(
            frame, 
            text="💡 Click 'Admin Mode' to manage questions", 
            font=("Arial", 10), 
            bg='#f0f0f0',
            fg='#666'
        )
        status_label.pack(pady=10)
        
        self.logger.info("Placeholder main window displayed")
    
    def _show_placeholder_admin(self):
        """Show placeholder admin window (for development)."""
        self.root.deiconify()
        self.root.title("Quiz App - Admin Panel (Placeholder)")
        
        frame = tk.Frame(self.root, bg='#e3f2fd')
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(frame, text="🔑 Admin Panel", font=("Arial", 24, "bold"), bg='#e3f2fd')
        title.pack(pady=20)
        
        # Status
        status_text = "Admin window is under development.\nCRUD functionality will be available soon."
        status_label = tk.Label(frame, text=status_text, font=("Arial", 12), bg='#e3f2fd')
        status_label.pack(pady=10)
        
        # Test database button
        test_btn = tk.Button(
            frame,
            text="🧪 Test Database Connection",
            font=("Arial", 12),
            bg='#FF9800',
            fg='white',
            padx=20,
            pady=10,
            command=self._test_database
        )
        test_btn.pack(pady=20)
        
        self.logger.info("Placeholder admin window displayed")
    
    def _launch_admin_mode(self):
        """Launch admin mode from main window."""
        self.root.destroy()
        app = QuizApplication(start_admin=True)
        app.run()
    
    def _test_database(self):
        """Test database connection and show some stats."""
        try:
            admin_service = AdminService()
            stats = admin_service.get_dashboard_stats()
            
            message = "📊 Database Connection Test:\n\n"
            message += f"✅ Connected successfully!\n"
            message += f"📝 Total Questions: {stats.get('total_questions', 0)}\n"
            message += f"📂 Categories: {stats.get('total_categories', 0)}\n"
            message += f"🎯 Total Quizzes: {stats.get('total_quizzes', 0)}\n"
            
            messagebox.showinfo("Database Test", message)
            self.logger.info("Database test successful")
            
        except Exception as e:
            error_msg = f"❌ Database Error:\n{str(e)}"
            messagebox.showerror("Database Test Failed", error_msg)
            self.logger.error(f"Database test failed: {e}")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Quiz Application with Admin Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Start main application
  %(prog)s --admin           # Start in admin mode
  %(prog)s --version         # Show version info
        """
    )
    
    parser.add_argument(
        '--admin', 
        action='store_true',
        help='Start in admin mode'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f"Quiz Application {get_version()}"
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()

def main():
    """Main entry point."""
    # Print banner
    app_info = get_app_info()
    print(f"🎯 {app_info['name']} v{app_info['version']}")
    print(f"📝 {app_info['description']}")
    print("=" * 50)
    
    # Parse arguments
    args = parse_arguments()
    
    # Set debug logging if requested
    if args.debug:
        Config.LOG_LEVEL = 'DEBUG'
        print("🐛 Debug logging enabled")
    
    try:
        # Create and run application
        app = QuizApplication(start_admin=args.admin)
        app.run()
        
    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()