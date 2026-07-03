from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# 測試用首頁，讓我們能一眼確認網頁開不開得啟
@app.route('/', methods=['GET'])
def home():
    return "<h1>圖書館後端 API 運作正常！</h1>"

def fetch_book_title(acno):
    # 處理書號邏輯
    if acno.startswith("61") and len(acno) == 14:
        acno = acno[4:]
        
    url = "http://tals-library.esp.edu.mo/Pages/Index.aspx"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        viewstate = soup.find(id="__VIEWSTATE")['value'] if soup.find(id="__VIEWSTATE") else ""
        viewstategenerator = soup.find(id="__VIEWSTATEGENERATOR")['value'] if soup.find(id="__VIEWSTATEGENERATOR") else ""
        eventvalidation = soup.find(id="__EVENTVALIDATION")['value'] if soup.find(id="__EVENTVALIDATION") else ""
        
        form_data = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'ctl00$searchType': '6',  
            'ctl00$search': acno,      
            'ctl00$search_btn': ''     
        }
        
        post_response = session.post(url, data=form_data, headers=headers, timeout=10)
        result_soup = BeautifulSoup(post_response.text, 'html.parser')
        
        book_elem = result_soup.select_one('a.book-name')
        if book_elem:
            return book_elem.text.strip()
            
    except Exception as e:
        print(f"爬蟲出錯: {e}")
        
    return "NONE"

@app.route('/api/get_book_title', methods=['GET'])
def get_book_title():
    acno = request.args.get('acno')
    if not acno:
        return jsonify({"error": "請提供書號"}), 400
    
    title = fetch_book_title(acno)
    return jsonify({"acno": acno, "title": title})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
