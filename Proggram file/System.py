"""
Hotel Management System
Developer: MD Atiqul Islam (Atik)
Email: atik.cmttiu1001@gmail.com
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("hotel.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
username TEXT PRIMARY KEY,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS rooms(
room_no INTEGER PRIMARY KEY,
type TEXT,
price INTEGER,
status TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
customer TEXT,
room_no INTEGER,
status TEXT
)
""")

conn.commit()

# default admin with updated password
cursor.execute("INSERT OR IGNORE INTO users VALUES('admin','atik123')")

# default rooms
rooms = [
    (101,'Single',1000,'Available'),
    (102,'Single',1000,'Available'),
    (201,'Double',2000,'Available'),
    (202,'Double',2000,'Available'),
    (301,'Suite',5000,'Available')
]

for r in rooms:
    cursor.execute("INSERT OR IGNORE INTO rooms VALUES(?,?,?,?)", r)

conn.commit()

# ---------------- LOGIN ----------------
def login():
    user = username_entry.get()
    pwd = password_entry.get()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
    if cursor.fetchone():
        login_window.destroy()
        open_dashboard()
    else:
        messagebox.showerror("Login Failed","Invalid username or password")

login_window = tk.Tk()
login_window.title("Hotel Management Login")
login_window.geometry("300x220")

tk.Label(login_window, text="Hotel Management Login", font=("Arial",14)).pack(pady=15)
tk.Label(login_window, text="Username").pack()
username_entry = tk.Entry(login_window)
username_entry.pack()
tk.Label(login_window, text="Password").pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()
tk.Button(login_window, text="Login", command=login, width=15).pack(pady=15)

# ---------------- DASHBOARD ----------------
def open_dashboard():
    dashboard = tk.Tk()
    dashboard.title("Hotel Management System")
    dashboard.geometry("700x450")

    tk.Label(dashboard, text="Hotel Dashboard", font=("Arial",18)).pack(pady=20)

    # -------- Show Rooms --------
    def show_rooms():
        room_window = tk.Toplevel(dashboard)
        room_window.title("Room List")

        tree = ttk.Treeview(room_window, columns=("Room","Type","Price","Status"), show="headings")
        tree.heading("Room", text="Room")
        tree.heading("Type", text="Type")
        tree.heading("Price", text="Price")
        tree.heading("Status", text="Status")
        tree.pack(fill="both", expand=True)

        cursor.execute("SELECT * FROM rooms")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    # -------- Book Room --------
    def book_room():
        book_win = tk.Toplevel(dashboard)
        book_win.title("Book Room")

        tk.Label(book_win, text="Customer Name").pack()
        name_entry = tk.Entry(book_win)
        name_entry.pack()

        tk.Label(book_win, text="Room Number").pack()
        room_entry = tk.Entry(book_win)
        room_entry.pack()

        def confirm_booking():
            name = name_entry.get()
            try:
                room = int(room_entry.get())
            except ValueError:
                messagebox.showerror("Error","Room number must be an integer")
                return

            cursor.execute("SELECT status FROM rooms WHERE room_no=?", (room,))
            data = cursor.fetchone()
            if data and data[0] == "Available":
                cursor.execute("INSERT INTO bookings(customer,room_no,status) VALUES(?,?,?)",
                               (name, room, 'Active'))
                cursor.execute("UPDATE rooms SET status='Booked' WHERE room_no=?", (room,))
                conn.commit()
                messagebox.showinfo("Success","Room booked successfully")
            else:
                messagebox.showerror("Error","Room not available")

        tk.Button(book_win, text="Book Room", command=confirm_booking).pack(pady=10)

    # -------- Checkout --------
    def checkout():
        checkout_win = tk.Toplevel(dashboard)
        checkout_win.title("Checkout")

        tk.Label(checkout_win, text="Room Number").pack()
        room_entry = tk.Entry(checkout_win)
        room_entry.pack()

        def confirm_checkout():
            try:
                room = int(room_entry.get())
            except ValueError:
                messagebox.showerror("Error","Room number must be an integer")
                return

            cursor.execute("SELECT price FROM rooms WHERE room_no=?", (room,))
            data = cursor.fetchone()
            if data:
                price = data[0]
                cursor.execute("UPDATE rooms SET status='Available' WHERE room_no=?", (room,))
                cursor.execute("UPDATE bookings SET status='Completed' WHERE room_no=?", (room,))
                conn.commit()
                messagebox.showinfo("Bill", f"Total Bill: {price} Tk")
            else:
                messagebox.showerror("Error","Invalid room")

        tk.Button(checkout_win, text="Checkout", command=confirm_checkout).pack(pady=10)

    # -------- View Client Status --------
    def client_status():
        status_win = tk.Toplevel(dashboard)
        status_win.title("Client Status")

        tree = ttk.Treeview(status_win, columns=("ID","Customer","Room","Status"), show="headings")
        tree.heading("ID", text="ID")
        tree.heading("Customer", text="Customer")
        tree.heading("Room", text="Room")
        tree.heading("Status", text="Status")
        tree.pack(fill="both", expand=True)

        cursor.execute("SELECT * FROM bookings")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    tk.Button(dashboard, text="Show Rooms", width=25, command=show_rooms).pack(pady=10)
    tk.Button(dashboard, text="Book Room", width=25, command=book_room).pack(pady=10)
    tk.Button(dashboard, text="Checkout", width=25, command=checkout).pack(pady=10)
    tk.Button(dashboard, text="Client Status", width=25, command=client_status).pack(pady=10)

    dashboard.mainloop()

login_window.mainloop()