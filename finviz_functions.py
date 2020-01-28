import pandas as pd
from pandas import ExcelWriter
from datetime import date
import requests
#import matplotlib.pyplot as plt

def get_ticker_data(ticker):
    url = 'https://finviz.com/quote.ashx?t={}'.format(ticker)

    response = requests.get(url).content
    ticker_dfs = pd.read_html(response)

    ticker_financials = ticker_dfs[6]

    sector, industry, country = ticker_dfs[5][0][2].split('|')
    ind = format_string(industry)

    return(ticker_financials, ind)

def get_comp_data(ind):
    pg = 1
    
    val_data, pages = extract_data_table(ind, '121', pg)
    fin_data, pages = extract_data_table(ind, '161', pg)
    
    while pg < pages:
        pg += 1
        val_data = pd.concat([val_data, extract_data_table(ind, '121', pg)[0]])
        fin_data = pd.concat([fin_data, extract_data_table(ind, '161', pg)[0]])
    
    comp_data = pd.concat([val_data, fin_data],axis=1)
    comp_data = comp_data.T.drop_duplicates().T

    return(comp_data)

def extract_data_table(ind, code, page):
    
    url = 'https://finviz.com/screener.ashx?v={}&f=ind_{}&r={}1'.format(code,ind,page*2-2)
    html_response = requests.get(url).content

    dfs = pd.read_html(html_response)
    
    pages = dfs[13][3].str.split('/')[0][-1]
    
    data_table = dfs[14]
    headers = data_table.iloc[0]
    data_table = pd.DataFrame(data_table.values[1:], columns=headers).set_index('No.')
    
    return(data_table, int(pages))

def format_string(data_string):
    return(data_string.lower().replace(" ","").replace("-","").replace("&",""))

def format_data_to_floats(table):
    for col in table:
        table[col] = table[col].str.strip("%").replace('-',0)
        table[col] = pd.to_numeric(table[col], errors='ignore')

def write_data_to_file(list_dfs, ticker):
    file_name = 'Security_Comps'+ ticker + '.xlsx'
    xls_path = '/Users/jakerobinson/Documents/CCA_Finviz/' + file_name

    with ExcelWriter(xls_path) as writer:
        for m, data in enumerate(list_dfs):
            for n, df in enumerate(data):
              if n == 0:
                df.to_excel(writer, 'Financials - ' + ticker)
              if n == 1:
                df.to_excel(writer, 'Comparable Companies')
        writer.save()
