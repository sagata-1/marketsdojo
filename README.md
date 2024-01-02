# REST API Documentation
This is the documentation for the endpoints of the APIs I have completed so far and how they behave. All front-end developers can reference this in order to see how the different endpoints currently behave, and what the responses are.

---

#### Base URL
`https://marketsdojo.vercel.app`

---

### 1. Register API

#### Endpoint
`/api/register`

#### Method
`POST`

#### Description
Registers a new user in the system. This endpoint accepts JSON data containing the user's username, email, and password. It checks if the username or email already exists in the database and returns an error if so. If successful, it creates a new user record, generates an access token, and returns the user's details along with the token.

#### Request JSON Object
- `username` (string): The desired username of the new user.
- `email` (string): The email address of the new user.
- `password` (string): The password for the new user.

#### Response
- **Success (200 OK)**:
  - Returns JSON containing the user's `username`, `user_id`, `email`, and `access_token`.

- **Error (400 Bad Request)**:
  - `{"error": {"code": 400, "message": "username not provided"}}` - Username missing.
  - `{"error": {"code": 400, "message": "email not provided"}}` - Email missing.
  - `{"error": {"code": 400, "message": "Did not enter a password"}}` - Password missing.
  - `{"error": {"code": 400, "message": "username or email already exists"}}` - Username or email already in use.

#### Example Request
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123"
}
```

#### Example Response
```json
{
  "username": "newuser",
  "user_id": 1,
  "email": "newuser@example.com",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### 2. Login API

#### Endpoint
`/api/login`

#### Method
`POST`

#### Description
Allows a user to log in to the system. The endpoint accepts JSON data with the user's username and password. It verifies the user's credentials and, if successful, returns the user's `username`, `user_id`, and an `access_token`.

#### Request JSON Object
- `username` (string): The username of the user trying to log in.
- `password` (string): The password of the user.

#### Response
- **Success (200 OK)**:
  - Returns JSON containing the user's `username`, `user_id`, and `access_token`.
- **Error (403 Forbidden)**:
  - `{"error": {"code": 403, "message": "username not provided"}}` - Username missing.
  - `{"error": {"code": 403, "message": "Did not enter a password"}}` - Password missing.
  - `{"error": {"code": 403, "message": "Incorrect username or password"}}` - Incorrect credentials.

#### Example Request
```json
{
  "username": "existinguser",
  "password": "password123"
}
```

#### Example Response
```json
{
  "username": "existinguser",
  "user_id": 2,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### General Notes
- The `access_token` provided in the responses is used for authenticating subsequent requests to the API.
- Error codes follow standard HTTP status codes for ease of understanding and handling in client applications.

## Routes to be deprecated- NOTE: DO NOT USE: These work on session data, not stateless access token data.

### 1. Portfolio API

**Endpoint Description**: Displays the user's portfolio of stocks, including the current value of each stock, total cash available, and overall portfolio performance.

**HTTP Method**: GET

**Route**: `api/portfolio`

**Parameters**: None at the moment

**Authentication**: User must be logged in (handled by Flask Session), otherwise the endpoint redirects to the landing page.

**Request Example**:
```
GET https://marketsdojo.vercel.app/api/portfolio
```

**Response Example**:
```
{
  "portfolio": [
    {"stock_symbol": "APPL", "price": 150.00, "num_shares": 10, "type": "Stock (Equity)"},
    // ... other stocks ...
  ],
  "cash": "$5000.00",
  "total": "$20000.00",
  "starting_amt": 10000,
  "username": "john_doe",
  "pl": 10000.00,
  "percent_pl": 100.00,
  "types": ["Stock (Equity)", "Forex", "Index", "ETF", "CFD", "Commodity"]
}
```

**Error Handling**:
- If the user is not logged in, they will not be able to access this endpoint.
- Any database connection issues or errors in fetching data will currently affect this endpoint.

**Additional Notes**: 
- The `/api/portfolio` endpoint updates the price of each stock in the user's portfolio to the current market price before returning the data.
- The response includes the user's total cash, the total value of the portfolio, the user's net profit or loss (pl), and the percentage of profit or loss (percent_pl).
- The starting amount is provided for reference (in this example, it's set at 10,000).
- The `types` array lists all the different types of assets that can be part of the portfolio.
- I plan to add in some exception handling in order to account for the case of the connection and database issues that could occur.

---


### 2. Buy API

**Endpoint Description**: This endpoint is used to buy shares of stock.

**HTTP Method**: GET

**URL**: `https://marketsdojo.vercel.app/api/buy?symbol=STOCKSYMBOL&shares=NUMSHARES&type=STOCKTYPE`

**Parameters**:
- `symbol` (String): Stock symbol to buy.
- `shares` (Integer): Number of shares to buy.
- `type` (String): Type of stock (Forex, Stock (Equity), CFD, Commodity, Index, ETF).

**Authentication**: User must be logged in (handled by Flask Session), otherwise the endpoint redirects to the landing page.

**Request Example**:
```
GET https://marketsdojo.vercel.app/api/buy?symbol=APPL&shares=10&type=Stock%20(Equity)
```

**Response Example**:
```
Redirects to https://marketsdojo.vercel.app/portfolio_api
```

**Error Handling**:
- Missing or incorrect query parameters.
- Invalid stock symbol.
- Asset type does not match symbol.
- Invalid number of shares.
- Trading time restrictions.

**Additional Notes**: Trades are restricted based on the type of stock and current time. Users can't trade on weekends, and trading hours are limited.

---

### 3. Sell API

**Endpoint Description**: Allows users to sell shares of stock.

**HTTP Method**: GET

**URL**: `https://marketsdojo.vercel.app/api/sell?symbol=STOCKSYMBOL&shares=NUMSHARES&type=STOCKTYPE`

**Parameters**:
- `symbol` (String): Stock symbol to sell.
- `shares` (Integer): Number of shares to sell.
- `type` (String): Type of stock.

**Authentication**: User must be logged in (handled by Flask Session), otherwise the endpoint redirects to the landing page.

**Request Example**:
```
GET https://marketsdojo.vercel.app/sell_api?symbol=APPL&shares=5&type=Stock%20(Equity)
```

**Response Example**:
```
Redirects to https://marketsdojo.vercel.app/api/portfolio
```

**Error Handling**:
- Missing or incorrect query parameters.
- Invalid stock symbol.
- Asset type does not match symbol.
- Invalid number of shares or selling more shares than owned.
- Trading time restrictions.

**Additional Notes**: Similar to the buy API, trading is restricted based on time and day.

---

### 3. Commodity API

**Endpoint Description**: Retrieves a list of available commodities.

**HTTP Method**: GET

**URL**: `https://marketsdojo.vercel.app/api/commodity`

**Parameters**: None.

**Authentication**: User must be logged in (handled by Flask Session), otherwise the endpoint redirects to the landing page.

**Request Example**:
```
GET https://marketsdojo.vercel.app/api/commodity
```

**Response Example**:
```
{
  "commodities": ["Gold", "Silver", "Oil"]
}
```

**Error Handling**: Not applicable for this endpoint.

**Additional Notes**: This endpoint is used to fetch a current list of commodities. Next, I will cache the result of this endpoint in the static folder (as it currently queries the FMP API for data) and then make request read from that file. That should be faster (and better for large data) than the current third party API query.

---

I will continue to update the documentation as I add in more api endpoints and as I make any changes to the current api endpoints behaviour.