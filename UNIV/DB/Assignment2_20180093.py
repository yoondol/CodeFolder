import sqlite3
import random
from faker import Faker

fake = Faker()
Faker.seed(24)

def create_tables(cursor):
    # ROOM 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ROOM (
        room_id INTEGER PRIMARY KEY,
        room_name TEXT NOT NULL,
        librarian_id INTEGER NOT NULL,
        FOREIGN KEY (librarian_id) REFERENCES LIBRARIAN(librarian_id)
    );
    """)

    # LIBRARIAN 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS LIBRARIAN (
        librarian_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL
    );
    """)

    # BOOKSHELF 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS BOOKSHELF (
        bookshelf_id INTEGER PRIMARY KEY,
        room_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        num_books INTEGER DEFAULT 0,
        FOREIGN KEY (room_id) REFERENCES ROOM(room_id)
        CHECK (num_books <= 500) -- 최대 500권 제한
    );
    """)

    # BOOK 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS BOOK (
        book_id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        publisher TEXT NOT NULL,
        category TEXT NOT NULL,
        total_copies INTEGER,
        remaining_copies INTEGER,
        bookshelf_id INTEGER NOT NULL,
        librarian_id INTEGER NOT NULL,
        FOREIGN KEY (bookshelf_id) REFERENCES BOOKSHELF(bookshelf_id)
        FOREIGN KEY (librarian_id) REFERENCES LIBRARIAN(librarian_id),
        CHECK (remaining_copies >= 0 AND remaining_copies <= total_copies)
    );
    """)

    # USER 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS USER (
        user_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT
    );
    """)

    # BOOK_LOAN 테이블 생성
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS BOOK_LOAN (
        loan_id INTEGER PRIMARY KEY,
        book_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        loan_date DATE NOT NULL,
        return_date DATE,  -- NULL이면 대출 중
        FOREIGN KEY (book_id) REFERENCES BOOK(book_id),
        FOREIGN KEY (user_id) REFERENCES USER(user_id)
        CHECK (return_date IS NULL OR return_date >= loan_date)
    );
    """)


# 트리거 생성 함수
def create_triggers(cursor):
    # BOOKSHELF의 num_books 관리 트리거
    ## 책 추가 시 자동 증가
    cursor.execute("DROP TRIGGER IF EXISTS increase_num_books;")
    cursor.execute("""
    CREATE TRIGGER increase_num_books
    AFTER INSERT ON BOOK
    BEGIN
        UPDATE BOOKSHELF
        SET num_books = num_books + 1
        WHERE bookshelf_id = NEW.bookshelf_id;
    END;
    """)

    ## 책 제거 시 자동 감소
    cursor.execute("DROP TRIGGER IF EXISTS decrease_num_books;")
    cursor.execute("""
    CREATE TRIGGER decrease_num_books
    AFTER DELETE ON BOOK
    BEGIN
        UPDATE BOOKSHELF
        SET num_books = num_books - 1
        WHERE bookshelf_id = OLD.bookshelf_id;
    END;
    """)
    
    # 새 책 추가 
    cursor.execute("DROP TRIGGER IF EXISTS add_book_copy;")
    cursor.execute("""
    CREATE TRIGGER add_book_copy
    AFTER INSERT ON BOOK
    BEGIN
        UPDATE BOOK
        SET total_copies = total_copies + 1
        WHERE book_id = NEW.book_id;
    END;
    """)

    # USER 대출 제한 트리거 (최대 3권)
    cursor.execute("DROP TRIGGER IF EXISTS limit_user_loans;")
    cursor.execute("""
    CREATE TRIGGER limit_user_loans
    BEFORE INSERT ON BOOK_LOAN
    WHEN (SELECT COUNT(*) FROM BOOK_LOAN WHERE user_id = NEW.user_id AND return_date IS NULL) >= 3
    BEGIN
        SELECT RAISE(FAIL, "Users cannot borrow more than 3 books");
    END;
    """)

    # BOOK 대출 시 remaining_copies 감소
    cursor.execute("DROP TRIGGER IF EXISTS loan_book;")
    cursor.execute("""
    CREATE TRIGGER loan_book
    AFTER INSERT ON BOOK_LOAN
    WHEN NEW.return_date IS NULL
    BEGIN
        UPDATE BOOK
        SET remaining_copies = remaining_copies - 1
        WHERE book_id = NEW.book_id AND remaining_copies > 0;
    END;
    """)

    # BOOK 반납 시 remaining_copies 증가
    cursor.execute("DROP TRIGGER IF EXISTS return_book;")
    cursor.execute("""
    CREATE TRIGGER return_book
    AFTER UPDATE ON BOOK_LOAN
    WHEN NEW.return_date IS NOT NULL
    BEGIN
        UPDATE BOOK
        SET remaining_copies = remaining_copies + 1
        WHERE book_id = NEW.book_id;
    END;
    """)

    # BOOK과 BOOKSHELF의 category 동기화
    cursor.execute("DROP TRIGGER IF EXISTS enforce_category;")
    cursor.execute("""
    CREATE TRIGGER enforce_category
    BEFORE INSERT ON BOOK
    WHEN (SELECT category FROM BOOKSHELF WHERE bookshelf_id = NEW.bookshelf_id) != NEW.category
    BEGIN
        SELECT RAISE(FAIL, "Book category must match bookshelf category");
    END;
    """)

    # ROOM당 BOOKSHELF 30개 제한
    cursor.execute("DROP TRIGGER IF EXISTS limit_bookshelves;")
    cursor.execute("""
    CREATE TRIGGER limit_bookshelves
    BEFORE INSERT ON BOOKSHELF
    WHEN (SELECT COUNT(*) FROM BOOKSHELF WHERE room_id = NEW.room_id) >= 30
    BEGIN
        SELECT RAISE(FAIL, "Cannot add more than 30 bookshelves to a room");
    END;
    """)



def insert_random_data(num_records=10):
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()

        # ROOM 데이터 삽입
        for i in range(1, 4):
            cursor.execute("INSERT OR IGNORE INTO ROOM (room_id, room_name, librarian_id) VALUES (?, ?, ?);",
                           (i, f"Room {i}", i))

        # LIBRARIAN 데이터 삽입
        for i in range(1, 4):
            cursor.execute("INSERT OR IGNORE INTO LIBRARIAN (librarian_id, name, phone, email) VALUES (?, ?, ?, ?);",
                           (i, fake.name(), fake.phone_number(), fake.email()))

        # BOOKSHELF 데이터 삽입
        for i in range(1, 10):
            room_id = random.randint(1, 3)
            category = random.choice(["Fiction", "Science", "History"])
            cursor.execute("INSERT OR IGNORE INTO BOOKSHELF (bookshelf_id, room_id, category) VALUES (?, ?, ?);",
                           (i, room_id, category))

        # BOOK 데이터 삽입
        for i in range(1, num_records + 1):
            # Randomly select a bookshelf_id and its category
            cursor.execute("SELECT bookshelf_id, category FROM BOOKSHELF ORDER BY RANDOM() LIMIT 1;")
            result = cursor.fetchone()
            if result:
                bookshelf_id, category = result
                cursor.execute("""
                INSERT OR IGNORE INTO BOOK (book_id, title, author, publisher, category, total_copies, remaining_copies, bookshelf_id, librarian_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (i, fake.text(max_nb_chars=20), fake.name(), fake.company(), category,
                      random.randint(5, 15), random.randint(3, 15), bookshelf_id, random.randint(1, 3)))

        # USER 데이터 삽입
        for i in range(1, num_records + 1):
            cursor.execute("INSERT OR IGNORE INTO USER (user_id, name, email, phone) VALUES (?, ?, ?, ?);",
                           (i, fake.name(), fake.email(), fake.phone_number()))

        # BOOK_LOAN 데이터 삽입
        for i in range(1, num_records // 2 + 1):
            cursor.execute("""
            INSERT OR IGNORE INTO BOOK_LOAN (loan_id, book_id, user_id, loan_date, return_date)
            VALUES (?, ?, ?, ?, ?);
            """, (i, random.randint(1, num_records), random.randint(1, num_records),
                  fake.date_this_year(), None))

        connection.commit()
        print(f"{num_records} random records inserted successfully.")


# CLI 메뉴 함수
def cli_menu():
    while True:
        print("\nWelcome to CAU Library Management System!")
        print("Please select the menu.")
        print("0. new user register")
        print("1. new book register")
        print("2. book update")
        print("3. book delete")
        print("4. new book loan")
        print("5. book loan return")
        print("6. view all data")
        print("7. exit")

        choice = input("Select an option: ")

        if choice == "0":
            new_user_register()
        elif choice == "1":
            new_book_register()
        elif choice == "2":
            book_update()
        elif choice == "3":
            book_delete()
        elif choice == "4":
            new_book_loan()
        elif choice == "5":
            book_loan_return()
        elif choice == "6":
            view_all_data()
        elif choice == "7":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# 유저 등록 함수
def new_user_register():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        name = input("Enter user name: ")
        email = input("Enter user email: ")
        phone = input("Enter user phone: ")
        cursor.execute("INSERT INTO USER (name, email, phone) VALUES (?, ?, ?);", (name, email, phone))
        connection.commit()
        print("User registered successfully!")

# 책 등록 함수
def new_book_register():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        title = input("Enter book title: ")
        author = input("Enter book author: ")
        publisher = input("Enter book publisher: ")
        category = input("Enter book category: ")
        total_copies = int(input("Enter total copies: "))
        bookshelf_id = int(input("Enter bookshelf ID: "))
        librarian_id = int(input("Enter librarian ID: "))
        cursor.execute("""
        INSERT INTO BOOK (title, author, publisher, category, total_copies, remaining_copies, bookshelf_id, librarian_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, (title, author, publisher, category, total_copies, total_copies, bookshelf_id, librarian_id))
        connection.commit()
        print("Book registered successfully!")

# 책 업데이트 함수
def book_update():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        book_id = int(input("Enter book ID to update: "))
        new_title = input("Enter new title: ")
        cursor.execute("UPDATE BOOK SET title = ? WHERE book_id = ?;", (new_title, book_id))
        connection.commit()
        print("Book updated successfully!")

# 책 삭제 함수
def book_delete():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        book_id = int(input("Enter book ID to delete: "))
        cursor.execute("DELETE FROM BOOK WHERE book_id = ?;", (book_id,))
        connection.commit()
        print("Book deleted successfully!")

# 새 책 대출 함수
def new_book_loan():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        book_id = int(input("Enter book ID: "))
        user_id = int(input("Enter user ID: "))
        loan_date = input("Enter loan date (YYYY-MM-DD): ")
        cursor.execute("INSERT INTO BOOK_LOAN (book_id, user_id, loan_date) VALUES (?, ?, ?);", (book_id, user_id, loan_date))
        connection.commit()
        print("Book loan created successfully!")

# 책 반납 함수
def book_loan_return():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        loan_id = int(input("Enter loan ID: "))
        return_date = input("Enter return date (YYYY-MM-DD): ")
        cursor.execute("UPDATE BOOK_LOAN SET return_date = ? WHERE loan_id = ?;", (return_date, loan_id))
        connection.commit()
        print("Book returned successfully!")

# 모든 데이터 보기 함수
def view_all_data():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        tables = ["ROOM", "LIBRARIAN", "BOOKSHELF", "BOOK", "USER", "BOOK_LOAN"]
        for table in tables:
            print(f"\n{table} DATA:")
            cursor.execute(f"SELECT * FROM {table};")
            for row in cursor.fetchall():
                print(row)

# 기존 테이블 및 트리거 삭제
def drop_existing_tables_and_triggers(cursor):
    # 모든 트리거 삭제
    triggers = ["increase_num_books", "decrease_num_books", "add_book_copy", "limit_user_loans", 
                "loan_book", "return_book", "enforce_category", "limit_bookshelves"]
    for trigger in triggers:
        cursor.execute(f"DROP TRIGGER IF EXISTS {trigger};")

    # 모든 테이블 삭제
    tables = ["BOOK_LOAN", "BOOK", "USER", "BOOKSHELF", "LIBRARIAN", "ROOM"]
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table};")
    print("All existing tables and triggers dropped successfully!")

# 데이터베이스 초기화 함수
def initialize_database():
    with sqlite3.connect("library_management.db") as connection:
        cursor = connection.cursor()
        print("Database connected successfully!")

        # 기존 테이블 및 트리거 삭제
        drop_existing_tables_and_triggers(cursor)
        print("All previous tables deleted successfully!")

        # 테이블 생성
        create_tables(cursor)
        print("All tables created successfully!")

        # 트리거 생성
        create_triggers(cursor)
        print("All triggers created successfully!")

        connection.commit()

# 메인 실행
if __name__ == "__main__":
    # 데이터베이스 초기화
    initialize_database()
    # 초기에 무작위 데이터 삽입
    insert_random_data(num_records=10)
    # CLI 시작
    cli_menu()