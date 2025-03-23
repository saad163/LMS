import os

class LibraryManagementSystem:
    def __init__(self, filename="library_data.txt"):
        self.filename = filename
        self.books = self.load_data()

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                books = [line.strip().split(",") for line in file.readlines()]
        else:
            books = []
        return books

    def save_data(self):
        with open(self.filename, "w") as file:
            for book in self.books:
                file.write(",".join(book) + "\n")

    def add_book(self, title, author, year):
        self.books.append([title, author, year])
        self.save_data()
        print(f"Book '{title}' added successfully.")

    def view_all_books(self):
        if self.books:
            for idx, book in enumerate(self.books, start=1):
                print(f"{idx}. Title: {book[0]}, Author: {book[1]}, Year: {book[2]}")
        else:
            print("No books available.")

    def search_book(self, title):
        found_books = [book for book in self.books if book[0].lower() == title.lower()]
        if found_books:
            for book in found_books:
                print(f"Title: {book[0]}, Author: {book[1]}, Year: {book[2]}")
        else:
            print(f"No books found with the title '{title}'.")

    def remove_book(self, title):
        initial_count = len(self.books)
        self.books = [book for book in self.books if book[0].lower() != title.lower()]
        if len(self.books) < initial_count:
            self.save_data()
            print(f"Book '{title}' removed successfully.")
        else:
            print(f"No books found with the title '{title}'.")

    def save_and_load_data(self):
        self.save_data()
        self.books = self.load_data()
        print("Data saved and loaded successfully.")

if __name__ == "__main__":
    library = LibraryManagementSystem()

    while True:
        print("\nLibrary Management System")
        print("1. Add a Book")
        print("2. View All Books")
        print("3. Search for a Book")
        print("4. Remove a Book")
        print("5. Save and Load Data")
        print("6. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter book title: ")
            author = input("Enter book author: ")
            year = input("Enter book year: ")
            library.add_book(title, author, year)
        elif choice == "2":
            library.view_all_books()
        elif choice == "3":
            title = input("Enter book title to search: ")
            library.search_book(title)
        elif choice == "4":
            title = input("Enter book title to remove: ")
            library.remove_book(title)
        elif choice == "5":
            library.save_and_load_data()
        elif choice == "6":
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")
