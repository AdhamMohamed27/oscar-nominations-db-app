import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pymysql
from datetime import datetime
import re
from tkcalendar import DateEntry  # You'll need to install this: pip install tkcalendar

# Database configuration
DB_CONFIG = {
    "host": "sql.freedb.tech",
    "user": "freedb_adhamsmacbook",
    "password": "$?%6HF9&a5k$#wz",
    "database": "freedb_OscarNominations",
    "port": 3306
}

# Color scheme
COLORS = {
    "bg": "#f5f5f7",         # Light background
    "primary": "#0071e3",    # Blue accent color
    "secondary": "#86c3ff",  # Lighter blue
    "text": "#1d1d1f",       # Dark text
    "success": "#34c759",    # Green for success
    "error": "#ff3b30",      # Red for errors
    "header_bg": "#e8e8ed",  # Header background
    "highlight": "#ffd60a"   # Yellow highlight
}

class DatabaseManager:
    @staticmethod
    def get_connection():
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.MySQLError as e:
            messagebox.showerror("Database Error", f"Could not connect to the database: {e}")
            return None

    @staticmethod
    def execute_query(query, params=None, fetch=True):
        connection = DatabaseManager.get_connection()
        if not connection:
            return None
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, params)
                
                if fetch:
                    return cursor.fetchall()
                else:
                    connection.commit()
                    return cursor.rowcount
        except pymysql.MySQLError as e:
            messagebox.showerror("Query Error", f"Error executing query: {e}")
            return None
        finally:
            connection.close()

class OscarNominationsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Oscar Nominations Database")
        self.geometry("1000x700")
        self.resizable(True, True)
        
        # Configure the window
        self.configure(bg=COLORS["bg"])
        self.iconbitmap(default="") # Add path to your icon if available
        
        # Set up styles
        self.setup_styles()
        
        # Current user information
        self.current_user = None
        
        # Create container for frames
        self.container = ttk.Frame(self, style="Main.TFrame")
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create and add frames
        for F in (LoginFrame, SignupFrame, MainMenuFrame, QueryOscarsFrame, 
                 CreateNominationFrame, SearchResultsFrame, UserNominationsFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid to expand
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Start with login frame
        self.show_frame(LoginFrame)
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")  # Base theme
        
        # Configure main frame
        style.configure("Main.TFrame", background=COLORS["bg"])
        
        # Configure regular frames
        style.configure("TFrame", background=COLORS["bg"])
        
        # Configure labels
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Helvetica", 10))
        style.configure("Header.TLabel", font=("Helvetica", 20, "bold"), foreground=COLORS["primary"], background=COLORS["bg"])
        style.configure("SubHeader.TLabel", font=("Helvetica", 14, "bold"), foreground=COLORS["text"], background=COLORS["bg"])
        style.configure("Info.TLabel", background=COLORS["bg"], foreground=COLORS["primary"], font=("Helvetica", 10, "italic"))
        
        # Configure buttons
        style.configure("TButton", background=COLORS["primary"], foreground="white", font=("Helvetica", 10))
        style.map("TButton", 
                 background=[('active', COLORS["secondary"])],
                 foreground=[('active', COLORS["text"])])
        
        # Configure primary action button
        style.configure("Primary.TButton", font=("Helvetica", 12, "bold"))
        
        # Configure entries
        style.configure("TEntry", fieldbackground="white", font=("Helvetica", 10))
        
        # Configure comboboxes
        style.configure("TCombobox", fieldbackground="white", background=COLORS["bg"], font=("Helvetica", 10))
        
        # Configure treeview (for tables)
        style.configure("Treeview", 
                       background="white", 
                       foreground=COLORS["text"],
                       rowheight=25,
                       fieldbackground="white")
        style.configure("Treeview.Heading", 
                       font=("Helvetica", 10, "bold"),
                       background=COLORS["header_bg"],
                       foreground=COLORS["text"])
        style.map("Treeview", 
                 background=[('selected', COLORS["secondary"])],
                 foreground=[('selected', COLORS["text"])])
    
    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()
        if hasattr(frame, 'on_show'):
            frame.on_show()
    
    def set_current_user(self, email):
        self.current_user = email

class LoginFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        # Header with logo (if available)
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=1, column=1, columnspan=2, pady=20)
        
        header = ttk.Label(header_frame, text="Oscar Nominations Database", style="Header.TLabel")
        header.pack(pady=10)
        
        subheader = ttk.Label(header_frame, text="Sign in to your account", style="SubHeader.TLabel")
        subheader.pack(pady=5)
        
        # Login form with better styling
        form_frame = ttk.Frame(self, style="TFrame")
        form_frame.grid(row=2, column=1, columnspan=2, padx=20, pady=20)
        
        # Email field
        email_frame = ttk.Frame(form_frame, style="TFrame")
        email_frame.pack(fill="x", pady=10)
        ttk.Label(email_frame, text="Email:", style="TLabel").pack(anchor="w", pady=2)
        self.email_entry = ttk.Entry(email_frame, width=40)
        self.email_entry.pack(fill="x", pady=2)
        
        # Username field
        username_frame = ttk.Frame(form_frame, style="TFrame")
        username_frame.pack(fill="x", pady=10)
        ttk.Label(username_frame, text="Username:", style="TLabel").pack(anchor="w", pady=2)
        self.username_entry = ttk.Entry(username_frame, width=40)
        self.username_entry.pack(fill="x", pady=2)
        
        # Buttons
        button_frame = ttk.Frame(form_frame, style="TFrame")
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Login", style="Primary.TButton", 
                  command=self.login).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Sign Up", 
                  command=lambda: controller.show_frame(SignupFrame)).grid(row=0, column=1, padx=10)
    
    def login(self):
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        
        if not email or not username:
            messagebox.showerror("Login Error", "Please enter both email and username.")
            return
        
        # Check if the user exists
        query = "SELECT Email_Address FROM Users WHERE Email_Address = %s AND User_Name = %s"
        result = DatabaseManager.execute_query(query, (email, username))
        
        if result:
            self.controller.set_current_user(email)
            messagebox.showinfo("Login Success", f"Welcome back, {username}!")
            self.controller.show_frame(MainMenuFrame)
        else:
            messagebox.showerror("Login Error", "Invalid email or username. Please try again.")

class SignupFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        # Header
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=1, column=1, columnspan=2, pady=20)
        
        header = ttk.Label(header_frame, text="Create New Account", style="Header.TLabel")
        header.pack(pady=10)
        
        # Signup form with improved styling
        form_frame = ttk.Frame(self, style="TFrame")
        form_frame.grid(row=2, column=1, columnspan=2, padx=20, pady=20)
        
        # Email field
        email_frame = ttk.Frame(form_frame, style="TFrame")
        email_frame.pack(fill="x", pady=8)
        ttk.Label(email_frame, text="Email:", style="TLabel").pack(anchor="w", pady=2)
        self.email_entry = ttk.Entry(email_frame, width=40)
        self.email_entry.pack(fill="x", pady=2)
        
        # Username field
        username_frame = ttk.Frame(form_frame, style="TFrame")
        username_frame.pack(fill="x", pady=8)
        ttk.Label(username_frame, text="Username:", style="TLabel").pack(anchor="w", pady=2)
        self.username_entry = ttk.Entry(username_frame, width=40)
        self.username_entry.pack(fill="x", pady=2)
        
        # Date of Birth field
        dob_frame = ttk.Frame(form_frame, style="TFrame")
        dob_frame.pack(fill="x", pady=8)
        ttk.Label(dob_frame, text="Date of Birth:", style="TLabel").pack(anchor="w", pady=2)
        self.dob_entry = DateEntry(dob_frame, width=38, date_pattern='yyyy-mm-dd', background=COLORS["primary"],
                                 foreground='white', borderwidth=2)
        self.dob_entry.pack(fill="x", pady=2)
        
        # Country field
        country_frame = ttk.Frame(form_frame, style="TFrame")
        country_frame.pack(fill="x", pady=8)
        ttk.Label(country_frame, text="Country:", style="TLabel").pack(anchor="w", pady=2)
        self.country_entry = ttk.Entry(country_frame, width=40)
        self.country_entry.pack(fill="x", pady=2)
        
        # Gender field
        gender_frame = ttk.Frame(form_frame, style="TFrame")
        gender_frame.pack(fill="x", pady=8)
        ttk.Label(gender_frame, text="Gender:", style="TLabel").pack(anchor="w", pady=2)
        
        gender_button_frame = ttk.Frame(gender_frame, style="TFrame")
        gender_button_frame.pack(fill="x", pady=2)
        
        self.gender_var = tk.StringVar()
        ttk.Radiobutton(gender_button_frame, text="Male", variable=self.gender_var, 
                       value="Male").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(gender_button_frame, text="Female", variable=self.gender_var, 
                       value="Female").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(gender_button_frame, text="Other", variable=self.gender_var, 
                       value="Other").grid(row=0, column=2, padx=10)
        self.gender_var.set("Male")  # Default selection
        
        # Buttons with better styling
        button_frame = ttk.Frame(form_frame, style="TFrame")
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Create Account", style="Primary.TButton",
                  command=self.create_account).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back to Login", 
                  command=lambda: controller.show_frame(LoginFrame)).grid(row=0, column=1, padx=10)
    
    def create_account(self):
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        dob = self.dob_entry.get_date()
        country = self.country_entry.get().strip()
        gender = self.gender_var.get()
        
        # Validation
        if not email or not username or not country:
            messagebox.showerror("Signup Error", "Please fill in all fields.")
            return
        
        # Email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Signup Error", "Please enter a valid email address.")
            return
        
        # Check if user already exists
        check_query = "SELECT Email_Address FROM Users WHERE Email_Address = %s OR User_Name = %s"
        result = DatabaseManager.execute_query(check_query, (email, username))
        
        if result:
            messagebox.showerror("Signup Error", "Email or username already exists. Please choose different ones.")
            return
        
        # Insert new user
        insert_query = """
            INSERT INTO Users (Email_Address, Date_of_birth, User_Name, Country, Gender)
            VALUES (%s, %s, %s, %s, %s)
        """
        result = DatabaseManager.execute_query(
            insert_query, 
            (email, dob.strftime('%Y-%m-%d'), username, country, gender),
            fetch=False
        )
        
        if result:
            messagebox.showinfo("Signup Success", "Account created successfully! You can now log in.")
            self.controller.show_frame(LoginFrame)
        else:
            messagebox.showerror("Signup Error", "Failed to create account. Please try again.")

class MainMenuFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        # Header with welcome message
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=1, column=1, pady=20)
        
        self.header_label = ttk.Label(header_frame, text="Oscar Nominations Database", style="Header.TLabel")
        self.header_label.pack(pady=10)
        
        self.user_label = ttk.Label(header_frame, text="Welcome, User", style="SubHeader.TLabel")
        self.user_label.pack(pady=5)
        
        # Menu options with improved styling
        menu_frame = ttk.Frame(self, style="TFrame")
        menu_frame.grid(row=2, column=1, pady=20)
        
        button_width = 35
        ttk.Button(menu_frame, text="Query Oscar Winners & Nominations", width=button_width,
                  style="Primary.TButton", command=lambda: controller.show_frame(QueryOscarsFrame)).pack(pady=12)
        
        ttk.Button(menu_frame, text="Create Your Own Nomination", width=button_width,
                  style="Primary.TButton", command=lambda: controller.show_frame(CreateNominationFrame)).pack(pady=12)
        
        ttk.Button(menu_frame, text="View Your Nominations", width=button_width,
                  style="Primary.TButton", command=lambda: controller.show_frame(UserNominationsFrame)).pack(pady=12)
        
        ttk.Button(menu_frame, text="Logout", width=button_width,
                  command=self.logout).pack(pady=20)
    
    def on_show(self):
        # Update user information when showing this frame
        if self.controller.current_user:
            query = "SELECT User_Name FROM Users WHERE Email_Address = %s"
            result = DatabaseManager.execute_query(query, (self.controller.current_user,))
            if result:
                self.user_label.config(text=f"Welcome, {result[0][0]}")
    
    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame(LoginFrame)

class QueryOscarsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        # Header with styled title
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=1, column=1, columnspan=2, pady=20)
        
        header = ttk.Label(header_frame, text="Query Oscar Information", style="Header.TLabel")
        header.pack(pady=5)
        
        subheader = ttk.Label(header_frame, text="Search for Oscar nominations and winners", style="SubHeader.TLabel")
        subheader.pack(pady=5)
        
        # Search options with improved layout
        options_frame = ttk.Frame(self, style="TFrame")
        options_frame.grid(row=2, column=1, columnspan=2, padx=20, pady=10)
        
        # By Iteration (formerly Year)
        iteration_frame = ttk.Frame(options_frame, style="TFrame")
        iteration_frame.pack(fill="x", pady=10)
        ttk.Label(iteration_frame, text="Search by Iteration:", style="TLabel").pack(anchor="w", pady=2)
        self.iteration_var = tk.StringVar()
        self.iteration_dropdown = ttk.Combobox(iteration_frame, textvariable=self.iteration_var, width=30)
        self.iteration_dropdown.pack(fill="x", pady=2)
        
        # By Category
        category_frame = ttk.Frame(options_frame, style="TFrame")
        category_frame.pack(fill="x", pady=10)
        ttk.Label(category_frame, text="Search by Category:", style="TLabel").pack(anchor="w", pady=2)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(category_frame, textvariable=self.category_var, width=30)
        self.category_dropdown.pack(fill="x", pady=2)
        
        # By Movie
        movie_frame = ttk.Frame(options_frame, style="TFrame")
        movie_frame.pack(fill="x", pady=10)
        ttk.Label(movie_frame, text="Search by Movie:", style="TLabel").pack(anchor="w", pady=2)
        self.movie_entry = ttk.Entry(movie_frame, width=30)
        self.movie_entry.pack(fill="x", pady=2)
        
        # By Person
        person_frame = ttk.Frame(options_frame, style="TFrame")
        person_frame.pack(fill="x", pady=10)
        ttk.Label(person_frame, text="Search by Person:", style="TLabel").pack(anchor="w", pady=2)
        self.person_entry = ttk.Entry(person_frame, width=30)
        self.person_entry.pack(fill="x", pady=2)
        
        # Search button
        search_button = ttk.Button(options_frame, text="Search", style="Primary.TButton", command=self.search)
        search_button.pack(pady=20)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self, style="TFrame")
        nav_frame.grid(row=4, column=1, columnspan=2, pady=10)
        
        ttk.Button(nav_frame, text="Back to Main Menu", 
                  command=lambda: controller.show_frame(MainMenuFrame)).pack()
    
    def on_show(self):
        # Populate dropdowns when showing this frame
        self.load_categories()
        self.load_iterations()
    
    def load_categories(self):
        query = "SELECT DISTINCT Award_Name FROM Nomination ORDER BY Award_Name"
        result = DatabaseManager.execute_query(query)
        
        if result:
            categories = [row[0] for row in result]
            self.category_dropdown['values'] = categories
    
    def load_iterations(self):
        query = "SELECT DISTINCT Iteration_Number FROM Nomination ORDER BY Iteration_Number DESC"
        result = DatabaseManager.execute_query(query)
        
        if result:
            iterations = [str(row[0]) for row in result]
            self.iteration_dropdown['values'] = iterations
    
    
    def search(self):
        category = self.category_var.get()
        iteration = self.iteration_var.get()
        movie = self.movie_entry.get().strip()
        person = self.person_entry.get().strip()
        
        if not category and not iteration and not movie and not person:
            messagebox.showerror("Search Error", "Please specify at least one search criteria.")
            return
        
        # Construct query based on search criteria
        query_parts = []
        params = []
        
        # Modified query to properly get winner information
        base_query = """
            SELECT 
                n.Award_Name, 
                n.Iteration_Number, 
                n.Movie_Name, 
                na.Film, 
                na.Winner as Winner,
                n.Granted
            FROM Nomination n
            LEFT JOIN Nominee_Association na ON n.Award_Name = na.Nomination_Award_Name 
                AND n.Iteration_Number = na.Nomination_Iteration_Number
        """
        
        if person:
            base_query += """
                LEFT JOIN User_Nominations un ON n.Award_Name = un.Award_Name 
                    AND n.Iteration_Number = un.Award_Iteration_Number
                LEFT JOIN Staff s ON un.Staff_FirstName = s.FirstName AND un.Staff_LastName = s.LastName
            """
            
            query_parts.append("(s.FirstName LIKE %s OR s.LastName LIKE %s)")
            params.extend([f"%{person}%", f"%{person}%"])
        
        if category:
            query_parts.append("n.Award_Name = %s")
            params.append(category)
        
        if iteration:
            query_parts.append("n.Iteration_Number = %s")
            params.append(iteration)
        
        if movie:
            query_parts.append("(n.Movie_Name LIKE %s OR na.Film LIKE %s)")
            params.extend([f"%{movie}%", f"%{movie}%"])
        
        if query_parts:
            base_query += " WHERE " + " AND ".join(query_parts)
        
        base_query += " ORDER BY n.Iteration_Number DESC, n.Award_Name"
        
        # Execute search
        results = DatabaseManager.execute_query(base_query, params)
        
        if results:
            search_results_frame = self.controller.frames[SearchResultsFrame]
            search_results_frame.display_results(results)
            self.controller.show_frame(SearchResultsFrame)
        else:
            messagebox.showinfo("Search Results", "No results found for your search criteria.")

class SearchResultsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Configure grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        # Header with styled title
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=0, column=0, pady=15)
        
        header = ttk.Label(header_frame, text="Search Results", style="Header.TLabel")
        header.pack()
        
        self.result_count = ttk.Label(header_frame, text="", style="Info.TLabel")
        self.result_count.pack(pady=5)
        
        # Results treeview with improved styling
        self.tree_frame = ttk.Frame(self, style="TFrame")
        self.tree_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Create horizontal and vertical scrollbars
        h_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scroll = ttk.Scrollbar(self.tree_frame)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("award", "iteration", "movie", "film", "winner", "granted")
        self.results_tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", 
                                        yscrollcommand=v_scroll.set,
                                        xscrollcommand=h_scroll.set)
        
        # Configure scrollbars
        v_scroll.config(command=self.results_tree.yview)
        h_scroll.config(command=self.results_tree.xview)
        
        # Configure columns
        self.results_tree.heading("award", text="Award Category")
        self.results_tree.heading("iteration", text="Iteration")
        self.results_tree.heading("movie", text="Movie")
        self.results_tree.heading("film", text="Film")
        self.results_tree.heading("winner", text="Winner")
        self.results_tree.heading("granted", text="Granted")
        
        # Set column widths
        self.results_tree.column("award", width=200, minwidth=150)
        self.results_tree.column("iteration", width=100, minwidth=80)
        self.results_tree.column("movie", width=200, minwidth=150)
        self.results_tree.column("film", width=200, minwidth=150)
        self.results_tree.column("winner", width=200, minwidth=150)
        self.results_tree.column("granted", width=80, minwidth=60)
        
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add alternating row colors
        self.results_tree.tag_configure('oddrow', background='white')
        self.results_tree.tag_configure('evenrow', background='#f0f0f0')
        
        # Navigation buttons
        nav_frame = ttk.Frame(self, style="TFrame")
        nav_frame.grid(row=3, column=0, pady=15)
        
        ttk.Button(nav_frame, text="Back to Search", 
                  command=lambda: controller.show_frame(QueryOscarsFrame)).grid(row=0, column=0, padx=10)
        ttk.Button(nav_frame, text="Back to Main Menu", 
                  command=lambda: controller.show_frame(MainMenuFrame)).grid(row=0, column=1, padx=10)
            
    def display_results(self, results):
        # Clear previous results
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        # Update result count
        self.result_count.config(text=f"Found {len(results)} results")
        
        # Add new results with alternating row colors
        for i, result in enumerate(results):
            award, iteration, movie, film, winner, granted = result
            granted_text = "Yes" if granted else "No"
            
            # Show winner name if available, otherwise show "None"
            winner_text = winner if winner else "None"
            
            # Determine row style based on even/odd
            row_tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
            
            self.results_tree.insert("", tk.END, 
                                   values=(award, iteration, movie, film, winner_text, granted_text),
                                   tags=row_tags)

class CreateNominationFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Initialize tracking variables
        self.current_iteration = None
        self.current_award = None
        self.current_film = None
        self.films = []
        self.awards = []
        self.iterations = []
        self.winners = []
        
        # Center content
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(3, weight=1)
        
        # Header with styled title
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=1, column=1, columnspan=2, pady=20)
        
        header = ttk.Label(header_frame, text="Create Your Nomination", style="Header.TLabel")
        header.pack(pady=5)
        
        subheader = ttk.Label(header_frame, text="Nominate someone for an Oscar award", style="SubHeader.TLabel")
        subheader.pack(pady=5)
        
        # Form with improved styling
        form_frame = ttk.Frame(self, style="TFrame")
        form_frame.grid(row=2, column=1, columnspan=2, padx=20, pady=10)
        
        # Iteration field
        iteration_frame = ttk.Frame(form_frame, style="TFrame")
        iteration_frame.pack(fill="x", pady=8)
        ttk.Label(iteration_frame, text="Iteration Number:", style="TLabel").pack(anchor="w", pady=2)
        self.iteration_var = tk.StringVar()
        self.iteration_dropdown = ttk.Combobox(iteration_frame, textvariable=self.iteration_var, width=40)
        self.iteration_dropdown.pack(fill="x", pady=2)
        # Bind selection event
        self.iteration_dropdown.bind("<<ComboboxSelected>>", self.on_iteration_selected)
        
        # Award Category field
        category_frame = ttk.Frame(form_frame, style="TFrame")
        category_frame.pack(fill="x", pady=8)
        ttk.Label(category_frame, text="Award Category:", style="TLabel").pack(anchor="w", pady=2)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(category_frame, textvariable=self.category_var, width=40)
        self.category_dropdown.pack(fill="x", pady=2)
        # Bind selection event
        self.category_dropdown.bind("<<ComboboxSelected>>", self.on_award_selected)
        
        # Film field
        film_frame = ttk.Frame(form_frame, style="TFrame")
        film_frame.pack(fill="x", pady=8)
        ttk.Label(film_frame, text="Film:", style="TLabel").pack(anchor="w", pady=2)
        self.film_var = tk.StringVar()
        self.film_dropdown = ttk.Combobox(film_frame, textvariable=self.film_var, width=40)
        self.film_dropdown.pack(fill="x", pady=2)
        # Bind selection event
        self.film_dropdown.bind("<<ComboboxSelected>>", self.on_film_selected)
        
        # Winner field
        winner_frame = ttk.Frame(form_frame, style="TFrame")
        winner_frame.pack(fill="x", pady=8)
        ttk.Label(winner_frame, text="Winner:", style="TLabel").pack(anchor="w", pady=2)
        self.winner_var = tk.StringVar()
        self.winner_dropdown = ttk.Combobox(winner_frame, textvariable=self.winner_var, width=40)
        self.winner_dropdown.pack(fill="x", pady=2)
        
        # Staff (Person) field
        staff_frame = ttk.Frame(form_frame, style="TFrame")
        staff_frame.pack(fill="x", pady=8)
        ttk.Label(staff_frame, text="Staff Member:", style="TLabel").pack(anchor="w", pady=2)
        self.staff_var = tk.StringVar()
        self.staff_dropdown = ttk.Combobox(staff_frame, textvariable=self.staff_var, width=40)
        self.staff_dropdown.pack(fill="x", pady=2)
        
        # Granted checkbox
        granted_frame = ttk.Frame(form_frame, style="TFrame")
        granted_frame.pack(fill="x", pady=8)
        self.granted_var = tk.BooleanVar()
        granted_check = ttk.Checkbutton(granted_frame, text="Granted", variable=self.granted_var)
        granted_check.pack(anchor="w", pady=2)
        
        # Submit button
        button_frame = ttk.Frame(form_frame, style="TFrame")
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Submit Nomination", style="Primary.TButton",
                  command=self.submit_nomination).pack(pady=5)
        
        # Navigation buttons
        nav_frame = ttk.Frame(self, style="TFrame")
        nav_frame.grid(row=4, column=1, columnspan=2, pady=10)
        
        ttk.Button(nav_frame, text="Back to Main Menu", 
                  command=lambda: controller.show_frame(MainMenuFrame)).pack()

    def on_show(self):
        # Populate dropdowns when showing this frame
        self.load_iterations()
        self.load_awards()
        # Don't load all staff here anymore - we'll load them when iteration is selected
    
    def load_iterations(self):
        query = "SELECT DISTINCT Iteration_Number FROM Nomination ORDER BY Iteration_Number DESC"
        result = DatabaseManager.execute_query(query)
        
        if result:
            self.iterations = [str(row[0]) for row in result]
            self.iteration_dropdown['values'] = self.iterations
    
    def load_awards(self):
        query = "SELECT DISTINCT Award_Name FROM Nomination ORDER BY Award_Name"
        result = DatabaseManager.execute_query(query)
        
        if result:
            self.awards = [row[0] for row in result]
            self.category_dropdown['values'] = self.awards
    
    def on_iteration_selected(self, event):
        self.current_iteration = self.iteration_var.get()
        if self.current_iteration:
            # Load all movies nominated in this iteration
            self.load_movies_for_iteration()
            # Load all staff associated with movies in this iteration
            self.load_staff_for_iteration()
        
        if self.current_iteration and self.current_award:
            self.load_films_for_award()
    
    def load_movies_for_iteration(self):
        """Load all movies nominated in the selected iteration"""
        query = """
            SELECT DISTINCT Movie_Name FROM Nomination 
            WHERE Iteration_Number = %s AND Movie_Name IS NOT NULL
            ORDER BY Movie_Name
        """
        result = DatabaseManager.execute_query(query, (self.current_iteration,))
        
        if result:
            self.films = [row[0] for row in result]
            self.film_dropdown['values'] = self.films
        else:
            self.films = []
            self.film_dropdown['values'] = []

    def load_staff_for_iteration(self):
        """Load all staff associated with movies nominated in this iteration"""
        query = """
            SELECT DISTINCT s.FirstName, s.LastName 
            FROM Staff s
            JOIN User_Nominations un ON s.FirstName = un.Staff_FirstName AND s.LastName = un.Staff_LastName
            JOIN Nomination n ON un.Award_Name = n.Award_Name AND un.Award_Iteration_Number = n.Iteration_Number
            WHERE n.Iteration_Number = %s
            UNION
            SELECT DISTINCT s.FirstName, s.LastName 
            FROM Staff s
            JOIN Nominee_Association na ON s.FirstName = na.FirstName AND s.LastName = na.LastName
            JOIN Nomination n ON na.Nomination_Award_Name = n.Award_Name AND na.Nomination_Iteration_Number = n.Iteration_Number
            WHERE n.Iteration_Number = %s
            ORDER BY LastName, FirstName
        """
        result = DatabaseManager.execute_query(query, (self.current_iteration, self.current_iteration))
        
        if result:
            staff_names = [f"{row[0]} {row[1]}" for row in result]
            self.staff_dropdown['values'] = staff_names
        else:
            # Fallback to all staff if none found for this iteration
            query_all = "SELECT DISTINCT FirstName, LastName FROM Staff ORDER BY LastName, FirstName"
            result_all = DatabaseManager.execute_query(query_all)
            if result_all:
                staff_names = [f"{row[0]} {row[1]}" for row in result_all]
                self.staff_dropdown['values'] = staff_names
            else:
                self.staff_dropdown['values'] = []
    
    def on_award_selected(self, event):
        self.current_award = self.category_var.get()
        if self.current_iteration and self.current_award:
            self.load_films_for_award()
    
    def load_films_for_award(self):
        """Load films nominated for the specific award in the selected iteration"""
        query = """
            SELECT DISTINCT Movie_Name FROM Nomination 
            WHERE Award_Name = %s AND Iteration_Number = %s AND Movie_Name IS NOT NULL
            ORDER BY Movie_Name
        """
        result = DatabaseManager.execute_query(query, (self.current_award, self.current_iteration))
        
        if result:
            self.films = [row[0] for row in result]
            self.film_dropdown['values'] = self.films
        else:
            self.films = []
            self.film_dropdown['values'] = []
    
    def on_film_selected(self, event):
        self.current_film = self.film_var.get()
        if self.current_film and self.current_iteration and self.current_award:
            self.load_winners_for_film()
    
    def load_winners_for_film(self):
        """Load winners for the selected film in the current award and iteration"""
        query = """
            SELECT DISTINCT Winner FROM Nominee_Association 
            WHERE Nomination_Award_Name = %s AND Nomination_Iteration_Number = %s AND Film = %s
            ORDER BY Winner
        """
        result = DatabaseManager.execute_query(query, (self.current_award, self.current_iteration, self.current_film))
        
        if result:
            self.winners = [row[0] for row in result if row[0]]  # Filter out None values
            self.winner_dropdown['values'] = self.winners
        else:
            self.winners = []
            self.winner_dropdown['values'] = []
    
    def submit_nomination(self):
        if not self.controller.current_user:
            messagebox.showerror("Error", "You must be logged in to create a nomination.")
            return
        
        # Get form values
        award_name = self.category_var.get()
        iteration = self.iteration_var.get()
        film = self.film_var.get()
        winner = self.winner_var.get()
        staff_fullname = self.staff_var.get().strip()
        
        # Split staff name into first and last names
        staff_fname = ""
        staff_lname = ""
        if staff_fullname:
            try:
                staff_fname, staff_lname = staff_fullname.split(" ", 1)
            except ValueError:
                messagebox.showerror("Error", "Staff name must include both first and last name.")
                return
        
        granted = self.granted_var.get()
        
        # Validation
        if not award_name or not iteration or not film:
            messagebox.showerror("Error", "Award category, iteration, and film are required fields.")
            return
        
        try:
            iteration = int(iteration)
        except ValueError:
            messagebox.showerror("Error", "Iteration must be a number.")
            return
        
        # Check if staff exists, create if not
        if staff_fname and staff_lname:
            check_staff_query = "SELECT * FROM Staff WHERE FirstName = %s AND LastName = %s"
            staff_exists = DatabaseManager.execute_query(check_staff_query, (staff_fname, staff_lname))
            
            if not staff_exists:
                # Create new staff member
                insert_staff_query = "INSERT INTO Staff (FirstName, LastName) VALUES (%s, %s)"
                DatabaseManager.execute_query(insert_staff_query, (staff_fname, staff_lname), fetch=False)
        
        # Check if nomination exists, create if not
        check_nomination_query = """
            SELECT * FROM Nomination 
            WHERE Award_Name = %s AND Iteration_Number = %s
        """
        nomination_exists = DatabaseManager.execute_query(check_nomination_query, (award_name, iteration))
        
        if not nomination_exists:
            # Create new nomination
            insert_nomination_query = """
                INSERT INTO Nomination (Award_Name, Iteration_Number, Movie_Name, Granted)
                VALUES (%s, %s, %s, %s)
            """
            DatabaseManager.execute_query(
                insert_nomination_query, 
                (award_name, iteration, film, granted),
                fetch=False
            )
        
        # Create user nomination
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_user_nomination_query = """
            INSERT INTO User_Nominations (
                Email_Address, Award_Name, Award_Iteration_Number, Staff_FirstName, 
                Staff_LastName, TimeStamp, Movie_Name, Film, Winner
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        result = DatabaseManager.execute_query(
            insert_user_nomination_query,
            (self.controller.current_user, award_name, iteration, staff_fname, 
             staff_lname, timestamp, film, film, winner),
            fetch=False
        )
        
        if result is not None:
            messagebox.showinfo("Success", "Your nomination has been submitted!")
            # Clear form fields
            self.iteration_var.set("")
            self.category_var.set("")
            self.film_var.set("")
            self.winner_var.set("")
            self.staff_var.set("")
            self.granted_var.set(False)
        else:
            messagebox.showerror("Error", "Failed to submit nomination. Please try again.")


class UserNominationsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        
        # Configure grid
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)
        self.grid_columnconfigure(0, weight=1)
        
        # Header with styled title
        header_frame = ttk.Frame(self, style="TFrame")
        header_frame.grid(row=0, column=0, pady=15)
        
        header = ttk.Label(header_frame, text="Your Nominations", style="Header.TLabel")
        header.pack()
        
        self.status_label = ttk.Label(header_frame, text="", style="Info.TLabel")
        self.status_label.pack(pady=5)
        
        # Results treeview with improved styling
        self.tree_frame = ttk.Frame(self, style="TFrame")
        self.tree_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # Create horizontal and vertical scrollbars
        h_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        v_scroll = ttk.Scrollbar(self.tree_frame)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        columns = ("id", "award", "iteration", "movie", "film", "winner", "staff", "timestamp")
        self.nominations_tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", 
                                            yscrollcommand=v_scroll.set,
                                            xscrollcommand=h_scroll.set)
        
        # Configure scrollbars
        v_scroll.config(command=self.nominations_tree.yview)
        h_scroll.config(command=self.nominations_tree.xview)
        
        # Configure columns
        self.nominations_tree.heading("id", text="ID")
        self.nominations_tree.heading("award", text="Award Category")
        self.nominations_tree.heading("iteration", text="Iteration")
        self.nominations_tree.heading("movie", text="Movie")
        self.nominations_tree.heading("film", text="Film")
        self.nominations_tree.heading("winner", text="Winner")
        self.nominations_tree.heading("staff", text="Staff")
        self.nominations_tree.heading("timestamp", text="Timestamp")
        
        # Set column widths
        self.nominations_tree.column("id", width=50, minwidth=50)
        self.nominations_tree.column("award", width=150, minwidth=150)
        self.nominations_tree.column("iteration", width=80, minwidth=80)
        self.nominations_tree.column("movie", width=150, minwidth=150)
        self.nominations_tree.column("film", width=150, minwidth=150)
        self.nominations_tree.column("winner", width=150, minwidth=150)
        self.nominations_tree.column("staff", width=150, minwidth=150)
        self.nominations_tree.column("timestamp", width=150, minwidth=150)
        
        self.nominations_tree.pack(fill=tk.BOTH, expand=True)
        
        # Add alternating row colors
        self.nominations_tree.tag_configure('oddrow', background='white')
        self.nominations_tree.tag_configure('evenrow', background='#f0f0f0')
        
        # Bind double-click event to open edit dialog
        self.nominations_tree.bind("<Double-1>", self.edit_nomination)
        
        # Button frame
        button_frame = ttk.Frame(self, style="TFrame")
        button_frame.grid(row=3, column=0, pady=15)
        
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_nomination).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Back to Main Menu", 
                  command=lambda: controller.show_frame(MainMenuFrame)).grid(row=0, column=1, padx=10)
    
    def on_show(self):
        self.load_nominations()

    def load_nominations(self):
        if not self.controller.current_user:
            self.status_label.config(text="You must be logged in to view your nominations.")
            return
        
        # Clear previous results
        for item in self.nominations_tree.get_children():
            self.nominations_tree.delete(item)
        
        # Fixed query - using correct column names
        query = """
            SELECT 
                un.ID, un.Award_Name, un.Award_Iteration_Number, un.Movie_Name, 
                un.Film, un.Winner, 
                CONCAT(IFNULL(un.Staff_FirstName,''), ' ', IFNULL(un.Staff_LastName,'')) as Staff, 
                un.TimeStamp
            FROM User_Nominations un
            WHERE un.Email_Address = %s
            ORDER BY un.TimeStamp DESC
        """
        
        results = DatabaseManager.execute_query(query, (self.controller.current_user,))
        
        if results:
            self.status_label.config(text=f"Found {len(results)} nominations")
            
            for i, result in enumerate(results):
                id, award, iteration, movie, film, winner, staff, timestamp = result
                
                # Format timestamp
                if timestamp:
                    timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                
                # Determine row style
                row_tags = ('evenrow',) if i % 2 == 0 else ('oddrow',)
                
                self.nominations_tree.insert("", tk.END, 
                                           values=(id, award, iteration, movie, film, winner, staff, timestamp),
                                           tags=row_tags)
        else:
            self.status_label.config(text="You haven't created any nominations yet.")
    
    def edit_nomination(self, event):
        # Get selected item
        selected_item = self.nominations_tree.selection()
        if not selected_item:
            return
        
        # Get nomination data
        values = self.nominations_tree.item(selected_item, 'values')
        if not values:
            return
        
        nomination_id = values[0]
        
        # Get full nomination details from database
        query = """
            SELECT 
                Award_Name, Award_Iteration_Number, Movie_Name, Film, Winner, 
                Staff_FirstName, Staff_LastName
            FROM User_Nominations
            WHERE ID = %s AND Email_Address = %s
        """
        
        result = DatabaseManager.execute_query(query, (nomination_id, self.controller.current_user))
        
        if not result:
            messagebox.showerror("Error", "Could not retrieve nomination details.")
            return
        
        # Create edit dialog
        edit_window = tk.Toplevel(self)
        edit_window.title("Edit Nomination")
        edit_window.configure(bg=COLORS["bg"])
        edit_window.geometry("500x550")
        edit_window.resizable(False, False)
        
        # Form frame
        form_frame = ttk.Frame(edit_window, style="TFrame")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Get current values
        award, iteration, movie, film, winner, staff_fname, staff_lname = result[0]
        
        # Award Category (disabled)
        category_frame = ttk.Frame(form_frame, style="TFrame")
        category_frame.pack(fill="x", pady=8)
        ttk.Label(category_frame, text="Award Category:", style="TLabel").pack(anchor="w", pady=2)
        category_entry = ttk.Entry(category_frame, width=40)
        category_entry.insert(0, award)
        category_entry.configure(state="readonly")
        category_entry.pack(fill="x", pady=2)
        
        # Iteration field (disabled)
        iteration_frame = ttk.Frame(form_frame, style="TFrame")
        iteration_frame.pack(fill="x", pady=8)
        ttk.Label(iteration_frame, text="Iteration Number:", style="TLabel").pack(anchor="w", pady=2)
        iteration_entry = ttk.Entry(iteration_frame, width=40)
        iteration_entry.insert(0, iteration)
        iteration_entry.configure(state="readonly")
        iteration_entry.pack(fill="x", pady=2)
        
        # Movie field
        movie_frame = ttk.Frame(form_frame, style="TFrame")
        movie_frame.pack(fill="x", pady=8)
        ttk.Label(movie_frame, text="Movie Name:", style="TLabel").pack(anchor="w", pady=2)
        movie_entry = ttk.Entry(movie_frame, width=40)
        movie_entry.insert(0, movie if movie else "")
        movie_entry.pack(fill="x", pady=2)
        
        # Film field
        film_frame = ttk.Frame(form_frame, style="TFrame")
        film_frame.pack(fill="x", pady=8)
        ttk.Label(film_frame, text="Film:", style="TLabel").pack(anchor="w", pady=2)
        film_entry = ttk.Entry(film_frame, width=40)
        film_entry.insert(0, film if film else "")
        film_entry.pack(fill="x", pady=2)
        
        # Winner field
        winner_frame = ttk.Frame(form_frame, style="TFrame")
        winner_frame.pack(fill="x", pady=8)
        ttk.Label(winner_frame, text="Winner:", style="TLabel").pack(anchor="w", pady=2)
        winner_entry = ttk.Entry(winner_frame, width=40)
        winner_entry.insert(0, winner if winner else "")
        winner_entry.pack(fill="x", pady=2)
        
        # Staff First Name field
        staff_fname_frame = ttk.Frame(form_frame, style="TFrame")
        staff_fname_frame.pack(fill="x", pady=8)
        ttk.Label(staff_fname_frame, text="Staff First Name:", style="TLabel").pack(anchor="w", pady=2)
        staff_fname_entry = ttk.Entry(staff_fname_frame, width=40)
        staff_fname_entry.insert(0, staff_fname if staff_fname else "")
        staff_fname_entry.pack(fill="x", pady=2)
        
        # Staff Last Name field
        staff_lname_frame = ttk.Frame(form_frame, style="TFrame")
        staff_lname_frame.pack(fill="x", pady=8)
        ttk.Label(staff_lname_frame, text="Staff Last Name:", style="TLabel").pack(anchor="w", pady=2)
        staff_lname_entry = ttk.Entry(staff_lname_frame, width=40)
        staff_lname_entry.insert(0, staff_lname if staff_lname else "")
        staff_lname_entry.pack(fill="x", pady=2)
        
        # Button frame
        button_frame = ttk.Frame(form_frame, style="TFrame")
        button_frame.pack(pady=15)
        
        # Save function
        def save_changes():
            # Get updated values
            updated_movie = movie_entry.get().strip()
            updated_film = film_entry.get().strip()
            updated_winner = winner_entry.get().strip()
            updated_staff_fname = staff_fname_entry.get().strip()
            updated_staff_lname = staff_lname_entry.get().strip()
            
            # Validation
            if not updated_movie:
                messagebox.showerror("Error", "Movie Name is required.")
                return
            
            # Check if staff exists, create if not
            if updated_staff_fname and updated_staff_lname:
                check_staff_query = "SELECT * FROM Staff WHERE FirstName = %s AND LastName = %s"
                staff_exists = DatabaseManager.execute_query(check_staff_query, (updated_staff_fname, updated_staff_lname))
                
                if not staff_exists:
                    # Create new staff member
                    insert_staff_query = "INSERT INTO Staff (FirstName, LastName) VALUES (%s, %s)"
                    DatabaseManager.execute_query(insert_staff_query, (updated_staff_fname, updated_staff_lname), fetch=False)
            
            # Update nomination
            update_query = """
                UPDATE User_Nominations
                SET Movie_Name = %s, Film = %s, Winner = %s, Staff_FirstName = %s, Staff_LastName = %s
                WHERE ID = %s AND Email_Address = %s
            """
            
            result = DatabaseManager.execute_query(
                update_query,
                (updated_movie, updated_film, updated_winner, updated_staff_fname, updated_staff_lname,
                 nomination_id, self.controller.current_user),
                fetch=False
            )
            
            if result is not None:
                messagebox.showinfo("Success", "Nomination updated successfully!")
                edit_window.destroy()
                self.load_nominations()  # Refresh the list
            else:
                messagebox.showerror("Error", "Failed to update nomination.")
        
        ttk.Button(button_frame, text="Save Changes", style="Primary.TButton",
                  command=save_changes).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="Cancel", 
                  command=edit_window.destroy).grid(row=0, column=1, padx=10)
    
    def delete_nomination(self):
        # Get selected item
        selected_item = self.nominations_tree.selection()
        if not selected_item:
            messagebox.showinfo("Info", "Please select a nomination to delete.")
            return
        
        # Get nomination ID
        nomination_id = self.nominations_tree.item(selected_item, 'values')[0]
        
        # Confirm deletion
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this nomination?")
        if not confirm:
            return
        
        # Delete nomination
        delete_query = "DELETE FROM User_Nominations WHERE ID = %s AND Email_Address = %s"
        result = DatabaseManager.execute_query(
            delete_query,
            (nomination_id, self.controller.current_user),
            fetch=False
        )
        
        if result is not None:
            messagebox.showinfo("Success", "Nomination deleted successfully!")
            self.load_nominations()  # Refresh the list
        else:
            messagebox.showerror("Error", "Failed to delete nomination.")

# Launch the application
if __name__ == "__main__":
    app = OscarNominationsApp()
    app.mainloop()