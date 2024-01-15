from helpers import lookup
from helpers import apology_test
from helpers import total_computation
from helpers import leaderboard
from helpers import buy_test, sell_test, update_test, login_api, register_api, portfolio_api
from datetime import datetime, timedelta, timezone
import psycopg2
from psycopg2.extras import RealDictCursor


con = psycopg2.connect(dbname="postgres", user="postgres", password="Saucepan03@!", host="db.krvuffjhmqiyerbpgqtv.supabase.co")
db = con.cursor(cursor_factory=RealDictCursor)

def test_portfolio():
    assert(portfolio_api("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6IkFybWFuIEphc3VqYSIsImlhdCI6MTcwNDE5MDI5MiwianRpIjoiMWI4N2Q1OTQtNWVkMy00ZDk3LWEzNTAtMGJlMzhlOTU4NzA1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MjYsIm5iZiI6MTcwNDE5MDI5MiwiY3NyZiI6IjBlNTBjMTZjLTNjMWItNDY0Ny1hYWFlLTgwMDY3OTdiYWU2YSIsImV4cCI6MTcwNDE5MTE5Mn0.WC6XDZs3tVyEHT8y3WN0SVxEUVkAoBdKKCmfzF6OVlk") == 
           {
            "cash": "$10,000.00",
            "percent_pl": 0.0,
            "pl": 0.0,
            "portfolio": [],
            "starting_amt": 10000,
            "total": "$10,000.00",
            "types": [
                "Stock (Equity)",
                "Forex",
                "Index",
                "ETF",
                "CFD",
                "Commodity"
            ],
            "username": "Arman Jasuja"
})
    
def test_login():
    assert(login_api({"email":"ajasuja1@jhu.edu", "password": "abcdefg"}) == {"username":"Arman Jasuja", "user_id": 26, "email": "ajasuja1@jhu.edu", "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6IkFybWFuIEphc3VqYSIsImlhdCI6MTcwNDE5MDI5MiwianRpIjoiMWI4N2Q1OTQtNWVkMy00ZDk3LWEzNTAtMGJlMzhlOTU4NzA1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MjYsIm5iZiI6MTcwNDE5MDI5MiwiY3NyZiI6IjBlNTBjMTZjLTNjMWItNDY0Ny1hYWFlLTgwMDY3OTdiYWU2YSIsImV4cCI6MTcwNDE5MTE5Mn0.WC6XDZs3tVyEHT8y3WN0SVxEUVkAoBdKKCmfzF6OVlk"})
    assert(login_api({"email":"ajasuja1@jhu.edu", "password": "abcdef"}) == {"error": {"code": 403, "message": "Incorrect email and/or password"}})
    assert(login_api({"emai":"ajasuja1@jhu.edu", "password": "abcdefg"}) == {"error": {"code": 403, "message": "email not provided"}})
    assert(login_api({"email":"ajasuja1@jhu.edu", "passwor": "abcdefg"}) == {"error": {"code": 403, "message": "Did not enter a password"}})
    

def test_update():
    db.execute("UPDATE progress set total_prog = 0.882352941176471, mod_5 = 0 WHERE user_id = (%s)", (22, ))
    con.commit()
    assert(update_test("1", 21) == 1)
    assert(update_test("1", 22) == 2)
    assert(update_test("2", 22) == 3)
    assert(update_test("3", 22) == 4)
    assert(update_test("4", 22) == 5)
    assert(update_test("6", 22) == 7)
    assert(update_test("5", 22) == 200)
    db.execute("SELECT mod_5 FROM progress WHERE user_id = (%s)", (22, ))
    mod5p = db.fetchall()
    mod5p = mod5p[0]["mod_5"]
    assert(mod5p == 0.5)
    db.execute("UPDATE progress set total_prog = 0.882352941176471, mod_5 = 0 WHERE user_id = (%s)", (22, ))
    con.commit()
    db.execute("SELECT mod_5 FROM progress WHERE user_id = (%s)", (22, ))
    mod5p = db.fetchall()
    mod5p = mod5p[0]["mod_5"]
    assert(mod5p == 0)
    

def test_buy_sell():
    utc_minus_5 = timezone(-timedelta(hours=5))
    valid_time = datetime(2023, 12, 18, 15, 30, tzinfo=utc_minus_5)
    post_trading_time = datetime(2023, 12, 18, 17, 30, tzinfo=utc_minus_5)
    pre_trading_time = datetime(2023, 12, 18, 7, 30, tzinfo=utc_minus_5)
    weekend_1 = datetime(2023, 12, 17, 10, 30, tzinfo=utc_minus_5)
    weekend_2 = datetime(2023, 12, 16, 10, 30, tzinfo=utc_minus_5)
    one_min_before_trading = datetime(2023, 12, 18, 8, 29, tzinfo=utc_minus_5)
    one_min_after_trading = datetime(2023, 12, 18, 17, 1, tzinfo=utc_minus_5)
    midnight_check = datetime(2023, 12, 18, 0, 0, tzinfo=utc_minus_5)
    
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s)", (2, )
    )
    portfolio = db.fetchall()
    db.execute (
        "SELECT bought FROM users WHERE id = (%s)", (2, )
    )
    bought = db.fetchall()
    bought = bought[0]["bought"]
    db.execute (
        "SELECT sold FROM users WHERE id = (%s)", (2, )
    )
    sold = db.fetchall()
    sold = sold[0]["sold"]
    assert(bought > 0)
    assert(sold > 0)
    assert(len(portfolio) == 0)
    # Test buy capabilities- datetime kept correct, testing other errors
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", valid_time) == ({"symbol": "TSLA", "num_shares": 5, "type": "Stock (Equity)"}, 200))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "GOOG", 1000000, "Stock (Equity)", valid_time) == ("Cannot afford", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Forex", valid_time) == ("Asset type does not match symbol", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "MYREUR", 5, "Stock (Equity)", valid_time) == ("Asset type does not match symbol", 400))
    # assert(buy_test("", "AAPL", "5", "CFD", valid_time) == 200)
    # Now test edge cases of datetime (invalid times)
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", post_trading_time) == ("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", one_min_after_trading) == ("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", one_min_before_trading) == ("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", midnight_check) == ("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", pre_trading_time) == ("Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", weekend_1) == ("Cannot trade on a weekend!", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "TSLA", 5, "Stock (Equity)", weekend_2) == ("Cannot trade on a weekend!", 400))
    assert(buy_test("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTcwNDIwNTkwNSwianRpIjoiYzAxNzliZTUtNjFiNS00ZjAxLTgwZjItNGIxZmRhMDg0ODhmIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJpZCI6MiwidXNlcm5hbWUiOiJ0ZXN0In0sIm5iZiI6MTcwNDIwNTkwNSwiY3NyZiI6Ijk3YjcyMThiLTg0YWQtNDc0NC04NWUzLTBiNDlhNDEwNzUxZiIsImV4cCI6MTcwNDIwNjgwNX0.Uf6eODQaCqmT5dF_URHqXnc3raPnjntEI_Snm1M0dlI", "MYREUR", 5, "Forex", weekend_1) == ("You cannot trade in the Forex market from 6:00 pm Friday to 4:00 pm on Sunday! (1 hour after the market closes and upto 1 hour before the market opens)", 400))
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", post_trading_time) == 2)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", one_min_after_trading) == 2)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", one_min_before_trading) == 2)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", midnight_check) == 2)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", pre_trading_time) == 2)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", weekend_1) == 1)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", weekend_2) == 1)
    # assert(sell_test("MYREUR", "2", "5", "Forex", weekend_1) == 400)
    # assert(sell_test("AAPL", "2", "5", "CFD", valid_time) == 200)
    db.execute(
        "SELECT * FROM portfolios WHERE user_id = (%s)", (2, )
    )
    portfolio = db.fetchall()
    db.execute (
        "SELECT bought FROM users WHERE id = (%s)", (2, )
    )
    bought_1 = db.fetchall()
    bought_1 = bought_1[0]["bought"]
    assert(bought_1 > bought)
    assert(portfolio[0]["stock_name"] == "Tesla, Inc.")
    assert(portfolio[0]["stock_symbol"] == "TSLA")
    assert(portfolio[0]["num_shares"] == 5)
    # Test sell capabilities
    # assert(sell_test("TSLA", "2", "10000000", "Stock (Equity)", valid_time) == 400)
    # assert(sell_test("TSLA", "2", "5", "Stock (Equity)", valid_time) == 200)
    # db.execute (
    #     "SELECT sold FROM users WHERE id = (%s)", (2, )
    # )
    # sold_1 = db.fetchall()
    # sold_1 = sold_1[0]["sold"]
    # assert(sold_1 > sold)
    # db.execute(
    #     "SELECT * FROM portfolios WHERE user_id = (%s)", (2, )
    # )
    # portfolio = db.fetchall()
    # assert(len(portfolio) == 0)
    

# def test_total():
#     db.execute(
#         "SELECT * FROM portfolios WHERE user_id IN (SELECT id FROM users WHERE username = (%s))", ("ss", )
#     )
#     portfolio = db.fetchall()
#     db.execute("SELECT * FROM users WHERE username = (%s)", ("ss",))
#     cash = db.fetchall()
#     cash = float(cash[0]["cash"])
#     total = cash
#     for stock in portfolio:
#         total += stock["price"] * stock["num_shares"]
#     total = round(total, 2)
#     assert(total_computation("ss") == (total, cash))
    
# def test_leaderboard():
#     assert(len(leaderboard()) == 10)
#     for i in range(9):
#         assert(leaderboard()[i]["total"] >= leaderboard()[i + 1]["total"])
        