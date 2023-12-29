import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
import openai
import psycopg2
from psycopg2.extras import RealDictCursor

from flask import redirect, render_template, session
from functools import wraps

con = psycopg2.connect(dbname="postgres", user="postgres", password="Saucepan03@!", host="db.krvuffjhmqiyerbpgqtv.supabase.co")
db = con.cursor(cursor_factory=RealDictCursor)

def apology(message, code=400):
    """Render message as an apology to user."""
    var = escape(message)
    return render_template("apology.html", top=code, bottom=var), code

def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("%s", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

def apology_test(message, code=400):
    """Render message as an apology to user."""
    return (message, code)

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/landing")
        return f(*args, **kwargs)

    return decorated_function


def list_lookup(type):
    url = "https://financialmodelingprep.com/api/v3/stock/list?apikey=6fbceaefb411ee907e9062098ef0fd66"
    try:
        response = requests.get(url,
        cookies={"session": str(uuid.uuid4())},
        headers={"User-Agent": "python-requests", "Accept": "*/*"},
        )

    # Get available asset list
        quotes = response.json()
        supported = []
        for quote in quotes:
            if quote["type"] == type and quote["price"] != None:
                price = round(float(quote["price"]), 2)
                supported.append({"name": quote["name"], "symbol": quote["symbol"], "price": price, "exchange": quote["exchangeShortName"]})
        return supported
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None
def commodity_list():
    url = "https://financialmodelingprep.com/api/v3/quotes/commodity?apikey=6fbceaefb411ee907e9062098ef0fd66"
    try:
        response = requests.get(url,
        cookies={"session": str(uuid.uuid4())},
        headers={"User-Agent": "python-requests", "Accept": "*/*"},
        )
    # Get available asset list
        commodities = response.json()
        res = []
        for commoditiy in commodities:
            price = round(float(commoditiy["price"]), 2)
            res.append({"name": commoditiy["name"], "symbol": commoditiy["symbol"], "price": price, "exchange": commoditiy["exchange"]})
        return res
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None

def admin_required(f):
    """
    Decorate admin routes to require admin to be logged in.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        elif session.get("user_id") != 18:
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function

def total_computation(username):
    db.execute(
        "SELECT * FROM portfolios WHERE user_id IN (SELECT id FROM users WHERE username = (%s))", (username, )
    )
    portfolio = db.fetchall()
    db.execute("SELECT * FROM users WHERE username = (%s)", (username,))
    cash = db.fetchall()
    cash = float(cash[0]["cash"])
    total = cash
    for stock in portfolio:
        total += stock["price"] * stock["num_shares"]
    total = round(total, 2)
    return total, cash

def leaderboard():
    """Test function for leaderboard"""
    db.execute("SELECT username FROM users LIMIT 10")
    usernames = db.fetchall()
    for username in usernames:
        username["total"] = total_computation(username["username"])[0]
    usernames = sorted(usernames, key=lambda a: a["total"], reverse=True)
    return usernames

def buy_test(symbol, user_id, num_shares, type, time):
    """Buy shares of stock"""
    stock = lookup(symbol, type)
    # Error checking (i.e. missing symbol, too many shares bought etc)
    if not stock:
        return 400
    if stock["exchange"] and (stock["exchange"] == "FOREX" and type != "Forex" or stock["exchange"] != "FOREX" and type == "Forex"):
        return 400
    if not num_shares.isdigit():
        return 400
    num_shares = int(num_shares)
    if num_shares < 0:
        return 400

    # Convert the datetime object to UTC-5 timezone
    utc_minus_5_dt = time
    open_time = utc_minus_5_dt.replace(hour=8, minute=30)
    close_time = utc_minus_5_dt.replace(hour=17, minute=0)
    # Error checking (i.e. missing symbol, too many shares sold etc)
    if type and type != "Forex":
        if time.date().weekday() == 5 or time.date().weekday() == 6:
            return 1
        if time.time() < open_time.time() or time.time() > close_time.time():
            return 2
    else:
        if time.date().weekday() == 5 or (time.date().weekday() == 6 and time.hour < 18) or (time.date().weekday == 4 and time.hour > 16):
            return 3
    price = stock["price"]
    db.execute("SELECT * FROM users WHERE id = (%s)", (user_id,))
    user = db.fetchall()
    if (num_shares * price) > user[0]["cash"]:
        return 400
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s) AND stock_symbol = (%s)",
        (user_id,
        symbol)
    )
    portfolio = db.fetchall()
    # Start a stock for a new user if it doesn't exist
    if (len(portfolio)) == 0:
        db.execute(
            "INSERT INTO portfolios(user_id, stock_name, stock_symbol, price, num_shares, time_bought, type) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (user_id,
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
            (user_id,
            stock["symbol"],
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), bought = bought + 1 WHERE id = (%s)",
            (num_shares * price,
            user_id)
        )
        con.commit()
        return 200
    # Update current portfolio
    else:
        db.execute(
            # Fixed bug- update on pythonanywere
            "UPDATE portfolios SET price = (%s), num_shares = num_shares + (%s) WHERE user_id = (%s) and stock_symbol = (%s)",
            (price,
            num_shares,
            user_id,
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (user_id,
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), bought = bought + 1 WHERE id = (%s)",
            (num_shares * price,
            user_id)
        )
        con.commit()
        return 200

def sell_test(symbol, user_id, num_shares, type, time):
    """Sell shares of stock"""
    db.execute(
        "SELECT stock_symbol FROM portfolios WHERE user_id = (%s)", (user_id,)
    )
    valid_symbols = db.fetchall()
    db.execute(
        "SELECT * FROM portfolios WHERE stock_symbol = (%s) AND user_id = (%s)",
        (symbol,
        user_id)
    )
    stock = db.fetchall()
    # Error checking (i.e. missing symbol, too many shares sold etc)
    if len(stock) != 1:
        return 400
    if not num_shares.isdigit():
        return 400
    num_shares = (int(num_shares)) * -1
    if num_shares > 0:
        return 400
    if stock[0]["num_shares"] + num_shares < 0:
        return 400
    utc_minus_5_dt = time
    open_time = utc_minus_5_dt.replace(hour=8, minute=30)
    close_time = utc_minus_5_dt.replace(hour=17, minute=0)
    # Error checking (i.e. missing symbol, too many shares sold etc)
    if type and type != "Forex":
        if time.date().weekday() == 5 or time.date().weekday() == 6:
            return 1
        if time.time() < open_time.time() or time.time() > close_time.time():
            return 2
    else:
        if time.date().weekday() == 5 or (time.date().weekday() == 6 and time.hour < 18) or (time.date().weekday == 4 and time.hour > 16):
            return 3
    # Keep track of sells
    # Update current portfolio
    price = lookup(symbol, type)["price"]
    if stock[0]["num_shares"] + num_shares == 0:
        db.execute(
            "DELETE FROM portfolios WHERE user_id = (%s) AND stock_symbol = (%s)",
            (user_id,
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (user_id,
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), sold = sold + 1 WHERE id = (%s)",
            (num_shares * price,
            user_id)
        )
        con.commit()
        return 200
    else:
        db.execute(
            "UPDATE portfolios SET price = (%s), num_shares = num_shares + (%s) WHERE user_id = (%s) AND stock_symbol = (%s)",
            (price,
            num_shares,
            user_id,
            symbol)
        )
        con.commit()
        db.execute(
            "INSERT INTO history(user_id, stock_symbol, price, num_shares, time_of_transaction) VALUES(%s, %s, %s, %s, %s)",
            (user_id,
            symbol,
            price,
            num_shares,
            time)
        )
        con.commit()
        db.execute(
            "UPDATE users SET cash = cash - (%s), sold = sold + 1 WHERE id = (%s)",
            (num_shares * price,
            user_id)
        )
        con.commit()
        return 200

def lookup(symbol, type):
    """Look up quote for symbol."""

    # Prepare API request
    symbol = symbol.upper()
    end = datetime.datetime.now(pytz.timezone("US/Eastern"))
    start = end - datetime.timedelta(days=7)

    # Financial Modeling Prep API
    if (type == "CFD"):
        url = f"https://marketdata.tradermade.com/api/v1/live?api_key=XZas9_pK9fByyYTKXbUa&currency={symbol}"
    else:
        url = f"https://financialmodelingprep.com/api/v3/quote/{symbol}?apikey=6fbceaefb411ee907e9062098ef0fd66"
    # url = (
    #     f"https://query1.finance.yahoo.com/v7/finance/download/{urllib.parse.quote_plus(symbol)}"
    #     f"%speriod1={int(start.timestamp())}"
    #     f"&period2={int(end.timestamp())}"
    #     f"&interval=1d&events=history&includeAdjustedClose=true"
    # )

    metal_dict = {
        "XAUUSD": "Gold",
        "XAGUSD": "Silver",
        "XPTUSD": "Platinum",
        "XPDUSD": "Palladium"
    }

    # Query API
    try:
        response = requests.get(url,
        cookies={"session": str(uuid.uuid4())},
        headers={"User-Agent": "python-requests", "Accept": "*/*"},
        )
    # CSV header: Date,Open,High,Low,Close,Adj Close,Volume
        quotes = response.json()
        if type == "CFD":
            quotes = quotes["quotes"][0]
            price = round(float(quotes["mid"]), 2)
            if quotes.get("instrument"):
                return {"name": quotes["instrument"], "price": price, "symbol": quotes["instrument"], "exchange": "CFD"}
            else:
                return {"name": metal_dict[symbol], "price": price, "symbol": symbol, "exchange": "CFD"}
        # quotes.reverse()
        else:
            price = round(float(quotes[0]["price"]), 2)
            return {"name": quotes[0]["name"], "price": price, "symbol": quotes[0]["symbol"], "exchange": quotes[0]["exchange"]}
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

def answer(question):
    """Get answer to user question"""
    openai.api_key = "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"
    prompt = question
    response = openai.completions.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000
    )
    response = response.choices[0].text

    return response

def update_test(complete, id):
    # Error handling (Can't allow progress to exceed 1)
    db.execute("SELECT * FROM progress WHERE user_id = (%s)", (id,))
    progress = db.fetchall()
    progress = progress[0]
    if progress["total_prog"]== 1:
        return 1
    if complete == "1":
        if progress["mod_1"] == 1:
            return 2
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_1 = mod_1 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/4,
                id)
            )
        con.commit()
    elif complete == "2":
        if progress["mod_2"] == 1:
            return 3
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_2 = mod_2 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/3,
                id)
            )
        con.commit()
    elif complete == "3":
        if progress["mod_3"] == 1:
            return 4
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_3 = mod_3 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/2,
                id)
            )
        con.commit()
    elif complete == "4":
        if progress["mod_4"] == 1:
            return 5
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_4 = mod_4 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/2,
                id)
            )
        con.commit()
    elif complete == "5":
        if progress["mod_5"] == 1:
            return 6
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_5 = mod_5 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/2,
                id)
            )
        con.commit()
    else:
        if progress["mod_6"] == 1:
            return 7
        db.execute(
                "UPDATE progress SET total_prog = total_prog + (%s), mod_6 = mod_6 + (%s)  WHERE user_id = (%s)",
                (1/17,
                 1/4,
                id)
            )
        con.commit()
    return 200