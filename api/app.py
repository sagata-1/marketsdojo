import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import pytz
import logging
from helpers import apology, commodity_list, login_required, lookup, usd, answer, total_computation, admin_required, list_lookup
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy

# Configure application
app = Flask(__name__)
encoded_password = quote_plus("Saucepan03@!")

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
# SQLAlchemy configuration
app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{encoded_password}@db.krvuffjhmqiyerbpgqtv.supabase.co:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure Flask-Session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "sqlalchemy"
# Initialize SQLAlchemy and Flask-Session
db_temp = SQLAlchemy(app)
app.config['SESSION_SQLALCHEMY'] = db_temp
app.config['SESSION_SQLALCHEMY_TABLE'] = 'flask_sessions'  # Name of the table for sessions
# Assign the session to the app
Session(app)
# Configure database connection
con = psycopg2.connect(dbname="postgres", user="postgres", password="Saucepan03@!", host="db.krvuffjhmqiyerbpgqtv.supabase.co")
db = con.cursor(cursor_factory=RealDictCursor)


# @app.after_request
# def after_request(response):
#     """Ensure responses aren't cached"""
#     response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     response.headers["Expires"] = 0
#     response.headers["Pragma"] = "no-cache"
#     return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s)", (session["user_id"],)
    )
    portfolio = db.fetchall()
    for stock in portfolio:
        db.execute(
            "UPDATE portfolios set price = (%s) WHERE user_id = (%s) AND stock_symbol = (%s) and type = (%s)",
            (lookup(stock["stock_symbol"], stock["type"])["price"],
            session["user_id"],
            stock["stock_symbol"],
            stock["type"])
        )
        con.commit()
    db.execute("SELECT * FROM users WHERE id = (%s)", (session["user_id"],))
    cash = db.fetchall()
    cash = float(cash[0]["cash"])
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s) ORDER BY stock_symbol",
        (session["user_id"],)
    )
    portfolio = db.fetchall()
    print(portfolio)

    assets = []
    total = cash
    for stock in portfolio:
        total += stock["price"] * stock["num_shares"]
        assets.append(stock["stock_symbol"])
    db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"],))
    username = db.fetchall()
    username = username[0]["username"]
    pl = round(total - 10000, 2)
    percent_pl = round((pl / 10000) * 100, 2)
    types = ["Stock (Equity)", "Forex", "Index", "ETF", "CFD", "Commodity"]
    return render_template("index.html", portfolio=portfolio, cash=usd(cash), total=usd(total), username=username, assets=assets, pl = pl, percent_pl = percent_pl, types=types)

@app.route("/portfolio_api")
@login_required
def portfolio_api():
    # Current request format: https://www.marketsdojo.com/portfolio_api and only works when we have a logged in user, with Flask Session handling the login
    # Request possible format: https://www.marketsdojo.com/portfolio_api?user_id=USERID
    """Show portfolio of stocks"""
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s)", (session["user_id"],)
    )
    portfolio = db.fetchall()
    for stock in portfolio:
        db.execute(
            "UPDATE portfolios set price = (%s) WHERE user_id = (%s) AND stock_symbol = (%s) and type = (%s)",
            (lookup(stock["stock_symbol"], stock["type"])["price"],
            session["user_id"],
            stock["stock_symbol"],
            stock["type"])
        )
        con.commit()
    db.execute("SELECT * FROM users WHERE id = (%s)", (session["user_id"],))
    cash = db.fetchall()
    cash = float(cash[0]["cash"])
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s) ORDER BY stock_symbol",
        (session["user_id"],)
    )
    portfolio = db.fetchall()
    total = cash
    for stock in portfolio:
        total += stock["price"] * stock["num_shares"]
    db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"],))
    username = db.fetchall()
    username = username[0]["username"]
    pl = round(total - 10000, 2)
    percent_pl = round((pl / 10000) * 100, 2)
    types = ["Stock (Equity)", "Forex", "Index", "ETF", "CFD", "Commodity"]
    data = {"portfolio": portfolio, "cash": usd(cash), "total": usd(total), "starting_amt": 10000, "username": username, "pl": pl, "percent_pl": percent_pl, "types": types}
    return data

# @app.route("/stocks", methods=["GET", "POST"])
# @login_required
# def stocks():
#     if request.method == "GET":
#         stocks = list_lookup("stock")
#         return render_template("stocks.html", stocks=stocks)

@app.route("/commodity", methods=["GET"])
@login_required
def commodity():
    if request.method == "GET":
        commodities = commodity_list()
        return render_template("commodity.html", commodities=commodities)
    
# api route to get commodities list
@app.route("/commodity_api", methods=["GET"])
@login_required
def commodity_api():
    # Current endpoint: https://www.marketsdojo.com/commodity_api
    # TODO- Cache list
    if request.method == "GET":
        commodities = commodity_list()
        data = {"commodities": commodities}
        return data

@app.route("/learn", methods=["GET", "POST"])
@login_required
def learn():
    if request.method == "POST":
        question = request.form.get("symbol")
        _answer = answer(question)
        session["answer"] = _answer
        session["question"] = question
        return redirect("/")
    db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"],))
    username = db.fetchall()
    username = username[0]["username"]
    db.execute("SELECT * FROM progress WHERE user_id = (%s)", (session["user_id"],))
    progress = db.fetchall()
    progress = progress[0]
    assets = []
    return render_template("learn.html", username=username, progress=progress)

@app.route("/learn_api", methods=["GET", "POST"])
@login_required
def learn_api():
    if request.method == "POST":
        question = request.form.get("symbol")
        _answer = answer(question)
        session["answer"] = _answer
        session["question"] = question
        return redirect("/")
    db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"],))
    username = db.fetchall()
    username = username[0]["username"]
    db.execute("SELECT * FROM progress WHERE user_id = (%s)", (session["user_id"],))
    progress = db.fetchall()
    progress = progress[0]
    assets = []
    data=[{"username": username, "progress": progress}]
    return jsonify(data)

@app.route("/update", methods = ["POST"])
@login_required
def update():
    complete = request.form.get("complete")
    # Error handling (Can't allow progress to exceed 1)
    db.execute("SELECT * FROM progress WHERE user_id = (%s)", (session["user_id"],))
    progress = db.fetchall()
    progress = progress[0]
    if progress["total_prog"]== 1:
        return redirect("/learn")
    if complete == "1":
        if progress["mod_1"] == 1:
            return redirect("/learn")
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_1 = mod_1 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/4,
                session["user_id"])
            )
        con.commit()
    elif complete == "2":
        if progress["mod_2"] == 1:
            return redirect("/learn")
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_2 = mod_2 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/3,
                session["user_id"])
            )
        con.commit()
    elif complete == "3":
        if progress["mod_3"] == 1:
            return redirect("/learn")
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_3 = mod_3 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/2,
                session["user_id"])
            )
        con.commit()
    elif complete == "4":
        if progress["mod_4"] == 1:
            return redirect("/learn")
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_4 = mod_4 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/2,
                session["user_id"])
            )
        con.commit()
    elif complete == "5":
        if progress["mod_5"] == 1:
            return redirect("/learn")
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_5 = mod_5 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/2,
                session["user_id"])
            )
        con.commit()
    else:
        if progress["mod_6"] == 1:
            return redirect("/learn")
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_6 = mod_6 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/4,
                session["user_id"])
            )
        con.commit()
    return redirect("/learn")

@app.route("/adminupdate", methods=["GET", "POST"])
@admin_required
def adminupdate():
    if request.method == "GET":
        course_name = request.args.get("course")
        db.execute("SELECT * FROM admin_courses_duplicate WHERE course_name = (%s)", (course_name, ))
        course = db.fetchall()
        return course

@app.route("/adminlearn", methods=["GET", "POST"])
@admin_required
def adminlearn():
    if request.method == "GET":
        db.execute("SELECT * FROM progress WHERE user_id = (%s)", (session["user_id"],))
        progress = db.fetchall()
        progress = progress[0]
        db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"],))
        username = db.fetchall()
        username = username[0]["username"]
        return render_template("adminlearn.html", username=username, progress=progress)
    



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    symbol = request.form.get("symbol").upper()
    num_shares = request.form.get("shares")
    type = request.form.get("type")
    stock = lookup(symbol, type)
    if not stock:
        return apology("Invalid Symbol", 400)
    if stock["exchange"] and type and (stock["exchange"] == "FOREX" and type != "Forex" or stock["exchange"] != "FOREX" and type == "Forex"):
        return apology("Asset Type does not match symbol", 400)
    if not num_shares.isdigit():
        return apology("Invalid Shares", 400)
    num_shares = int(num_shares)
    if num_shares < 1:
        return apology("Invalid Shares", 400)
    price = stock["price"]
    # Create a datetime object in UTC
    utc_dt = datetime.datetime.now(pytz.timezone("UTC"))

    # Convert the datetime object to UTC-5 timezone
    utc_minus_5_dt = utc_dt.astimezone(pytz.timezone('Etc/GMT+5'))
    open_time = utc_minus_5_dt.replace(hour=8, minute=30)
    close_time = utc_minus_5_dt.replace(hour=17, minute=0)
    time = utc_minus_5_dt
    # Error checking (i.e. missing symbol, too many shares bought etc)
    # Can only buy when market is open
    if type and type != "Forex":
        if open_time.date().weekday() == 5 or open_time.date().weekday() == 6:
            return apology("Cannot trade on a weekend!", 400)
        if time < open_time or time > close_time:
            return apology("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes) ", 400)
    else:
        if open_time.date().weekday() == 5 or (open_time.date().weekday() == 6 and time.hour < 18) or (open_time.date().weekday == 4 and time.hour > 16):
            return apology("You cannot trade in the Forex market from 6:00 pm Friday to 4:00 pm on Sunday! (1 hour after the market closes and upto 1 hour before the market opens)", 400)
    db.execute("SELECT * FROM users WHERE id = (%s)", (session["user_id"],))
    user = db.fetchall()
    if (num_shares * price) > user[0]["cash"]:
        return apology("Cannot Afford", 400)
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s) AND stock_symbol = (%s) AND type = (%s)",
        (session["user_id"],
        symbol,
        type)
    )
    portfolio = db.fetchall()
    # Start a stock for a new user if it doesn't exist
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    if (len(portfolio)) == 0:
        db.execute(
            "INSERT INTO portfolios(user_id, stock_name, stock_symbol, price, num_shares, time_bought, type) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (session["user_id"],
            stock["name"],
            stock["symbol"],
            price,
            num_shares,
            time,
            type)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            stock["symbol"],
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), bought = bought + 1  WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    # Update current portfolio
    else:
        db.execute(
            "UPDATE portfolios SET price = (%s), num_shares = num_shares + (%s) WHERE user_id = (%s) and stock_symbol = (%s)",
            (price,
            num_shares,
            session["user_id"],
            stock["symbol"])
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            stock["symbol"],
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), bought = bought + 1 WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    db.execute (
        "SELECT bought FROM users WHERE id = (%s)", (session["user_id"], )
    )
    bought = db.fetchall()
    bought = bought[0]["bought"]
    if (bought == 1):
        flash("Achievement Unlocked! First Virtual Buy")
    else:
        flash("Bought!")
    return redirect("/")

@app.route("/buy_api", methods=["GET"])
@login_required
def buy_api():
    """Buy shares of stock"""
    # Current endpoint: https://www.marketsdojo.com/buy_api?symbol=STOCKSYMBOL&shares=NUMSHARES&type=STOCKTYPE
    # This will conduct a complete buy operation on the backend and then send you back to https://www.marketsdojo.com/portfolio_api
    # Expects user to be logged in, and types is one of ["Forex", "Stock (Equity)", "CFD", "Commodity", "Index", "ETF"]
    symbol = request.args.get("symbol")
    num_shares = request.args.get("shares")
    type = request.args.get("type")
    if symbol == None or num_shares == None or type == None:
        return {400: "Missing or incorrect query parameters"}
    symbol = symbol.upper()
    stock = lookup(symbol, type)
    if not stock:
        return {400:"Invalid Symbol"}
    if stock["exchange"] and type and (stock["exchange"] == "FOREX" and type != "Forex" or stock["exchange"] != "FOREX" and type == "Forex"):
        return {400: "Asset Type does not match symbol"}
    if not num_shares.isdigit():
        return {400: "Invalid Shares"}
    num_shares = int(num_shares)
    if num_shares < 1:
        return {400: "Invalid Shares"}
    price = stock["price"]
    # Create a datetime object in UTC
    utc_dt = datetime.datetime.now(pytz.timezone("UTC"))

    # Convert the datetime object to UTC-5 timezone
    utc_minus_5_dt = utc_dt.astimezone(pytz.timezone('Etc/GMT+5'))
    open_time = utc_minus_5_dt.replace(hour=8, minute=30)
    close_time = utc_minus_5_dt.replace(hour=17, minute=0)
    time = utc_minus_5_dt
    # Error checking (i.e. missing symbol, too many shares bought etc)
    # Can only buy when market is open
    if type and type != "Forex":
        if open_time.date().weekday() == 5 or open_time.date().weekday() == 6:
            return {400: "Cannot trade on a weekend!"}
        if time < open_time or time > close_time:
            return {400: "Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)"}
    else:
        if open_time.date().weekday() == 5 or (open_time.date().weekday() == 6 and time.hour < 18) or (open_time.date().weekday == 4 and time.hour > 16):
            return {400: "You cannot trade in the Forex market from 6:00 pm Friday to 4:00 pm on Sunday! (1 hour after the market closes and upto 1 hour before the market opens)"}
    db.execute("SELECT * FROM users WHERE id = (%s)", (session["user_id"],))
    user = db.fetchall()
    if (num_shares * price) > user[0]["cash"]:
        return {400: "Cannot Afford"}
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s) AND stock_symbol = (%s) AND type = (%s)",
        (session["user_id"],
        symbol,
        type)
    )
    portfolio = db.fetchall()
    # Start a stock for a new user if it doesn't exist
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    if (len(portfolio)) == 0:
        db.execute(
            "INSERT INTO portfolios(user_id, stock_name, stock_symbol, price, num_shares, time_bought, type) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (session["user_id"],
            stock["name"],
            stock["symbol"],
            price,
            num_shares,
            time,
            type)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            stock["symbol"],
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), bought = bought + 1  WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    # Update current portfolio
    else:
        db.execute(
            "UPDATE portfolios SET price = (%s), num_shares = num_shares + (%s) WHERE user_id = (%s) and stock_symbol = (%s)",
            (price,
            num_shares,
            session["user_id"],
            stock["symbol"])
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            stock["symbol"],
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), bought = bought + 1 WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    db.execute (
        "SELECT bought FROM users WHERE id = (%s)", (session["user_id"], )
    )
    bought = db.fetchall()
    bought = bought[0]["bought"]
    return redirect("/portfolio_api")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    db.execute(
        "SELECT * FROM history WHERE user_id = (%s) ORDER BY time_of_transaction",
        (session["user_id"],)
    )
    user_history = db.fetchall()
    db.execute("SELECT username FROM users")
    usernames = db.fetchall()
    for username in usernames:
        username["total"] = total_computation(username["username"])[0]
    usernames = sorted(usernames, key=lambda a: a["total"], reverse=True)
    usernames = usernames[:10]
    db.execute (
        "SELECT bought FROM users WHERE id = (%s)", (session["user_id"], )
    )
    bought = db.fetchall()
    bought = bought[0]["bought"]
    db.execute (
        "SELECT sold FROM users WHERE id = (%s)", (session["user_id"], )
    )
    sold = db.fetchall()
    sold = sold[0]["sold"]
    return render_template("history.html", history=user_history, usernames=usernames, size=len(usernames), bought=bought, sold=sold)

@app.route("/advanced", methods=["GET", "POST"])
@login_required
def advanced():
    if request.method == "POST":
        question = request.form.get("symbol")
        _answer = answer(question)
        return render_template("answer_c.html", _answer=_answer)
    return render_template("advanced.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        db.execute("SELECT * FROM users WHERE username = (%s)", (request.form.get("username"),))
        rows = db.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    symbol = request.form.get("symbol")
    type = request.form.get("type")
    stock = lookup(symbol, type)
    if not stock:
        return apology("Invalid Symbol", 400)
    types = ["Stock (Equity)", "Forex", "Index", "ETF", "Commodity"]
    return render_template("quoted.html", stock=stock, types=types, type=type)

@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin():
    if request.method == "GET":
        db.execute("SELECT course_name FROM admin_courses_duplicate")
        courses = db.fetchall()
        names = []
        for course in courses:
            names.append(course["course_name"])
        names = set(names)
        db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"], ))
        username = db.fetchall()
        username = username[0]["username"]
        
        return render_template("admin.html", courses=names, username=username)
    course_name = request.form['courseName']
    num_modules = request.form['numModules']
    course_data = {'courseName': course_name, 'modules': {}, "numModules": num_modules}
    for key in request.form:
        if key.startswith('module-'):
            course_data['modules'][key] = request.form[key]
    for lesson, article in course_data["modules"].items():
        db.execute("INSERT INTO admin_courses_duplicate(course_name, lesson_name, article) VALUES (%s, %s, %s)", (course_name, lesson, article))
    con.commit()
    db.execute("SELECT course_name FROM admin_courses_duplicate")
    courses = db.fetchall()
    names = []
    for course in courses:
        names.append(course["course_name"])
    names = set(names)
    db.execute("SELECT username FROM users WHERE id = (%s)", (session["user_id"], ))
    username = db.fetchall()
    username = username[0]["username"]
    return render_template("admin.html", courses=names, username=username)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return ("Please provide a username", 400)
        db.execute("SELECT username FROM users WHERE username = (%s)", (username,))
        database_username = db.fetchall()
        if (
            len(database_username)
            > 0
        ):
            return apology("username already exists", 400)
        password = request.form.get("password")
        password_check = request.form.get("confirmation")
        if password != password_check or not password:
            return apology("passwords do not match / did not enter a password", 400)
        # Register user
        db.execute("INSERT INTO users (username, hash) VALUES(%s, %s)", (username,generate_password_hash(password)))
        con.commit()
        db.execute("SELECT id FROM users WHERE username = (%s)", (username,))
        user = db.fetchall()
        # Log user in  after registration
        db.execute("INSERT INTO progress (user_id, total_prog, mod_1, mod_2, mod_3, mod_4, mod_5, mod_6) VALUES(%s, 0, 0, 0, 0, 0, 0, 0)", (user[0]["id"],))
        con.commit()
        session["user_id"] = user[0]["id"]
        flash("Registered!")
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    db.execute(
        "SELECT stock_symbol FROM portfolios WHERE user_id = (%s)", (session["user_id"],)
    )
    valid_symbols = db.fetchall()
    if request.method == "GET":
        return render_template("sell.html", symbols=valid_symbols)
    type = request.form.get("type")
    symbol = request.form.get("symbol").upper()
    num_shares = request.form.get("shares")
    db.execute(
        "SELECT * FROM portfolios WHERE stock_symbol = (%s) AND user_id = (%s) AND type = (%s)",
        (symbol,
        session["user_id"],
        type)
    )
    stock = db.fetchall()
    db.execute("SELECT type FROM portfolios WHERE stock_symbol = (%s)", (symbol,))
    types = db.fetchall()
    type_ans = types[0]["type"]
    if type != type_ans:
        return apology("Asset Type does not match symbol", 400)
    if len(stock) != 1:
        return apology("Invalid Symbol", 400)
    if not num_shares.isdigit():
        return apology("Invalid Shares", 400)
    num_shares = (int(num_shares)) * -1
    if num_shares > 0:
        return apology("Invalid Shares", 400)
    if stock[0]["num_shares"] + num_shares < 0:
        return apology("Too many shares", 400)
     # Create a datetime object in UTC
    utc_dt = datetime.datetime.now(pytz.timezone("UTC"))

    # Convert the datetime object to UTC-5 timezone
    utc_minus_5_dt = utc_dt.astimezone(pytz.timezone('Etc/GMT+5'))
    open_time = utc_minus_5_dt.replace(hour=8, minute=30)
    close_time = utc_minus_5_dt.replace(hour=17, minute=0)
    time = utc_minus_5_dt
    # Error checking (i.e. missing symbol, too many shares sold etc)
    if type and type != "Forex":
        if open_time.date().weekday() == 5 or open_time.date().weekday() == 6:
            return apology("Cannot trade on a weekend!", 400)
        if time < open_time or time > close_time:
            return apology("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes) ", 400)
    else:
        if open_time.date().weekday() == 5 or (open_time.date().weekday() == 6 and time.hour < 18) or (open_time.date().weekday == 4 and time.hour > 16):
            return apology("You cannot trade in the Forex market from 6:00 pm Friday to 4:00 pm on Sunday! (1 hour after the market closes and upto 1 hour before the market opens)", 400)
    # Keep track of sells
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    # Update current portfolio
    price = lookup(symbol, type)["price"]
    if stock[0]["num_shares"] + num_shares == 0:
        db.execute(
            "DELETE FROM portfolios WHERE user_id = (%s) AND stock_symbol = (%s)",
            (session["user_id"],
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), sold = sold + 1 WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    else:
        db.execute(
            "UPDATE portfolios SET price = (%s), num_shares = num_shares + (%s) WHERE user_id = (%s) AND stock_symbol = (%s)",
            (price,
            num_shares,
            session["user_id"],
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), sold = sold + 1 WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    db.execute (
        "SELECT sold FROM users WHERE id = (%s)", (session["user_id"], )
    )
    sold = db.fetchall()
    sold = sold[0]["sold"]
    if sold == 1:
        flash("Achievement Unlocked! First Virtual Sell")
    else:
        flash("Sold!")
    return redirect("/")

@app.route("/sell_api", methods=["GET"])
@login_required
def sell_api():
    """Sell shares of stock"""
    # Current endpoint: https://www.marketsdojo.com/sell_api?symbol=STOCKSYMBOL&shares=NUMSHARES&type=STOCKTYPE
    # This will conduct a complete buy operation on the backend and then send you back to https://www.marketsdojo.com/portfolio_api
    # Expects user to be logged in, and types is one of ["Forex", "Stock (Equity)", "CFD", "Commodity", "Index", "ETF"]
    type = request.args.get("type")
    symbol = request.args.get("symbol")
    num_shares = request.args.get("shares")
    if not type or not symbol or not num_shares:
        return {400: "Missing or inccorect query parameters!"}
    symbol = symbol.upper()
    db.execute(
        "SELECT * FROM portfolios WHERE stock_symbol = (%s) AND user_id = (%s) AND type = (%s)",
        (symbol,
        session["user_id"],
        type)
    )
    stock = db.fetchall()
    db.execute("SELECT type FROM portfolios WHERE stock_symbol = (%s)", (symbol,))
    types = db.fetchall()
    type_ans = types[0]["type"]
    if type != type_ans:
        return {400: "Asset Type does not match symbol"}
    if len(stock) != 1:
        return {400:"Invalid Symbol"}
    if not num_shares.isdigit():
        return {400:"Invalid Shares"}
    num_shares = (int(num_shares)) * -1
    if num_shares > 0:
        return {400: "Invalid Shares"}
    if stock[0]["num_shares"] + num_shares < 0:
        return {400: "Too many shares"}
     # Create a datetime object in UTC
    utc_dt = datetime.datetime.now(pytz.timezone("UTC"))

    # Convert the datetime object to UTC-5 timezone
    utc_minus_5_dt = utc_dt.astimezone(pytz.timezone('Etc/GMT+5'))
    open_time = utc_minus_5_dt.replace(hour=8, minute=30)
    close_time = utc_minus_5_dt.replace(hour=17, minute=0)
    time = utc_minus_5_dt
    # Error checking (i.e. missing symbol, too many shares sold etc)
    if type and type != "Forex":
        if open_time.date().weekday() == 5 or open_time.date().weekday() == 6:
            return {400: "Cannot trade on a weekend!"}
        if time < open_time or time > close_time:
            return {400: "Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes) "}
    else:
        if open_time.date().weekday() == 5 or (open_time.date().weekday() == 6 and time.hour < 18) or (open_time.date().weekday == 4 and time.hour > 16):
            return {400: "You cannot trade in the Forex market from 6:00 pm Friday to 4:00 pm on Sunday! (1 hour after the market closes and upto 1 hour before the market opens)"}
    # Keep track of sells
    time = time.strftime("%Y-%m-%d %H:%M:%S")
    # Update current portfolio
    price = lookup(symbol, type)["price"]
    if stock[0]["num_shares"] + num_shares == 0:
        db.execute(
            "DELETE FROM portfolios WHERE user_id = (%s) AND stock_symbol = (%s)",
            (session["user_id"],
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), sold = sold + 1 WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    else:
        db.execute(
            "UPDATE portfolios SET price = (%s), num_shares = num_shares + (%s) WHERE user_id = (%s) AND stock_symbol = (%s)",
            (price,
            num_shares,
            session["user_id"],
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (session["user_id"],
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), sold = sold + 1 WHERE id = (%s)",
            (num_shares * price,
            session["user_id"])
        )
        con.commit()
    db.execute (
        "SELECT sold FROM users WHERE id = (%s)", (session["user_id"], )
    )
    sold = db.fetchall()
    sold = sold[0]["sold"]
    return redirect("/portfolio_api")

@app.route("/password-change", methods=["GET", "POST"])
@login_required
def password_change():
    if request.method == "GET":
        return render_template("password_change.html")
    db.execute("SELECT * FROM users WHERE id = (%s)", (session["user_id"],))
    prev_password = db.fetchall()
    prev_password = prev_password[0]["hash"]
    if not check_password_hash(prev_password, request.form.get("curr_password")):
        return apology("Invalid Current Password", 400)
    new_password = request.form.get("new_password")
    if new_password != request.form.get("confirmation") or not new_password:
        return apology(
            "Please make sure you have confirmed your password / chosen a new password",
            400,
        )
    db.execute(
        "UPDATE users SET hash = (%s) WHERE id = (%s)",
        (generate_password_hash(new_password),
        session["user_id"])
    )
    con.commit()
    flash("Password Changed!")
    return redirect("/")

@app.route("/landing", methods=["GET"])
def layout():
    return render_template("trial_1.html")

@app.route("/achievements", methods=["GET"])
@login_required
def achievements():
    db.execute (
        "SELECT bought FROM users WHERE id = (%s)", (session["user_id"], )
    )
    bought = db.fetchall()
    bought = bought[0]["bought"]
    db.execute (
        "SELECT sold FROM users WHERE id = (%s)", (session["user_id"], )
    )
    sold = db.fetchall()
    sold = sold[0]["sold"]
    return render_template("achievements.html", bought=bought, sold=sold)

# # Function to create tables (including the "flask_sessions" table)
# def create_tables():
#     with app.app_context():
#         db_temp.create_all()

if __name__ == "__main__":
    # create_tables()
    app.run()