from flask import Flask, jsonify,send_file,render_template,request,redirect,url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis
import jwt.algorithms
from outils import parse_tickers
from .auth import require_cf_token
from datetime import datetime
from aiReport import ai_query, compile
from flask_cors import CORS
from flask_session import Session
import pandas as pd
from rittenhouse import quant_rittenhouse
import fetch5yData
import stockPlotData
import companyData
import getStockPrice
import stockIntrinsicVal
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
from worker import generate_ai_report,celery, generate_ai_7powers,generate_ai_quant,generate_ai_quant_rittenhouse
from s3_bucket_ops import s3_upload,s3_presigned_url
from quant import quant
load_dotenv()

CF_CERT_URL = f"https://{os.getenv('CF_URL_CDN_CGI_CERTS')}/cdn-cgi/access/certs"
CERT_KYS = requests.get(CF_CERT_URL).json()
CF_AUDIENCE_ID = os.getenv('CF_AUD_ID')
uri = os.getenv('MONGODB_URI')
client = MongoClient(uri, server_api=ServerApi('1'))
db=client['test']
edgar_collection=db['rawEdgarCollection']
ai_tasks_collection=db['aiTasks']
app = Flask(__name__)
app.config.from_object(app_constants)
ENV=os.getenv('ENV')
if ENV=="prod":
    CORS(app, resources={
        r"/api/*":{
            "origins":[
                "https://www.eacsa.us",
                "wss://www.eacsa.us"
            ],
            "supports_credentials":False,
            "allow_headers":["Content-Type","Authorization","token"]
        }
    })
    limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/3"
    )
if ENV=="dev":
    CORS(app)
    limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    storage_uri="memory://",
    enabled=False
    )
if ENV=='':
    raise Exception("environment not defined. potential attack!")
Session(app)
DOWNLOAD_DIR = os.getenv('DIRECTORY')

@app.route('/api/economy_index', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def fetch_economy_index():
    all_data = {}
    indexList= ["STLFSI4","SP500","HOUST1F","UNRATE","SOFR","DRCLACBS","WTREGEN","DCOILWTICO","WTISPLC","POILBREUSDM","PNGASEUUSDM","PNGASUSUSDM","MNGLCP","RRPONTSYD","FPCPITOTLZGUSA","DGS10","T10YIE","DGS2","U6RATE"]
    for myIndex in indexList:
      indexData = EconomyStats.getEconomicIndex(myIndex)
      all_data[myIndex] = indexData
    return jsonify(all_data)
#fetch company names, price and earnings day
@app.route('/api/company_data', methods=['GET'])
@require_cf_token
@limiter.limit("3 per minute") 
def fetch_company_data():
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers= parse_tickers(raw_tickers)
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    company_data = companyData.compile_stockData(tickers)

    return company_data
#fetch the stock price
@app.route('/api/stock_price', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def fetch_stock_price():
    price=[]
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers=parse_tickers(raw_tickers)
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400
    data = {ticker: getStockPrice.fetch_stock_price_data(ticker) for ticker in tickers}
    return jsonify(data)
#fetch other metrics for value for plots
@app.route('/api/financial_data', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def fetch_financial_data():
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers=parse_tickers(raw_tickers)
    if not tickers:
        return jsonify({'error': 'No tickers provided'}), 400    
    data = {ticker: stockPlotData.fetch_financials(ticker) for ticker in tickers} 
    return jsonify({"financial_data": data}),200
# New API for value stock analysis
@app.route('/api/5y_data', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def fetch_5y_financial_data():
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers=parse_tickers(raw_tickers)
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
        combined_data = pd.concat(all_data, ignore_index=False).fillna(0)
    except:
        return jsonify({"error": "Failed to fetch any data"}), 500
    
    combined_data.reset_index(inplace=True) 
    # Convert DataFrame to JSON serializable format
    result = combined_data.to_dict(orient='records')
    return jsonify(result),200
#Rittenhouse Analysis API
@app.route('/api/v1/analyze_rittenhouse', methods=['POST'])
@require_cf_token
@limiter.limit("1 per minute") 
def analyze_rittenhouse():
    data=request.json
    if 'user_id' not in data or 'tickers' not in data or 'report_type' not in data:
        return jsonify({
            "error":"missing payload"
        }),400
    else:
        try:
            tickers =data.get('tickers','')
            user_id=data.get('user_id','')
            report_type=data.get('report_type','')
            task=generate_ai_quant_rittenhouse.delay(tickers,user_id,report_type)
            return jsonify({
            'task_id':task.id,
            'status':'processing',
            'report_type':report_type
            }),202
        except Exception as e:
                return jsonify({'error':"internal server error"}),500
# calculate intrinsic values
@app.route('/api/intrinsic_value', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def analyze_intrinsic_value():
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers=parse_tickers(raw_tickers)
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
            return jsonify({'error': f'Error processing ticker {ticker}'}), 500

    if intrinsic_values:
        return jsonify(intrinsic_values), 200
    else:
        return jsonify({'error': 'No valid data to display.'}), 400
# API route for login
@app.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute") 
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
@limiter.limit("5 per minute") 
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
@limiter.limit("5 per minute") 
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
@require_cf_token
@limiter.limit("5 per minute") 
def messageBot():
    data = request.json
    tickers = data.get('tickers')
    user_id=data.get('user_id')
    report_type=data.get("report_type")
    if 'tickers' not in data or 'user_id' not in data or 'report_type' not in data:
        return jsonify({
            'error':'missing fields'
        }),400
    try:
        task = generate_ai_7powers.delay(tickers,user_id,report_type)
        return jsonify({
            'task_id':task.id,
            'status':'processing',
            'report_type':report_type
            }),202
    except Exception as e:
        return jsonify({'error':"internal server error"}),500
@app.route('/api/v1/gemini',methods=['POST'])
@require_cf_token
@limiter.limit("5 per minute") 
def gemini_post():
    data=request.json
    tickers = data.get('tickers','')
    user_id = data.get('user_id','')
    report_type=data.get('report_type','')
    if 'user_id' not in data or 'tickers' not in data or 'report_type' not in data:
        return jsonify({
            'error':'missing one or more keys'
        }),400
    if not tickers or not user_id or not report_type:
        
        return jsonify({
            'error':'missing values'
        }),400
    try:
        task =generate_ai_report.delay(tickers,user_id,report_type)
        return jsonify({
            'task_id':task.id,
            'status':'processing',
            'report_type':report_type
        }),202
    except Exception as e:
            return jsonify({'error':"internal server error"}),500
@app.route('/api/v1/gemini/report',methods=['POST'])
@require_cf_token
@limiter.limit("5 per minute") 
def report_generate_and_upload():
    data= request.json
    task_id=data.get('task_id')
    file_name=task_id
    bucket_name=data.get('bucket_name')
    if not file_name or not bucket_name:
        return jsonify({
            "error":"missing fields"
        }),400
    else:
        try:
            pdf_report = PDFReport(task_id)
            pdf_report.generate()
            s3_upload(bucket_name=bucket_name,file_name=file_name)
            return jsonify({
                "message":"success"
            }),200
        except Exception as e:
            return jsonify({
                "error":"internal server error"
            }),500
@app.route('/api/fetchStockfromDB', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def MongoFetchStock():
    try:
        # Get pagination parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))  # Number of symbols per page
        exchange = request.args.get('exchange','')
        # Fetch grouped stock data
        grouped_stocks,total_symbols = stockFetch(db,page,page_size,exchange)
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
        return jsonify({'error': "internal server error"}), 500
@app.route('/api/QStockScore', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def QtrStockScore ():
    stockData=[]
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers=parse_tickers(raw_tickers)
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
            return jsonify({'error': "internal server error"}), 500
    return jsonify(stockData)
@app.route('/api/AllQStockTrend',methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
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
        return jsonify({'error': "internal server error"}), 500   
@app.route('/api/financial_data_qtr', methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def fetch_4qtr_financial_data():
    raw_tickers = [request.args.get(f'ticker{i}') for i in range(1, 4) if request.args.get(f'ticker{i}')]
    tickers=parse_tickers(raw_tickers)
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
    try:
        key = next(k for k in CERT_KYS["keys"] if k["kid"]==headers["kid"])
    except StopIteration:
        return jsonify({
            "success":False,
            "message":"invalid key id"
        }),401
    
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
@require_cf_token
@limiter.limit("5 per minute") 
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
            'error':"internal server error"
        }),500
@app.route('/api/v1/user_reports',methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def query_reports():
    user_id=request.args.get('user_id')
    if not user_id:
        return jsonify({
            "error":"missing fields"
        }),400
    try:
        filter={
            "user_id":user_id.strip(),
        }
        project={
            "assistant":0
        }
        sort=list({
            'timestamp':-1
        }.items())
        limit=10
        docs=db['aiTasks'].find(
            filter=filter,
            projection=project,
            sort=sort,
            limit=limit
            )
        collection=[]
        for doc in docs:
            doc["_id"]=str(doc["_id"])
            if 'timestamp' in doc:
                doc["timestamp"]=doc["timestamp"].isoformat()+ "Z"
            collection.append(doc)
        if not collection:
            return jsonify({
                "message":"no reports found"
            }),200
        return jsonify({
            "status":"ok",
            "count":len(collection),
            "data":collection
        }),200
    except Exception as e:
        return jsonify({
            "error":"internal server error"
        }),500
@app.route('/api/v1/user_report',methods=['GET'])
@require_cf_token
@limiter.limit("5 per minute") 
def download_report():
    bucket_name=request.args.get('bucket_name','')
    file_name=request.args.get('file_name','')
    client_method=request.args.get('client_method','')
    if not bucket_name or not file_name or not client_method or client_method!="get_object":
        return jsonify({
            "error":"missing fields"
        }),400
    else:
        try:
            params={"Bucket":bucket_name,"Key":f"{file_name}.pdf"}
            signed_url=s3_presigned_url(client_method=client_method,method_params=params,expiration_time=30)
            return jsonify({
                "signed_url":signed_url
            }),200
        except Exception as e:
            return jsonify({
                "error":"internal server error"
            }),500
@app.route('/api/v1/quant',methods=['POST'])
@require_cf_token
@limiter.limit("5 per minute") 
def quantize():
    data=request.json
    if 'user_id' not in data or 'tickers' not in data or 'report_type' not in data:
        return jsonify({
            "error":"missing payload"
        }),400
    else:
        try:
            tickers =data.get('tickers','')
            user_id=data.get('user_id','')
            report_type=data.get('report_type','')
            task=generate_ai_quant.delay(tickers,user_id,report_type)
            return jsonify({
            'task_id':task.id,
            'status':'processing',
            'report_type':report_type
            }),202
        except Exception as e:
                return jsonify({'error':"internal server error"}),500
@app.route('/api/private')
@require_cf_token
@limiter.limit("5 per minute") 
def secret_area():
    return jsonify({
        "message": "Access granted",
        "identity": request.cf_identity
    })
if __name__ == '__main__':
    debug_mode= os.getenv("FLASK_DEBUG","0")=="1"
    app.run(host="0.0.0.0",port=5000,debug=debug_mode)
