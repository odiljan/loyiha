import sqlite3
import hashlib
import re

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Jadval yaratish
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user'
)
""")
conn.commit()


# ========================
# Parol hash
# ========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ========================
# Parol kuchini tekshirish
# ========================
def check_password_strength(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    return True


# ========================
# Registratsiya
# ========================
def register():
    username = input("Username kiriting: ")
    password = input("Parol kiriting: ")

    if not check_password_strength(password):
        print("❌ Parol kuchsiz! (8+ belgi, katta harf, kichik harf, raqam)")
        return

    hashed = hash_password(password)

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed)
        )
        conn.commit()
        print("✅ Ro'yxatdan o'tdingiz!")
    except sqlite3.IntegrityError:
        print("❌ Username mavjud!")


# ========================
# Admin yaratish
# ========================
def create_admin():
    cursor.execute("SELECT * FROM users WHERE role='admin'")
    if not cursor.fetchone():
        admin_pass = hash_password("Admin123")
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", admin_pass, "admin")
        )
        conn.commit()


# ========================
# Login
# ========================
def login():
    username = input("Username: ")
    password = input("Parol: ")

    hashed = hash_password(password)

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed)
    )
    user = cursor.fetchone()

    if user:
        print("🎉 Xush kelibsiz,", username)
        user_panel(user)
    else:
        print("❌ Login xato!")


# ========================
# User panel
# ========================
def user_panel(user):
    while True:
        print("\n1. Parolni o‘zgartirish")

        if user[3] == "admin":
            print("2. Userlarni ko‘rish")
            print("3. Chiqish")
        else:
            print("2. Chiqish")

        choice = input("Tanlang: ")

        if choice == "1":
            change_password(user)
        elif choice == "2" and user[3] == "admin":
            show_users()
        elif (choice == "2" and user[3] != "admin") or \
             (choice == "3" and user[3] == "admin"):
            break
        else:
            print("Noto‘g‘ri tanlov!")


# ========================
# Parol o‘zgartirish
# ========================
def change_password(user):
    new_password = input("Yangi parol: ")

    if not check_password_strength(new_password):
        print("❌ Parol kuchsiz!")
        return

    hashed = hash_password(new_password)

    cursor.execute(
        "UPDATE users SET password=? WHERE id=?",
        (hashed, user[0])
    )
    conn.commit()

    print("✅ Parol o‘zgartirildi!")


# ========================
# Admin userlarni ko‘rish
# ========================
def show_users():
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()

    print("\n--- Userlar ro‘yxati ---")
    for u in users:
        print(f"ID: {u[0]} | Username: {u[1]} | Role: {u[2]}")


# ========================
# Asosiy menyu
# ========================
def main():
    create_admin()

    while True:
        print("\n1. Registratsiya")
        print("2. Login")
        print("3. Chiqish")

        choice = input("Tanlang: ")
        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            break
        else:
            print("Noto‘g‘ri tanlov!")


if __name__ == "__main__":
    main()
    conn.close() 