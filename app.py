from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'cs-219'
BOOKS_FILE = "books.txt"
USERS_FILE = "users.txt"
ADMINS_FILE = "admins.txt"  # ✅ Admins ke liye alag file
ISSUED_BOOKS_FILE = "issued_books.txt"

# 📚 Load Books
def load_books():
    if not os.path.exists(BOOKS_FILE):
        return []
    with open(BOOKS_FILE, "r") as file:
        return [line.strip().split(",") for line in file.readlines()]

# Load Issued Books
def load_issued_books():
    if not os.path.exists(ISSUED_BOOKS_FILE):
        return []
    with open(ISSUED_BOOKS_FILE, "r") as file:
        return [line.strip().split(",") for line in file.readlines()]

# Save Issued Books
def save_issued_books(issued_books):
    with open(ISSUED_BOOKS_FILE, "w") as file:
        for book in issued_books:
            file.write(",".join(book) + "\n")


# 📚 Save Books
def save_books(books):
    with open(BOOKS_FILE, "w") as file:
        for book in books:
            file.write(",".join(book) + "\n")

# 👤 Load Users
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    users = {}
    with open(USERS_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 4:
                fullname, email, username, password = parts
                users[username] = {"fullname": fullname, "email": email, "password": password}
    return users

# 👑 Load Admins
def load_admins():
    if not os.path.exists(ADMINS_FILE):
        return {}
    admins = {}
    with open(ADMINS_FILE, "r") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 4:
                fullname, email, username, password = parts
                admins[username] = {"fullname": fullname, "email": email, "password": password}
    return admins

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/library')
def index():
    if "user" not in session:
        return redirect(url_for('login'))
    books = load_books()
    return render_template('index.html', books=books, username=session.get("user"), is_admin=(session.get("role") == "admin"))

@app.route('/add', methods=['POST'])
def add_book():
    if "user" not in session or session.get("role") != "admin":
        return "❌ Unauthorized Access! Only Admin can add books.", 403
    
    title = request.form['title'].strip()
    author = request.form['author'].strip()
    year = request.form['year'].strip()
    shelf = request.form['shelf'].strip()
    
    if title and author and year.isdigit() and shelf:
        books = load_books()
        books.append([title, author, year, shelf])
        save_books(books)
    return redirect(url_for('index'))

@app.route('/delete/<title>')
def delete_book(title):
    if "user" not in session or session.get("role") != "admin":
        return "❌ Unauthorized Access! Only Admin can delete books.", 403

    books = load_books()
    books = [book for book in books if book[0].lower() != title.lower()]
    save_books(books)
    return redirect(url_for('index'))

@app.route('/issue/<title>')
def issue_book(title):
    if "user" not in session or session.get("role") == "admin":
        return "Unauthorized Access! Only Users can issue books.", 403

    issued_books = load_issued_books()
    books = load_books()

    # Check if book exists and is available
    for book in books:
        if book[0].lower() == title.lower():
            issued_books.append([session["user"], book[0], book[1], book[2], book[3]])  # Save user & book details
            save_issued_books(issued_books)
            return redirect(url_for('index'))
    
    return "Book not available!", 404

@app.route('/search', methods=['GET'])
def search_book():
    if "user" not in session:
        return redirect(url_for('login'))
    
    query = request.args.get('query', '').strip().lower()
    books = load_books()
    filtered_books = [book for book in books if query in book[0].lower() or query in book[1].lower() or query in book[3].lower()]
    
    return render_template('index.html', books=filtered_books, search_query=query, username=session.get("user"), is_admin=(session.get("role") == "admin"))

@app.route('/my_issued_books')
def my_issued_books():
    if "user" not in session:
        return redirect(url_for('login'))

    issued_books = load_issued_books()
    user_books = [book for book in issued_books if book[0] == session["user"]]
    
    return render_template('issued_books.html', books=user_books)

@app.route('/return/<title>')
def return_book(title):
    if "user" not in session:
        return redirect(url_for('login'))

    issued_books = load_issued_books()
    issued_books = [book for book in issued_books if not (book[0] == session["user"] and book[1].lower() == title.lower())]
    save_issued_books(issued_books)
    
    return redirect(url_for('my_issued_books'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname'].strip()
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        users = load_users()
        if username in users:
            return render_template('register.html', error="⚠️ Username already exists! Try another.")

        with open(USERS_FILE, "a") as file:
            file.write(f"{fullname},{email},{username},{password}\n")

        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        fullname = request.form['fullname'].strip()
        email = request.form['email'].strip()
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        admins = load_admins()
        if username in admins:
            return render_template('admin_register.html', error="⚠️ Admin username already exists!")

        # ✅ Naya Admin Register Ho Raha Hai
        with open(ADMINS_FILE, "a") as file:
            file.write(f"{fullname},{email},{username},{password}\n")

        # ✅ Session me role "admin" set kar do taki ye books add/delete kar sake
        session["user"] = username
        session["role"] = "admin"

        return redirect(url_for('index'))  # 📚 Admin ko Library Page pe bhejo
    
    return render_template('admin_register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        users = load_users()
        if username in users and users[username]["password"] == password:
            session["user"] = username
            session["role"] = "user"
            return redirect(url_for('index'))

        return render_template("login.html", error="⚠️ Invalid login! Try again.")

    return render_template("login.html")

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()

        admins = load_admins()
        if username in admins and admins[username]["password"] == password:
            session["user"] = username
            session["role"] = "admin"
            return redirect(url_for('index'))

        return render_template("admin_login.html", error="⚠️ Invalid admin login! Try again.")

    return render_template("admin_login.html")

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
