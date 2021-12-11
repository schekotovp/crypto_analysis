import requests
import json
import pandas as pd
import matplotlib.pyplot as plt

api_key = 'c5c94069-224f-47fc-9f0e-fde520ad3295'

headers = {
    'X-CMC_PRO_API_KEY': api_key}

params = {
    'limit': 5000}

req = requests.get('https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest', headers=headers,
                   params=params)
data = json.loads(req.text)['data']

names = []
smart_contracts = []
market_pairs = []
circulating_supply = []
max_supply = []
market_cap = []
market_cap_dominance = []
percent_change_60d = []
for currency in data:
    names.append(currency['name'])
    market_pairs.append(currency['num_market_pairs'])
    circulating_supply.append(currency['circulating_supply'] / 10 ** 6)
    max_sup = currency['max_supply']
    if max_sup is not None:
        max_sup = 1
    else:
        max_sup = 0
    max_supply.append(max_sup)
    smart_contracts.append('smart-contracts' in currency['tags'])
    market_cap.append(currency['quote']['USD']['market_cap'] / 10 ** 6)
    market_cap_dominance.append(currency['quote']['USD']['market_cap_dominance'])
    percent_change_60d.append(currency['quote']['USD']['percent_change_60d'])

df = pd.DataFrame({'name': names,
                   'market_pairs': market_pairs,
                   'circulating': circulating_supply,
                   'max supply': max_supply,
                   'MC': market_cap,
                   'MC_dominance': market_cap_dominance,
                   'sixty_days_change': percent_change_60d,
                   'SC': smart_contracts
                   })
df.to_csv('data.csv')

