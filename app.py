from flask.json import jsonify
import requests 
from bs4 import BeautifulSoup as BS
from flask import Flask
from flask import request
import os
from fake_useragent import UserAgent

app = Flask(__name__)

def formula_balance(formula: str) -> str:
    formula_prepare = formula.replace(' ', '').replace('+', '+%2B').replace('=', '+%3D')
    url = f'https://ru.intl.chemicalaid.com/tools/equationbalancer.php?equation={formula_prepare}'
    ua = UserAgent()
    headers = {
        'user-agent': ua.random
    }
    r = requests.get(url, headers=headers)
    soup = BS(r.content.decode('utf-8'), 'html.parser')
    try:
        
        balance = soup.find('div', class_='card-body chemical-formula balanced-result').text.strip()
    except:
        print(formula)
        return ''

    return balance

def get_el_ids(react: str, product: str) -> tuple:
    url = f'https://chemequations.com/ru/rasshirennyj-poisk/?reactant1={react}&product1={product}&submit='
    session = requests.Session()
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0'
    }

    r = session.get(url, headers=headers)
    soup = BS(r.content.decode('utf-8'), 'html.parser')

    div = soup.find('div', class_='search-results-async')
    try:
        reactantIds, productIds = div.attrs['data-reactantids'], div.attrs['data-productids']
    except:
        return None, None
    return reactantIds, productIds

def get_res(reactid: str, productid: str) -> list:
    url = f'https://chemequations.com/api/search-reactions-by-compound-ids?reactantIds={reactid}&productIds={productid}&offset=0'  
    r = requests.get(url)
    content = r.json()
    res = []

    for i in content['searchResults']:
        res.append(i['equationStr'])  
    
    return res

@app.route('/', methods=['GET'])
def home():
    return 'Text'

@app.route('/get_reaction', methods=['POST'])
def get():
    data = request.form
    react, product = data['react'], data['product']
    reactId, productId = get_el_ids(react, product)

    if reactId != None and productId != None:
        res = get_res(reactId, productId)
        res = [formula_balance(i) for i in res]
        res = [i for i in res if i != '']
        return jsonify({
            'res': res
        })
    
    return jsonify({
        'res': 'not found'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 80))

