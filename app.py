#!/isr/bin/python3

import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlrd
from openpyxl import Workbook, load_workbook
from optparse import OptionParser


def main():
    # Data to be written
    parser = OptionParser()
    parser.add_option('-i', '--input', type='string', help='The excel file to convert')
    parser.add_option('-o', '--outfile', help='Final txt file name')

    (options, args) = parser.parse_args()

    if (options.input is None):
        worksheet = pd.read_excel('getFrim/Models and Firmwares.xls')
    else:
        if (options.input[-4:-1] == '.xls'):
            worksheet = pd.read_excel('getFrim/Models and Firmwares.xls')
        else:
            worksheet = pd.read_excel(options.input + '.xls')
        if (worksheet is None):
            print('Fail to read the input txt file')
            exit()

    if (options.outfile is None):
        output = open("output.txt", "w")
    else:
        if (options.outfile[-4:] == '.txt'):
            output = open(options.outfile, 'w')
        else:
            output = open(options.outfile +'.txt', 'w')


    for model in worksheet.columns:
        i = 0
        firmware = worksheet.at[i, model]

        last = worksheet[model].iloc[[-1]].astype(str).tolist()
        last = ''.join(last)
        print(model,file=output)
        print(model)
        while (str(firmware) != last):  # str(firmware) != 'nan' and

            firmware = worksheet.at[i, model]
            result = requests.get("https://www.sammobile.com/samsung/" + str(model) + "/firmware/#" + str(firmware))

            if result.status_code != 200:
                print("Error , status code != 200,Exit.")
                exit()

            src = result.content
            soup = BeautifulSoup(src, 'lxml')
            table = soup.find('div', attrs={'id': firmware})
            if (table is None):
                # print('Table is None !!')
                break
            else:
                for row in table.findAll('td'):
                    tmp = row.get_text()
                    if tmp != 'Model' and tmp != 'Country/Carrier' and tmp != 'Date' and tmp != 'PDA' and tmp != 'Version':
                        print(tmp,file=output)

            i += 1


if __name__ == "__main__":
    main()
    exit()
