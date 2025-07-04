from flask import flash, Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from helper import account_change, account_create, get_db, login_required, profile_history, scoring, search_db
import logging
import random
import string

app = Flask(__name__)
app.secret_key = "CS50_FiNaL_pRoJeCt"
app.config["TEMPLATES_AUTO_RELOAD"] = True  
app.config["SESSION_PERMANENT"] = False 
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

logging.basicConfig(
    filename='error.log',           # Log file name
    level=logging.ERROR,            # Only log errors and higher (ERROR, CRITICAL)
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

# Configure session to use filesystem (instead of signed cookies)
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/extra", methods=["GET", "POST"])
def extra():
    """Show extra long game page."""
    if request.method == "POST":

        """Handle form submission for the extra game."""
        # Initial scores for both players (ie. 50 points is max to be scored)
        p1_score = 50
        p2_score = 50
        
        # Get the letter from the form
        letter = request.form.get("letter")
        
        # Gets player 1 answers into a list
        p1_list = [
            request.form.get("p1answer1").lower(),
            request.form.get("p1answer2").lower(),
            request.form.get("p1answer3").lower(),
            request.form.get("p1answer4").lower(),
            request.form.get("p1answer5").lower()
            ]
        
        # Gets player 2 answers into a list
        p2_list = [
            request.form.get("p2answer1").lower(),
            request.form.get("p2answer2").lower(),
            request.form.get("p2answer3").lower(),
            request.form.get("p2answer4").lower(),
            request.form.get("p2answer5").lower()
        ]
        
        # Function to calculate the scores of each player
        scores = scoring(p1_score, p2_score, p1_list, p2_list, letter)
          
        # Unpack the scores for scores and status of players
        p1_score = scores[0]
        p2_score = scores[1]    
        
        # Identifies winner and loser
        if p1_score > p2_score:
            p1_status = "win"
            p2_status = "lose"
        elif p1_score < p2_score:
            p1_status = "lose"
            p2_status = "win"
        else:
            p1_status = "tie"
            p2_status = "tie"
        
        # Store the scores and lists in the session
        session["p1_score"] = p1_score
        session["p2_score"] = p2_score
        session["p1_list"] = p1_list
        session["p2_list"] = p2_list
        
        # Open the database connection
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Logging users data into the database
            # If no players, close the database connection
            if session["username1"] == "Player 1":
                print("No players, closing database connection")
                pass
            # If 1 player, send data to database and close connection
            elif session["username1"] != "Player 1":
                cursor.execute("INSERT INTO game_records (GameSelect, Letter, WinLossTie1, WinLossTie2, Username1, Username2, WordList1, WordList2, Score1, Score2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (session["gameselect"], letter, p1_status, p2_status, session["username1"], session["username2"], str(p1_list), str(p2_list), p1_score, p2_score))
                db.commit()
                print("Player 1 & Player 2 data inserted successfully")
                print("Data inserted successfully")
                    
        except Exception as e:
            db.rollback()
            print("Error inserting data:", e)
        
        print("Database connection closed")

        # Render the results page
        return redirect(url_for("results"))
    
    else:
        """GET for extra game page"""

        # Generate a random letter for the game
        random_letter = random.choice(string.ascii_lowercase)
        
        # Get all data into 1 list
        all_data = []
        data = {"gameselect": session.get("gameselect"), "p1": session.get("username1"), "p2": session.get("username2"), "letter": random_letter, "timer": 60}
        all_data.append(data)
        
        # Render template with the random letter, player names and timer
        return render_template("extra.html", all_data=all_data)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Getting the game option selected from index page
        # 1 = Quick, 2 = Extra Time, 3 = Long
        # Saving to session and redirecting to login page
        if request.form.get("playgame") == "1":
            session["gameselect"] = "Quick"
            return redirect(url_for("login"))
        
        if request.form.get("playgame") == "2":
            session["gameselect"] = "Extra Time"
            return redirect(url_for("login"))
        
        if request.form.get("playgame") == "3":
            session["gameselect"] = "Long"
            return redirect(url_for("login"))
        
    else:
        """Show the main page."""
        # Clears session if not first landing on page and opening fresh
        session.clear()
        return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        
        # Gets the option selected from page to process
        option = request.form.get("r_login")
        
        # Get game option chosen from index
        gameselect = session.get("gameselect")
        
        # Get user input if there
        user1 = request.form.get("username1")
        pass1 = request.form.get("password1")
        user2 = request.form.get("username2")
        pass2 = request.form.get("password2")
        
        # Pre-assigning session
        session["username1"] = "Player 1"
        session["username2"] = "Player 2"

        # Possible game play scenerios & saving to session
        if gameselect == "Quick":
            # Starts Quick game with no players
            if option == "1":
                return redirect(url_for("quick"))
            
            # Starts Quick game with player 1
            elif option == "2":
                # Checks player credentials
                user_pass = search_db(user1, pass1)
                if user_pass == [1, 2, 4]:
                    flash("Invalid username and/or password")
                    return redirect(url_for("login"))
                
                # Save to session & redirect to game page
                session["username1"] = user1
                return redirect(url_for("quick"))
            
            # Starts Quick game with 2 players
            elif option == "3":
                # Checks first player credentials
                user_pass = search_db(user1, pass1)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user1}")
                    return redirect(url_for("login"))

                
                # Checks second player credentials
                user_pass = search_db(user2, pass2)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user2}")
                    return redirect(url_for("login"))
                
                # Save to session & redirect to game page
                session["username1"] = user1
                session["username2"] = user2
                return redirect(url_for("quick"))
        
        if gameselect == "Extra Time":
            #Starts Extra Time game with no players
            if option == "1":
                # Save to session & redirect to game page
                return redirect(url_for("extra"))
            
            # Starts Extra Time game with player 1
            elif option == "2":
                # Checks player credentials
                user_pass = search_db(user1, pass1)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user1}")
                    return redirect(url_for("login"))
                
                # Save to session & redirect to game page
                session["username1"] = user1
                return redirect(url_for("extra"))
        
            # Starts Extra Time game with 2 players
            elif option == "3":
                # Checks first player credentials
                user_pass = search_db(user1, pass1)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user1}")
                    return redirect(url_for("login"))
                
                # Checks second player credentials
                user_pass = search_db(user2, pass2)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user2}")
                    return redirect(url_for("login"))

                # Save to session & redirect to game page
                session["username1"] = user1
                session["username2"] = user2                
                return redirect(url_for("extra"))
        
        if gameselect == "Long":
            #Starts Long game with no players
            if option == "1":
                # Save to session & redirect to game page
                return redirect(url_for("long"))
        
            # Starts Long game with one player
            elif option == "2":
                # Checks player credentials
                user_pass = search_db(user1, pass1)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user1}")
                    return redirect(url_for("login"))

                # Save to session & redirect to game page
                session["username1"] = user1
                return redirect(url_for("long"))
        
            # Starts Long game with two players
            elif option == "3":
                # Checks first player
                user_pass = search_db(user1, pass1)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user1}")
                    return redirect(url_for("login"))
                
                # Checks second player
                user_pass = search_db(user2, pass2)
                if user_pass == [1, 2, 4]:
                    flash(f"Invalid username and/or password for {user2}")
                    return redirect(url_for("login"))

                # Save to session & redirect to game page
                session["username1"] = user1
                session["username2"] = user2        
                return redirect(url_for("long"))
        
        flash("Something went wrong. Refresh and try again.")
        return redirect(url_for("login"))

    else:
        """Render the login page."""
        # Get the game option chosen from index through session
        gameselect = session.get("gameselect")
        return render_template("login.html", gameselect=gameselect)

@app.route("/logout")
def logout():
    """Log user out."""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/long", methods=["GET", "POST"])
def long():
    """Show long game page."""
    if request.method == "POST":
        # Gets letters from form       
        letter = request.form.get("letter")

        letters = [x.strip() for x in letter.split(",")]
        
        # get inputs
        p1_list = [
            request.form.get("p1answer1").lower(),
            request.form.get("p1answer2").lower(),
            request.form.get("p1answer3").lower(),
            request.form.get("p1answer4").lower(),
            request.form.get("p1answer5").lower(),
            request.form.get("p1answer6").lower(),
            request.form.get("p1answer7").lower(),
            request.form.get("p1answer8").lower(),
            request.form.get("p1answer9").lower(),
            request.form.get("p1answer10").lower(),
            request.form.get("p1answer11").lower(),
            request.form.get("p1answer12").lower(),
            request.form.get("p1answer13").lower(),
            request.form.get("p1answer14").lower(),
            request.form.get("p1answer15").lower(),
            ]
                
        p2_list = [
            request.form.get("p2answer1").lower(),
            request.form.get("p2answer2").lower(),
            request.form.get("p2answer3").lower(),
            request.form.get("p2answer4").lower(),
            request.form.get("p2answer5").lower(),
            request.form.get("p2answer6").lower(),
            request.form.get("p2answer7").lower(),
            request.form.get("p2answer8").lower(),
            request.form.get("p2answer9").lower(),
            request.form.get("p2answer10").lower(),
            request.form.get("p2answer11").lower(),
            request.form.get("p2answer12").lower(),
            request.form.get("p2answer13").lower(),
            request.form.get("p2answer14").lower(),
            request.form.get("p2answer15").lower(),
        ]
        # Session the lists for the game
        session["p1_list"] = p1_list
        session["p2_list"] = p2_list
             
        # Changes the lists into rows of 5 for scoring
        p1_list_rows = [p1_list[i:i + 5] for i in range(0, len(p1_list), 5)]
        p2_list_rows = [p2_list[i:i + 5] for i in range(0, len(p2_list), 5)]
        
        # Functions to calculate the scores of each player
        score1 = scoring(50, 50, p1_list_rows[0], p2_list_rows[0], letters[0])
        score2 = scoring(50, 50, p1_list_rows[1], p2_list_rows[1], letters[1])
        score3 = scoring(50, 50, p1_list_rows[2], p2_list_rows[2], letters[2])
        
        # Get the scores of the players        
        p1_score = score1[0] + score2[0] + score3[0]
        p2_score = score1[1] + score2[1] + score3[1]
        
        # Assigning winner and loser        
        if p1_score > p2_score:
            p1_status = "win"
            p2_status = "lose"
        elif p1_score < p2_score:
            p1_status = "lose"
            p2_status = "win"
        else:
            p1_status = "tie"
            p2_status = "tie"
            
        # Store the scores and lists in the session
        session["p1_score"] = p1_score
        session["p2_score"] = p2_score
        session["p1_list"] = p1_list
        session["p2_list"] = p2_list
        
        # Open the database connection
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Logging users data into the database
            # If no players, close the database connection
            if session["username1"] == "Player 1":
                print("No players, closing database connection")
                pass
            # If 1 player, send data to database and close connection
            elif session["username1"] != "Player 1":
                cursor.execute("INSERT INTO game_records (GameSelect, Letter, WinLossTie1, WinLossTie2, Username1, Username2, WordList1, WordList2, Score1, Score2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (session["gameselect"], letter, p1_status, p2_status, session["username1"], session["username2"], str(p1_list), str(p2_list), p1_score, p2_score))
                db.commit()
                print("Player 1 & Player 2 data inserted successfully")
                print("Data inserted successfully")
                    
        except Exception as e:
            db.rollback()
            print("Error inserting data:", e)
        
        print("Database connection closed")

        # Render the results page
        return redirect(url_for("results"))

    else:
        """GET for long game page"""
        # Generate a random letter for the game
        random_letter1 = random.choice(string.ascii_lowercase)
        random_letter2 = random.choice(string.ascii_lowercase)
        random_letter3 = random.choice(string.ascii_lowercase)
        
        # Format the letters with spaces
        spaced_letters = f"{random_letter1}, {random_letter2}, {random_letter3}"

        # Get all data into 1 list
        all_data = []
        data = {"gameselect": session.get("gameselect"), "p1": session.get("username1"), "p2": session.get("username2"), "letter": spaced_letters, "timer": 60}
        all_data.append(data)
        
        # Render template with the random letter, player names and timer
        return render_template("long.html", all_data=all_data)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Show user profile."""
    if request.method == "POST":     
        # Assign values
        email = request.form.get("change_email").strip() if request.form.get("change_email") else None
        password = request.form.get("change_pass").strip() if request.form.get("change_pass") else None
        confirm = request.form.get("confirm").strip() if request.form.get("confirm") else None
        
        # Function for checking user inputs
        change = account_change(session["user_id"], email, password, confirm)
        
        # Possible outputs of function
        if change == 0.5:
            flash("Email not in correct format")
            return redirect(url_for("profile"))
        elif change == 1:
            flash("Password not matching. Try again.")
            return redirect(url_for("profile"))
        elif change == 2:
            flash("Password Successfully changed")
            return redirect(url_for("profile"))
        elif change == 3:
            flash("Email Successfully changed")
            return redirect(url_for("profile"))
        elif change == 4:
            flash("Email & password successfully changed")
            return redirect(url_for("profile"))
        elif change == 5:
            flash("Something went wrong. Try again.")
            return redirect(url_for("profile"))
            
        return redirect("/profile")

    else:
        """Load user profile."""
        # Get the username from the session
        username = session.get("user_id")
        
        # Run helper function to get profile history
        all_data = profile_history(username)
        
        if all_data == 1:
            flash("Could not load data. Sign out and sign in again.")
            return redirect(url_for("profile"))
        
        return render_template("profile.html", all_data=all_data)

@app.route("/quick", methods=["GET", "POST"])
def quick():
    """Show quick game page."""
    if request.method == "POST":

        """Handle form submission for the quick game."""
        # Initial scores for both players (ie. 50 points is max to be scored)
        p1_score = 50
        p2_score = 50
        
        # Get the letter from the form
        letter = request.form.get("letter")
        
        # Gets player 1 answers into a list
        p1_list = [
            request.form.get("p1answer1").lower(),
            request.form.get("p1answer2").lower(),
            request.form.get("p1answer3").lower(),
            request.form.get("p1answer4").lower(),
            request.form.get("p1answer5").lower()
            ]
        
        # Gets player 2 answers into a list
        p2_list = [
            request.form.get("p2answer1").lower(),
            request.form.get("p2answer2").lower(),
            request.form.get("p2answer3").lower(),
            request.form.get("p2answer4").lower(),
            request.form.get("p2answer5").lower()
        ]
        
        # Function to calculate the scores of each player
        scores = scoring(p1_score, p2_score, p1_list, p2_list, letter)
                    
        # Unpack the scores for scores and status of players
        p1_score = scores[0]
        p2_score = scores[1]    
        
        # Identifies winner and loser
        if p1_score > p2_score:
            p1_status = "win"
            p2_status = "lose"
        elif p1_score < p2_score:
            p1_status = "lose"
            p2_status = "win"
        else:
            p1_status = "tie"
            p2_status = "tie"
        
        # Store the scores and lists in the session
        session["p1_score"] = p1_score
        session["p2_score"] = p2_score
        session["p1_list"] = p1_list
        session["p2_list"] = p2_list
        
        # Open the database connection
        db = get_db()
        cursor = db.cursor()
        
        try:
            # Logging users data into the database
            # If no players, close the database connection
            if session["username1"] == "Player 1":
                print("No players, closing database connection")
                pass
            # If 1 player, send data to database and close connection
            elif session["username1"] != "Player 1":
                cursor.execute("INSERT INTO game_records (GameSelect, Letter, WinLossTie1, WinLossTie2, Username1, Username2, WordList1, WordList2, Score1, Score2) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (session["gameselect"], letter, p1_status, p2_status, session["username1"], session["username2"],str(p1_list), str(p2_list), p1_score, p2_score))
                db.commit()
                print("Player 1 & Player 2 data inserted successfully")
                print("Data inserted successfully")
                    
        except Exception as e:
            db.rollback()
            print("Error inserting data:", e)
        
        print("Database connection closed")

        # Render the results page
        return redirect(url_for("results"))
    
    else:
        """Show quick game page."""
        # Generate a random letter for the game
        random_letter = random.choice(string.ascii_lowercase)
        
        # Get all data into 1 list
        all_data = []
        data = {"gameselect": session.get("gameselect"), "p1": session.get("username1"), "p2": session.get("username2"), "letter": random_letter, "timer": 30}
        all_data.append(data)
        
        # Render template with the random letter, player names and timer
        return render_template("quick.html", all_data=all_data)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        # Forget any user_id
        session.clear()

        create = account_create(username, email, password, confirm)
        
        if create == 0:
            session["user_id"] = username
            flash("Welcome to the game! This is your profile page.")
            return redirect(url_for("profile"))
        elif create == 1:
            flash("Username not provided")
            return redirect(url_for("register"))
        elif create == 2:
            flash ("Username not the correct length. Must be between 3 and 20 characters")
            return redirect(url_for("register"))
        elif create == 3:
            flash("Email not provided")
            return redirect(url_for("register"))  
        elif create == 4:
            flash("Email not in correct format. Must contain @ and .")
        elif create == 5:
            flash("Email not in correct format. Must be like: test@domain.com")
            return redirect(url_for("register"))
        elif create == 6:
            flash("Password not provided.")
            return redirect(url_for("register"))
        elif create == 7:
            flash("Password not the correct length. Must be between 8 and 20 characters.")
            return redirect(url_for("register"))
        elif create == 8:
            flash("Password and Confirmation must match.")
            return redirect(url_for("register"))
        elif create == 9:
            flash("Username and password cannot be the same.")
            return redirect(url_for("register"))
        elif create == 10:
            flash("Username and email cannot be the same.")
            return redirect(url_for("register"))
        elif create == 11:
            flash("Confirmation not provided.")
            return redirect(url_for("register"))
        elif create == 12:
            flash("Email and password cannot be the same.")
            return redirect(url_for("register"))
        elif create == 13:
            flash("Username or email already exists. Please choose another.")
            return redirect(url_for("register"))
        elif create == 14:
            flash("Something went wrong. Thats on us. Try again.")
            return redirect(url_for("register"))
        elif create == 15:
            flash("An unexpected error occured. Please refresh and try again.")
            return redirect(url_for("register"))

        # Redirect user to home page
        flash("Something went wrong. Try again.")
        return redirect(url_for("register"))

    else:
        return render_template("register.html")

@app.route ("/results")
def results():
        # Get the all game details from session
        # Get all data into 1 list      
        all_data = []
        data = {"gameselect": session.get("gameselect"), "p1": session.get("username1"), "p2": session.get("username2"), "p1_score": session.get("p1_score"), "p2_score": session.get("p2_score"), "p1_list": session.get("p1_list"), "p2_list": session.get("p2_list")}
        all_data.append(data)
        
        # Render template with player names, scores, lists and winner  
        return render_template("results.html", all_data=all_data)

@app.route("/signin", methods=["GET", "POST"])
def signin():
    """Log user in."""
    if request.method == "POST":
        # Forget any user in session
        session.clear()

        username = request.form.get("username")
        password = request.form.get("password")
    
        user = search_db(username, password)
        
        # Ensure username was submitted
        if user == 1:
            flash("Username not provided.")
            return redirect("signin")

        # Ensure password was submitted
        elif user == 2:
            flash("Password not provided.")
            return redirect(url_for("signin"))
        
        # Error with database
        elif user == 3:
            flash("Error: Username does not exist.")
            return redirect(url_for("signin"))
        
        # Wrong password
        elif user == 4:
            flash("Incorrect password.")
            return redirect(url_for("signin"))

        # Remember which user has logged in
        session["user_id"] = username

        # Redirect user to home page
        return redirect("/profile")

    else:
        # Render the sign-in page
        return render_template("signin.html")