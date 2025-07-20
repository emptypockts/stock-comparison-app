from flask import Flask, jsonify,send_file,render_template,request,redirect,url_for
import jwt.algorithms
from datetime import datetime
from aiReport import ai_query, compile
from flask_cors import CORS
from flask_session import Session
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
import app_constants
from authLogin import loginStep
from authRegister import registerStep
import EconomyStats
from fetchStockfromdB import stockFetch
from qtrStockDbOps import pull_QStockData,PullQtrStockRevenueTrends
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from stockPlotDataQtr import fetch_4qtr_data
from PDFReport import PDFReport
import requests
from worker import generate_ai_report,celery
load_dotenv()
CF_CERT_URL = f"https://{os.getenv('CF_URL_CDN_CGI_CERTS')}/cdn-cgi/access/certs"
CERT_KYS = requests.get(CF_CERT_URL).json()
CF_AUDIENCE_ID = os.getenv('CF_AUD_ID')
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["test"]
app = Flask(__name__)
app.config.from_object(app_constants)
CORS(app)
Session(app)
DOWNLOAD_DIR = 'sec_filings'


@app.route('/api/economy_index', methods=['GET'])
def fetch_economy_index():
    all_data = {}
    indexList= ["STLFSI4","SP500","HOUST1F","UNRATE","SOFR","DRCLACBS","WTREGEN","DCOILWTICO","WTISPLC","POILBREUSDM","PNGASEUUSDM","PNGASUSUSDM","MNGLCP","RRPONTSYD"]
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
@app.route('/api/v1/seven_p', methods=['POST'])
def messageBot():
    data = request.json
    tickers = data.get('tickers')
    try:
        response = geminiChat.seven_powers(tickers)
        return jsonify({
            'assistant':response,
            }),200
    except Exception as e:
        return jsonify({'error':e}),400
@app.route('/api/v1/gemini',methods=['POST'])
def gemini_post():
    data=request.json
    tickers = data.get('tickers')
    user_id = data.get('user_id')
    if 'user_id' not in data or 'tickers' not in data:
        return jsonify({
            'error':'missing fields'
        }),400
    try:
        task =generate_ai_report.delay(tickers,user_id)
        return jsonify({
            'task_id':task.id,
            'status':'processing'
        }),202
    except Exception as e:
            return jsonify({'error':str(e)}),400
@app.route('/api/v1/gemini/report',methods=['POST'])
def gemini_generate_pdf():
    data= request.json
    task_id=data.get('task_id')
    print('task_id',task_id)
    try:
        pdf_report = PDFReport(task_id)
        pdf_buffer,today=pdf_report.generate()
        return send_file(pdf_buffer,as_attachment=True,
                         download_name=f"{today}.pdf",
                         mimetype='application/pdf',
                         ),200
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),500
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
            return jsonify({'error': str(e)}), 400
    return jsonify(stockData)
@app.route('/api/AllQStockTrend',methods=['GET'])
def AllQtrStockRevTrend():
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))  # Number of symbols per page
        
        
        # Fetch grouped stock data
        grouped_stocks,total_symbols = PullQtrStockRevenueTrends(db['QtrStockRevTrend'],page,page_size)
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
        return jsonify({'error': str(e)}), 400   
@app.route('/api/financial_data_qtr', methods=['GET'])
def fetch_4qtr_financial_data():
    tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400

    all_data={
    ticker:{
        'financial_data_qtr':fetch_4qtr_data(ticker)
        }
        for ticker in tickers
    }
    if not all_data:
        return jsonify({"error": "Failed to fetch any qtr data"}), 500
    return jsonify(all_data),200
@app.route('/api/v1/cfToken',methods=['GET'])
def get_a_token():
    token = request.headers.get("Cf-Access-Jwt-Assertion") or request.cookies.get("CF_Authorization")
    if not token:
        return jsonify({
            "error":"missing token"
        }),401
    headers = jwt.get_unverified_header(token)
    key = next(k for k in CERT_KYS["keys"] if k["kid"]==headers["kid"])
    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
    try:
        decoded = jwt.decode(
        token,
        public_key,
        algorithms=["RS256"],
        audience=CF_AUDIENCE_ID)
        return jsonify({
            "success":True,
            "email":decoded.get("email",''),
            "sub":decoded.get("sub",''),
            "name":decoded.get("name",''),
            "aud":decoded.get("aud",''),
            "iss":decoded.get("iss",''),
            "preferred_username":decoded.get('custom','').get('preferred_username',''),
            "upn":decoded.get('custom',{}).get('upn',''),
            "exp":datetime.datetime.fromtimestamp(decoded.get('exp'))
        }),200
    except jwt.ExpiredSignatureError:
        return jsonify({"success": False, "message": "Token has expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"success": False, "message": "Invalid token"}), 401
 #check celery task status   
@app.route('/api/v1/gemini/status/<task_id>',methods=['GET'])
def gemini_task_status(task_id):
    try:
        task=celery.AsyncResult(task_id)
        if task.state=='PENDING':
            return jsonify({'status':'pending'}),202
        elif task.state=='SUCCESS':
            return jsonify({
                'status':'completed',
                'assistant':task.result
                }),200
        elif task.state=='FAILURE':
            return jsonify({
                'status':'failed',
                'error':str(task.result)
            }),500
        else:
            return jsonify({
                'status':task.state
            }),202
    except Exception as e:
        return jsonify({
            'error':e
        })
if __name__ == '__main__':
    app.run(debug=True)