import tkinter as tk
from tkinter import messagebox
import sqlite3
from tkinter import ttk
import re


def count_books():
    try:
        connect = sqlite3.connect("Books.db")
        cursor = connect.cursor()
        cursor.execute('''SELECT COUNT(*) FROM Books''')
        count = cursor.fetchone()[0]
        connect.close()
    except sqlite3.Error as e:
        messagebox.showerror(title="Error!", message=f"{e}")
        count = 0
    return count


def create_database():
    connect = sqlite3.connect("Books.db")
    cursor = connect.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Books(
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            start_date TEXT,
            end_date TEXT
        )
    ''')
    connect.commit()
    connect.close()


class BookApp:

    def __init__(self, root):
        self.max_book_amount = 10
        self.root = root
        self.book_amount = count_books()
        self.root.title("Book Management App")
        self.root.geometry("800x600")  # Set Window Size
        self.root.resizable(False, False)  # Lock window size

        # Creating main frame
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(row=0, column=0, sticky="nsew")

        # Creating entry frame
        self.entry_frame = ttk.Frame(self.main_frame)
        self.entry_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)

        # Creating canvas for list frame
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.grid(row=1, column=0, sticky="nsew")

        # Creating vertical scrollbar
        self.scrollbar_vertical = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_vertical.grid(row=1, column=1, sticky="ns")
        self.canvas.configure(yscrollcommand=self.scrollbar_vertical.set)

        # Creating horizontal scrollbar
        self.scrollbar_horizontal = ttk.Scrollbar(self.main_frame, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_horizontal.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.canvas.configure(xscrollcommand=self.scrollbar_horizontal.set)

        # Creating content frame inside the canvas
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Setting the size of content frame to canvas
        self.content_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Adding Book Name
        self.title_label = tk.Label(self.entry_frame, text="Book Name", justify="center", font=('bold', 16))
        self.title_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

        self.title_entry = tk.Entry(self.entry_frame, width=20, font=12)
        self.title_entry.grid(row=0, column=1, padx=0, pady=10, ipadx=3, ipady=3, sticky="w")

        # Adding Author
        self.author_label = tk.Label(self.entry_frame, text="Author", justify="center", font=('bold', 16))
        self.author_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)

        self.author_entry = tk.Entry(self.entry_frame, width=20, font=12)
        self.author_entry.grid(row=1, column=1, padx=0, pady=10, ipadx=3, ipady=3, sticky="w")

        # Adding Start Date
        self.start_date_label = tk.Label(self.entry_frame, text="Start Date", justify="center", font=('bold', 16))
        self.start_date_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)

        self.start_entry = tk.Entry(self.entry_frame, width=20, font=12)
        self.start_entry.grid(row=2, column=1, padx=0, pady=10, ipadx=3, ipady=3, sticky="w")

        # Adding End Date
        self.end_date_label = tk.Label(self.entry_frame, text="End Date", justify="center", font=('bold', 16))
        self.end_date_label.grid(row=3, column=0, sticky=tk.W, padx=10, pady=10)

        self.end_entry = tk.Entry(self.entry_frame, width=20, font=12)
        self.end_entry.grid(row=3, column=1, padx=0, pady=10, ipadx=3, ipady=3, sticky="w")

        # Adding buttons
        self.add_button = tk.Button(self.entry_frame, text="Add Book", command=self.add_book, justify="center",
                                    font=16, bd=5, width=10)
        self.add_button.grid(row=4, column=0, columnspan=1, padx=10, pady=10, sticky=tk.N + tk.W + tk.S, ipadx=20)

        self.clear_button = tk.Button(self.entry_frame, text="Clear All", command=self.confirm_clear_all,
                                      justify="center", font=16, bd=5, width=10)
        self.clear_button.grid(row=4, column=1, columnspan=1, padx=10, pady=10, sticky=tk.N + tk.S + tk.W, ipadx=20)

        self.book_display_limit_label = tk.Label(self.entry_frame, text="Display Limit", justify="center", font=('bold', 12))
        self.book_display_limit_label.grid(row=4, column=2, padx=5, pady=10, sticky="w")

        self.book_display_limit = tk.IntVar(value=self.max_book_amount)
        self.book_display_limit_combobox = ttk.Combobox(self.entry_frame, textvariable=self.book_display_limit,
                                                        font=14, width=5, state="readonly")
        self.book_display_limit_combobox.grid(row=4, column=3, sticky="w", pady=10, padx=5)
        self.book_display_limit_combobox["values"] = [10, 25, 50, 100]
        self.book_display_limit_combobox.bind("<<ComboboxSelected>>", self.update_book_display_limit)

        self.total_books_label = tk.Label(self.entry_frame, text=f"Total Books: {self.book_amount}", font=('bold', 14))
        self.total_books_label.grid(row=4, column=4, sticky="w", padx=5, pady=10)

        # List Headers
        self.headers = ["#", "Book Name", "Author", "Start Date", "End Date"]
        for col, header in enumerate(self.headers):
            tk.Label(self.content_frame, text=header, font=('bold', 16)).grid(row=0, column=col, padx=10, pady=10, sticky="w")

        # Adjust columns width
        self.root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Listing books
        self.list_books()

    def update_book_display_limit(self, event):
        self.max_book_amount = self.book_display_limit.get()
        self.list_books()

    def list_books(self):
        connect = sqlite3.connect("Books.db")
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM Books")
        data = cursor.fetchall()
        connect.close()

        # Clear old list
        for widget in self.content_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()

        # Add new list
        for row, book_data in enumerate(data[:self.max_book_amount], start=1):

            tk.Label(self.content_frame, text=str(row), font=('normal', 14)).grid(row=row, column=0, sticky="w", pady=2, padx=10)

            for col, cell in enumerate(book_data, start=1):

                tk.Label(self.content_frame, text=cell, font=('normal', 14)).grid(row=row, column=col, sticky="w", padx=10, pady=2)

        self.total_books_label.config(text=f"Total Books: {len(data)}")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.start_entry.delete(0, tk.END)
        self.end_entry.delete(0, tk.END)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def confirm_clear_all(self):
        if messagebox.askyesno(title="Clear All", message="Are you sure to clear all data?"):
            self.clear_all()

    def clear_all(self):
        connect = sqlite3.connect("Books.db")
        cursor = connect.cursor()
        cursor.execute('DELETE FROM Books')
        connect.commit()
        connect.close()

        # Clear widgets under the headers
        for widget in self.content_frame.grid_slaves():
            if int(widget.grid_info()["row"]) > 0:
                widget.grid_forget()
        self.list_books()

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        start_date = self.start_entry.get()
        end_date = self.end_entry.get()
        connect = sqlite3.connect("Books.db")
        cursor = connect.cursor()
        if not re.match("^[a-zA-ZçÇğĞıİöÖşŞüÜ ]*$", author):
            messagebox.showerror(title="Invalid type", message="Author name must be a string!")
            return
        if title and author:

            if start_date == "":
                start_date = "-"
            if end_date == "":
                end_date = "-"

            cursor.execute('''
                INSERT INTO Books(title, author, start_date, end_date)
                VALUES(?, ?, ?, ?)
            ''', (title, author, start_date, end_date))
            messagebox.showinfo("Success", "Book added successfully.")
            self.clear_form()

        else:
            messagebox.showerror("Error", "Book name and author fields are required.")
        connect.commit()
        connect.close()
        self.list_books()


def main():
    create_database()
    root = tk.Tk()
    app = BookApp(root)
    root.mainloop()


def test():
    pass


if __name__ == '__main__':
    main()
    #test()