from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import secDBFetch
import rittenhouse
import fetch5yData
import stockPlotData
import companyData
import getStockPrice
import stockIntrinsicVal
import geminiChat
from dotenv import load_dotenv
import os
import bcrypt
import jwt
import datetime
from authLogin import loginStep
from authRegister import registerStep
import EconomyStats
from fetchStockfromdB import stockFetch
from QStockScore import pull_QStockData,pullAllStockData,RevenueGrowthQtrStockData,PullQtrStockRevenueTrends
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from fetch4qtrData import fetch_4qtr_data

uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]
load_dotenv()
app = Flask(__name__)
CORS(app)
DOWNLOAD_DIR = 'sec_filings'
#fetch Economy Indicators
@app.route('/api/economy_index', methods=['GET'])
def fetch_economy_index():
    all_data = {}
    indexList= ["STLFSI4","SP500","HOUST1F","UNRATE","SOFR","DRCLACBS","WTREGEN"]
    for myIndex in indexList:
      indexData = EconomyStats.getEconomicIndex(myIndex)
      all_data[myIndex] = indexData
    return jsonify(all_data)


#fetch company names, price and earnings day
@app.route('/api/company_data', methods=['GET'])
def fetch_company_data():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    company_data = companyData.compile_stockData(tickers)
    return jsonify(company_data)
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
#Rittenhouse Analysis API
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
# analyse text from 10-K 8-K 6-K and DEF reports for rittenhouse analysis
@app.route('/api/analyze_rittenhouse', methods=['GET'])
def analyze_rittenhouse():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    data = {ticker: rittenhouse.analyze_ticker(DOWNLOAD_DIR,ticker) for ticker in tickers} 
    return jsonify({"reports": data}),200
# calculate intrinsic values
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
@app.route('/api/login', methods=['POST'])
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
        expiration_time =datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes= 30)
        print(expiration_time)
        token = jwt.encode({
            'user_id': str(user['_id']),
            'exp': expiration_time
        }, os.getenv('JWT_SECRET'), algorithm='HS256')
        return jsonify({'success': True, 'token': token,'expiresAt': int(expiration_time.timestamp())}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
# # API route for registration
@app.route('/api/register', methods=['POST'])
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
@app.route('/api/verify', methods=['POST'])
def verify_token():
    
    token = request.headers.get('token')
    if not token:
        return jsonify({'success': False, 'message': 'Token is missing'}), 401

    try:
        decoded = jwt.decode(token, os.getenv('JWT_SECRET'), algorithms=['HS256'])
        return jsonify({'success': True, 'user_id': decoded['user_id'],"expire":datetime.datetime.fromtimestamp(decoded['exp'],tz=datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S UTC')}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'success': False, 'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'success': False, 'message': 'Invalid token'}), 401

@app.route('/api/chat', methods=['POST'])
def messageBot():
    data = request.json
    query = data.get('query')
    try:
        response = geminiChat.chatQuery(query)
        return jsonify({
            'assistant':response,
            }),200
    except:
        return jsonify({'error':response}),400

@app.route('/api/fetchStockfromDB', methods=['GET'])
def MongoFetchStock():
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))  # Number of symbols per page
        
        # Fetch grouped stock data
        grouped_stocks,total_symbols = stockFetch(db,page,page_size)
        # Pagination logic
        start = (page - 1) * page_size
        end = start + page_size

        # Build paginated response

        return jsonify({
            'data': grouped_stocks,
            'page': page,
            'total_symbols':total_symbols
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400

@app.route('/api/QStockScore', methods=['GET'])
def QtrStockScore ():
    stockData=[]
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    for ticker in tickers:
        try:
            response = pull_QStockData(db,ticker)
            stockData.extend( [{
                **item,
                '_id':str(item['_id']),

            }for item in response])

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': str(e)}), 400
    return jsonify(stockData)
    
@app.route('/api/AllQStockTrend',methods=['GET'])
def AllQtrStockRevTrend():
    try:
        print("trying to get parameters")
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))  # Number of symbols per page
        
        
        # Fetch grouped stock data
        grouped_stocks,total_symbols = PullQtrStockRevenueTrends(db,page,page_size)
        # Pagination logic
        start = (page - 1) * page_size
        end = start + page_size

        # Build paginated response

        return jsonify({
            'data': grouped_stocks,
            'page': page,
            'total_symbols':total_symbols
            }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 400
    
@app.route('/api/4qtr_data', methods=['GET'])
def fetch_4qtr_financial_data():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    all_data = []
    for ticker in tickers:
        try:
            data = fetch_4qtr_data(ticker)
            all_data.append(data)
        except Exception as e:
            print(f"Cannot fetch stock {ticker}: {e}")
            all_data.append(None)
    if not all_data:
        return jsonify({"error": "Failed to fetch any qtr data"}), 500
    try:
        combined_data = pd.concat(all_data, ignore_index=False)
    except:
        return jsonify({"error": "Failed to fetch any data"}), 500
    
    combined_data.reset_index(inplace=True) 
    # Convert DataFrame to JSON serializable format
    result = combined_data.to_dict(orient='records')

    return jsonify(result),200


if __name__ == '__main__':
    app.run(debug=True)
