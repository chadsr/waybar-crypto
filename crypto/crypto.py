#!/usr/bin/env python3

import sys
import os
import requests
import json
import configparser
from decimal import Decimal

API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'

# Attempt to load crypto.ini configuration file
config = configparser.ConfigParser()
abs_dir = os.path.dirname(os.path.abspath(__file__)) # Get the absolute path of this script
config_path = f'{abs_dir}/crypto.ini'
try:
	with open(config_path, 'r', encoding='utf-8') as f:
		config.read_file(f)
except Exception as e:
	print(f'Could not find/open crypto.ini ({config_path}). Does it exist?\n{e}')
	sys.exit(1)

# Attempt to parse required fields of crypto.ini
try:
	coins = [section for section in config.sections() if section != 'general'] # Any section that isn't general, is a coin
	currency = config['general']['currency'].upper() # The fiat currency used in the trading pair
	currency_symbol = config['general']['currency_symbol']
except Exception as e:
	print(f'Could not parse required fields of the configuration file:\n{e}')

# Construct API query parameters
params = {
	'convert': currency.upper(),
	'symbol': ','.join(coin.upper() for coin in coins)
}

# Add the API key as the expected header field
headers = {'X-CMC_PRO_API_KEY': config['general']['api_key']}

# Request the chosen price pairs
response = requests.get(API_URL, params=params, headers=headers, timeout=2)
if response.status_code != 200:
	print(f'Coinmarketcap API returned non 200 response:\n', response.content)
	sys.exit(1)

# Get a list of the chosen display options
display_options = config['general']['display'].split(',')

# Waybar prefers a json output with the following structure.
output_obj = {
	'text': '',
	'tooltip': 'Cryptocurrency metrics from Coinmarketcap:\n',
	'class': 'crypto'
}

# For each coin, populate our output_obj with a string, according to the display_options
for coin in coins:
	icon = config[coin]['icon']
	
	# Extract the object relevant to our coin/currency pair
	pair_info = response.json()['data'][coin.upper()]['quote'][currency]

	output = f'{icon} '
	# Shows price by default
	if 'price' in display_options or not display_options:
		current_price = round(Decimal(pair_info['price']), 2)
		output += f'{currency_symbol}{current_price} '
	if 'volume24h' in display_options:
		percentage_change = round(Decimal(pair_info['volume_24']), 2)
		output += f'24h:{currency_symbol}{percentage_change:+} '
	if 'change24h' in display_options:
		percentage_change = round(Decimal(pair_info['percent_change_24h']), 2)
		output += f'24h:{percentage_change:+}% '
	if 'change1h' in display_options:
		percentage_change = round(Decimal(pair_info['percent_change_1h']), 2)
		output += f'1h:{percentage_change:+}% '
	if 'change7d' in display_options:
		percentage_change = round(Decimal(pair_info['percent_change_7d']), 2)
		output += f'7d:{percentage_change:+}% '

	output_obj['text'] += output
	output_obj['tooltip'] += output

# Write the output_obj dict as a json string to stdout
sys.stdout.write(json.dumps(output_obj))