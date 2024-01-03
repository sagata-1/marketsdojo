# REST API Documentation
This is the documentation for the endpoints of the APIs I have completed so far and how they behave. All front-end developers can reference this in order to see how the different endpoints currently behave, and what the responses are.

---

#### Base URL
`https://marketsdojo.vercel.app`

---

### 1. Register API

#### Endpoint
`/v1/api/register`

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
`/v1/api/login`

#### Method
`POST`

#### Description
Allows a user to log in to the system. The endpoint accepts JSON data with the user's email and password. It verifies the user's credentials and, if successful, returns the user's `username`, `email`, `user_id`, and an `access_token`.

#### Request JSON Object
- `email` (string): The email of the user trying to log in.
- `password` (string): The password of the user.

#### Response
- **Success (200 OK)**:
  - Returns JSON containing the user's `username`, `email`, `user_id`, and `access_token`.
- **Error (403 Forbidden)**:
  - `{"error": {"code": 403, "message": "email not provided"}}` - Email missing.
  - `{"error": {"code": 403, "message": "Did not enter a password"}}` - Password missing.
  - `{"error": {"code": 403, "message": "Incorrect email and/or password"}}` - Incorrect credentials.

#### Example Request
```json
{
  "email": "existinguser@gamil.com",
  "password": "password123"
}
```

#### Example Response
```json
{
  "username": "existinguser",
  "email": "existinguser@gamil.com",
  "user_id": 2,
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

### General Notes
- The `access_token` provided in the responses is used for authenticating subsequent requests to the API.
- Error codes follow standard HTTP status codes for ease of understanding and handling in client applications.

### 3. Portfolio API

#### Endpoint
`/v1/api/portfolio`

#### Method
`POST`

#### Description
The Portfolio API provides details of the user's stock portfolio. It requires authentication via an access token. The endpoint retrieves the user's portfolio, updates the current prices of the stocks, calculates the total value and profit/loss, and returns detailed portfolio information including the user's cash on hand and various types of investments.

#### Authentication
- This API requires an access token for authentication.
- The access token must be provided as a value in the Authorization request header.

#### Request Format
- **Authenticated Request URL**: `https://marketsdojo.vercel.app/v1/api/portfolio`

#### Query Parameters
- `Authorization` (string): The token used to authenticate the user's session.

#### Response
- **Success (200 OK)**: Returns a JSON object with the following keys:
  - `portfolio`: An array of the user's stock holdings, including stock symbol, number of shares, and current price.
  - `cash`: The user's current cash balance in USD.
  - `total`: The total value of the user's portfolio in USD.
  - `starting_amt`: The starting amount of the portfolio (default is 10,000 USD).
  - `username`: The username of the account holder.
  - `pl`: The total profit or loss since the start in USD.
  - `percent_pl`: The percentage profit or loss since the start.
  - `types`: An array of investment types (e.g., Stock (Equity), Forex, Index, ETF, CFD, Commodity).
- **Error (403 Forbidden)**:
  - `{"error": {"code": 403, "message": "Missing access token"}}` - If the access token is not provided in the request.
  - `{"error": {"code": 403, "message": "Invalid or Expired Access Token"}}` - If the provided access token is invalid or expired.

#### Example Request
```
POST https://marketsdojo.vercel.app/v1/api/portfolio
request header

  "Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6IkFybWFuIEphc3VqYSIsImlhdCI6MTcwNDE5MDI5MiwianRpIjoiMWI4N2Q1OTQtNWVkMy00ZDk3LWEzNTAtMGJlMzhlOTU4NzA1IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MjYsIm5iZiI6MTcwNDE5MDI5MiwiY3NyZiI6IjBlNTBjMTZjLTNjMWItNDY0Ny1hYWFlLTgwMDY3OTdiYWU2YSIsImV4cCI6MTcwNDE5MTE5Mn0.WC6XDZs3tVyEHT8y3WN0SVxEUVkAoBdKKCmfzF6OVlk",
  "Content-type: application/json"

```

#### Example Response
```json
{
  "portfolio": [
    {
      "stock_symbol": "AAPL",
      "num_shares": 10,
      "price": 150
    },
    // ... more stocks
  ],
  "cash": "$5000.00",
  "total": "$15000.00",
  "starting_amt": 10000,
  "username": "user123",
  "pl": 5000,
  "percent_pl": 50.00,
  "types": ["Stock (Equity)", "Forex", "Index", "ETF", "CFD", "Commodity"]
}
```

---

### General Notes
- This API endpoint is designed to be accessed by authenticated users only.

---
### 3. Buy Api

**Route**: `/v1/api/buy` - Buy Assets

**Description**:  
This endpoint allows authenticated users to buy shares of various asset types including stocks, forex, CFDs, commodities, indices, and ETFs. The purchase is subject to several validations, including checking for valid symbols, matching asset types, and ensuring the user has sufficient funds.

**HTTP Method**: `GET`

**URL**: `https://marketsdojo.vercel.app/v1/api/buy`

**Query Parameters**:

- `symbol` (string): The ticker symbol of the asset to be purchased.
- `shares` (int): The number of shares to buy.
- `type` (string): The type of asset. Valid values include "Forex", "Stock (Equity)", "CFD", "Commodity", "Index", "ETF".

**Headers**:

- `Authorization` (string): Bearer token for user authentication.

**Request Example**:

```
GET "https://marketsdojo.vercel.app/v1/api/buy?symbol=AAPL&shares=5&type=Stock%20(Equity)" \
-H "Authorization: <ACCESS_TOKEN>"
```

**Success Response**:

- **Code**: `200 OK`
- **Content Example**:
  ```json
  {
    "symbol": "AAPL",
    "num_shares": 5,
    "type": "Stock (Equity)"
  }
  ```

**Error Response**:

- **Missing or Incorrect Parameters**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Missing or incorrect query parameters"
      }
    }
    ```
- **Invalid Symbol**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Invalid Symbol"
      }
    }
    ```
- **Asset Type Does Not Match Symbol**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Asset type does not match symbol"
      }
    }
    ```
- **Invalid Shares**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Invalid shares"
      }
    }
    ```
- **Cannot Trade on a Weekend**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Cannot trade on a weekend!"
      }
    }
    ```
- **Non-Forex Assets Trading Time Restriction**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)"
      }
    }
    ```

---
### 4. Sell API

**Route**: `/v1/api/sell` - Sell Shares of Stock

**Description**:  
This endpoint enables authenticated users to sell shares of various asset types, including stocks, forex, CFDs, commodities, indices, and ETFs. It includes checks for valid symbols and asset types, as well as ensuring the user has the specified number of shares to sell.

**HTTP Method**: `GET`

**URL**: `https://marketsdojo.vercel.app/v1/api/sell`

**Query Parameters**:

- `symbol` (string): The ticker symbol of the asset to be sold.
- `shares` (int): The number of shares to sell.
- `type` (string): The type of asset. Valid values include "Forex", "Stock (Equity)", "CFD", "Commodity", "Index", "ETF".

**Headers**:

- `Authorization` (string): Access token for user authentication.

**Request Example**:

```
GET "https://marketsdojo.vercel.app/v1/api/sell?symbol=AAPL&shares=5&type=Stock%20(Equity)" \
-H "Authorization: <ACCESS_TOKEN>"
```

**Success Response**:

- **Code**: `200 OK`
- **Content Example**:
  ```json
  {
    "symbol": "AAPL",
    "num_shares": 5,
    "type": "Stock (Equity)"
  }
  ```

**Error Response**:

- **Missing or Incorrect Parameters**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Missing or incorrect query parameters"
      }
    }
    ```
- **Invalid Symbol**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Invalid Symbol"
      }
    }
    ```
- **Asset Type Does Not Match Symbol**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Asset type does not match symbol"
      }
    }
    ```
- **Invalid Shares**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Invalid shares"
      }
    }
    ```
- **Too Many Shares**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Too many shares"
      }
    }
    ```
- **Non-Forex Assets Trading Time Restriction**:
  - **Code**: `400 Bad Request`
  - **Content**: 
    ```json
    {
      "error": {
        "code": 400,
        "message": "Non-Forex assets can only trade from 8:30 am to 5:00 pm! (1 hour before the market opens and upto 1 hour after the market closes)"
      }
    }
    ```

---

## Legacy Routes to be deprecated- NOTE: DO NOT USE: These work on session data, not stateless access token data.


### 2. Old Buy API

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

### 3. Old Sell API

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