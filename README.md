# APPLICATON-Quiz
Well, dùng thử tư duy thiết kế hệ thống để làm một bản demo EOS cho everyone nghịch CRUD ngân hàng câu hỏi qua giao diện đồ họa

## LƯU Í :

#### ADMIN_USERNAME = 'admin'
#### ADMIN_PASSWORD = 'admin123'

##### cách chạy VS Code : terminal : cd "D:\Github\đăng github ngày 17-8-25\quiz_app"  
#####                                python main.py

# 🎯 Quiz Application

Ứng dụng Quiz tương tác với giao diện đồ họa, hỗ trợ quản lý câu hỏi và làm bài thi trắc nghiệm.

## ✨ Tính năng

### 👤 Người dùng
- ✅ Làm bài quiz với thời gian giới hạn
- ✅ Chọn câu hỏi theo danh mục và độ khó
- ✅ Xem điểm và thống kê sau khi hoàn thành
- ✅ Theo dõi lịch sử làm bài
- ✅ Giao diện tiếng Việt thân thiện

### 👨‍💼 Quản trị viên
- ✅ Quản lý câu hỏi (CRUD đầy đủ)
- ✅ Phân loại câu hỏi theo danh mục
- ✅ Thiết lập độ khó (Easy, Medium, Hard)
- ✅ Cài đặt thời gian làm bài
- ✅ Xem thống kê tổng quan
- ✅ Tìm kiếm và lọc câu hỏi nâng cao

### 🔧 Kỹ thuật
- ✅ Database SQLite tích hợp
- ✅ Repository Pattern cho data access
- ✅ Service Layer cho business logic
- ✅ Logging system
- ✅ Input validation
- ✅ Database migrations
  
```
quiz_app/
├── __init__.py
├── main.py                 # Entry point
│
├── config/                 # Cấu hình
│   ├── __init__.py
│   └── settings.py
│
├── database/               # Database layer
│   ├── __init__.py
│   ├── connection.py       # Database connection
│   ├── migrations.py       # Schema migrations
│   └── repository.py       # Data repositories
│
├── gui/                    # Giao diện
│   ├── __init__.py
│   ├── main_window.py      # Màn hình chính
│   ├── admin_window.py     # Panel admin
│   ├── quiz_window.py      # Màn hình làm quiz
│   │
│   └── components/         # UI components
│       ├── __init__.py
│       ├── dialogs.py
│       └── timer_settings_dialog.py
│
├── models/                 # Data models
│   ├── __init__.py
│   ├── question.py
│   └── user.py
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── admin_service.py
│   └── quiz_service.py
│
└── utils/                  # Tiện ích
│   ├── __init__.py
│   ├── logger.py
│   └── validators.py
│
├── quiz.db                         # SQLite database
├── quiz_app.log                    # Log file
├── quiz_config.json                # Timer settings
└── README.md                       # Documentation

```


# Cấu hình

## Cấu hình cơ bản
File config/settings.py chứa các cài đặt mặc định:

# Database
DATABASE_PATH = 'quiz.db'

# GUI
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

# Quiz
DEFAULT_QUESTIONS_PER_QUIZ = 5
TOTAL_QUIZ_TIME = 300  # 5 phút

# Admin
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

## Cấu hình thời gian quiz
Admin có thể cài đặt thời gian thông qua giao diện:

- Đăng nhập Admin Panel
- Click "⏰ Cài đặt thời gian"
- Chọn thời gian tổng cho bài thi
- Lưu cài đặt

# Database

## Schema chính

### questions
- id - Primary key
- prompt - Câu hỏi
- option_a, option_b, option_c - Các lựa chọn
- answer - Đáp án đúng (A/B/C)
- category - Danh mục
- difficulty - Độ khó
- tags - Tags
- created_at, updated_at - Timestamps

### users
- id - Primary key
- username - Tên đăng nhập
- password_hash - Mật khẩu (hash)
- role - Vai trò (admin/user)
- created_at, last_login - Timestamps

### quiz_results
- id - Primary key
- user_id - Foreign key to users
- score - Điểm số
- total_questions - Tổng số câu
- time_taken - Thời gian làm bài
- completed_at - Thời gian hoàn thành


