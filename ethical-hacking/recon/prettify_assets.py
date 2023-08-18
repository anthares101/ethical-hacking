# Python 3 requirements: json, xlsxwriter
#
# Script to read the domains_to_assets.py JSON output and return a pretty print of it.

import json
import collections
import re
import argparse
import xlsxwriter
import os

from tabulate import tabulate


parser = argparse.ArgumentParser(
	description='Takes a JSON file generated by domains_to_assets.py and prints the result in a pretty way.'
)
parser.add_argument('-if', '--input-file', type=str, help='JSON file generated by domains_to_assets.py', required=True)
parser.add_argument('-oX', type=str, metavar='XLSX_FILE', help='generate a XLSX file', required=False)

args = parser.parse_args()
input_file = args.input_file
xlsx_file = args.oX

try:
	with open(input_file) as assets_file:
		assets = json.load(assets_file)
except:
	print('Error opening input file!')
	exit()

# Parse JSON
try:
	parsed_dict = collections.defaultdict(list)
	for asset in assets.keys():
		# Get only the IPs for domains
		ips_and_domains = asset.split(',')
		ips = ''
		for ip_or_domain in ips_and_domains:
			ipv4_regex = '^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$'
			ipv6_regex = '((([0-9a-fA-F]){1,4})\\:){7}([0-9a-fA-F]){1,4}'
			if re.search(ipv4_regex, ip_or_domain) or re.search(ipv6_regex, ip_or_domain):
				if ips:
					ips = ips + ','
				ips = ips + ip_or_domain

		# Order by TLD
		domains = assets[asset]
		for domain in domains:
			tld = '.'.join(domain.split('.')[-2:])
			parsed_dict[tld].append([domain, ips])
except:
	print('Input file format not correct!')
	exit()

# Pretty print and XLSX generation if needed
try:
	workbook = None
	if xlsx_file:
		if os.path.exists(xlsx_file):
	  		os.remove(xlsx_file)
		workbook = xlsxwriter.Workbook(xlsx_file)

	for tld in parsed_dict.keys():
		domains_and_ips = parsed_dict[tld]
		print(tabulate(domains_and_ips, headers=[tld], tablefmt='github'))
		print()

		if workbook:
			worksheet = workbook.add_worksheet(tld)
			cell_format = workbook.add_format({'bg_color': '#0070c0', 'font_color': 'white'})
			worksheet.write(0, 0, tld, cell_format)
			worksheet.write(0, 1, '', cell_format)
			worksheet.write(0, 2, '', cell_format)

			row = 1
			cell_format = workbook.add_format({'bg_color': '#b4c6e7'})
			for domain_and_ip in domains_and_ips:
				worksheet.write(row, 0, domain_and_ip[0], cell_format)
				worksheet.write(row, 1, domain_and_ip[1], cell_format)
				worksheet.write(row, 2, '', cell_format)
				row+=1
			worksheet.autofit()

	if workbook:
		workbook.close()
except:
	print('Error trying to save XLSX file!')
