from flask import Flask, request, jsonify
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)
# 允許前端網頁跨網域呼叫此 API
CORS(app)

def fetch_book_title(acno):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080") 
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10) 
    
    title = "NONE"
    try:
        driver.get("http://tals-library.esp.edu.mo/Pages/Index.aspx")
        time.sleep(2) # 稍微縮短等待時間以提升效能
        
        # 處理書號邏輯 (保留你原本的判斷)
        if acno.startswith("61") and len(acno) == 14:
            acno = acno[4:]
            
        try:
            driver.execute_script("document.getElementById('search-box').style.display = 'block';")
        except:
            pass
            
        select_elem = wait.until(EC.presence_of_element_located((By.ID, "searchType")))
        driver.execute_script("arguments[0].value = '6'; arguments[0].dispatchEvent(new Event('change'));", select_elem)

        search_input = wait.until(EC.presence_of_element_located((By.ID, "search")))
        driver.execute_script("arguments[0].value = arguments[1];", search_input, acno)
        
        search_btn = driver.find_element(By.CSS_SELECTOR, "a.search_btn")
        driver.execute_script("arguments[0].click();", search_btn)

        try:
            result = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "a.book-name, #ctl00_ContentPlaceHolder1_divNoData")
            ))
            if "book-name" in result.get_attribute("class"):
                title = result.text.strip()
        except:
            pass
    finally:
        driver.quit()
        
    return title

@app.route('/api/get_book_title', methods=['GET'])
def get_book_title():
    acno = request.args.get('acno')
    if not acno:
        return jsonify({"error": "請提供書號"}), 400
    
    title = fetch_book_title(acno)
    return jsonify({"acno": acno, "title": title})

if __name__ == '__main__':
    # 執行在本地端 port 5000
    app.run(port=5000, debug=True)