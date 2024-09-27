from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import secDBFetch  # Assuming secDBFetch.py is refactored as a module
import rittenhouse  # Assuming rittenhouse.py is refactored as a module
import fetch5yData
import stockPlotData
import companyName
import getStockPrice
import stockIntrinsicVal
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime
from server.api.auth.authLogin import loginStep
from server.api.auth.authRegister import registerStep
from datetime import timedelta
load_dotenv()
app = Flask(__name__)
CORS(app)
DOWNLOAD_DIR = 'sec_filings'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
# Ensure the download directory exists



#fetch company names, price and earnings day
@app.route('/api/company_name', methods=['GET'])
def fetch_company_names():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    company_names = {ticker: companyName.get_company_name(ticker) for ticker in tickers}
    return jsonify(company_names)
#fetch the stock price
@app.route('/api/stock_price', methods=['GET'])
def fetch_stock_price():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    data = {ticker: getStockPrice.fetch_stock_price_data(ticker) for ticker in tickers}
    return jsonify(data)
#fetch other metrics for value for plots
@app.route('/api/financial_data', methods=['GET'])
def fetch_financial_data():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400    
    data = {ticker: stockPlotData.fetch_financials(ticker) for ticker in tickers} 
    return jsonify({"financial_data": data}),200

# New API for value stock analysis
@app.route('/api/5y_data', methods=['GET'])
def fetch_5y_financial_data():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    all_data = []
    for ticker in tickers:
        try:
            data = fetch5yData.fetch_5y_data(ticker)
            all_data.append(data)
        except Exception as e:
            print(f"Cannot fetch stock {ticker}: {e}")
            all_data.append(None)
    if not all_data:
        return jsonify({"error": "Failed to fetch any data"}), 500
    try:
        combined_data = pd.concat(all_data, ignore_index=False)
    except:
        return jsonify({"error": "Failed to fetch any data"}), 500
    
    combined_data.reset_index(inplace=True) 
    # Convert DataFrame to JSON serializable format
    result = combined_data.to_dict(orient='records')

    return jsonify(result),200
#fetch sec report data if non existing
@app.route('/api/fetch_sec_reports', methods=['GET'])
def fetch_sec_reports():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    for ticker in tickers:
        try:
            form_types = request.args.getlist('form_types') or ['10-K', '10-Q', '8-K', 'DEF 14A']
            # Fetch the SEC filings using the secDBFetch module
            secDBFetch.get_sec_filings(ticker.capitalize(), form_types)
            return jsonify({'message': 'SEC filings fetched successfully'}), 200
        except Exception as e:
            return jsonify({'error check the secDBFetch flow': str(e)}), 500
#analyse text from 10-K 8-K 6-K and DEF reports for rittenhouse analysis
@app.route('/api/analyze_rittenhouse', methods=['GET'])
def analyze_rittenhouse():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    data = {ticker: rittenhouse.analyze_ticker(DOWNLOAD_DIR,ticker) for ticker in tickers} 
    return jsonify({"reports": data}),200
#calculate intrinsic values
@app.route('/api/intrinsic_value', methods=['GET'])
def analyze_intrinsic_value():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]

    intrinsic_values = []

    for index, ticker in enumerate(tickers):
        try:
            growth_rate = float(request.args.get(f'growthRate{index + 1}', 5.0))
            discount_rate = float(request.args.get(f'discountRate{index + 1}', 10.0))
            terminal_growth_rate = float(request.args.get(f'terminalGrowthRate{index + 1}', 2.0))
            projection_years = int(request.args.get(f'projectionYears{index + 1}', 5))
            result = stockIntrinsicVal.getAllIntrinsicValues(
                ticker=ticker,
                growth_rate=growth_rate,
                discount_rate=discount_rate,
                terminal_growth_rate=terminal_growth_rate,
                projection_years=projection_years
            )
            if result:
                intrinsic_values.extend(result)

        except Exception as e:
            return jsonify({'error': f'Error processing ticker {ticker}: {str(e)}'}), 500

    if intrinsic_values:
        return jsonify(intrinsic_values), 200
    else:
        return jsonify({'error': 'No valid data to display.'}), 400



# API route for login
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'success':False, 'message': 'missing username or password'}),400
    user = loginStep(username)
    if not user:
        return ({'success': False, 'message': 'User not found'}), 404
    # Get the stored hashed password
    stored_hashed_password = user['password']
    if isinstance(stored_hashed_password,str):
        stored_hashed_password= stored_hashed_password.encode('utf-8')
    # Validate the password entered by the user with the stored hash
    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        # If valid, create and return JWT token
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours= 1)
        }, os.getenv('JWT_SECRET'), algorithm='HS256')
        return jsonify({'success': True, 'token': token}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

# # API route for registration
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    email = data.get('email')
    result = registerStep(username,password,name,email)
    # Return the result to the client
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

# # Middleware to verify JWT token
@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    token = request.headers.get('authorization')
    
    if not token:
        return jsonify({'success': False, 'message': 'Token is missing'}), 401

    try:
        decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return jsonify({'success': True, 'user_id': decoded['user_id']}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 401


if __name__ == '__main__':
    app.run(debug=True)
