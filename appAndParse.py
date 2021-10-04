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
    parser.add_option('-o', '--outfile', help='Final Json file name')

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
        output = open("output.json", "w")
    else:
        if (options.outfile[-4:] == '.json'):
            output = open(options.outfile, 'w')
        else:
            output = open(options.outfile +'.json', 'w')

    # Json headers
    headers = ["Model", "Firmware", "Country", "Date", "PDA", "Version"]
    # Header counter
    i =0
    # Tmp dict
    dict1 = {}
    # Get the file path+name.
    worksheet = pd.read_excel('getFrim/Models and Firmwares.xls', sheet_name='Models and Firmwares')


    for model in worksheet.columns:
        j = 0                           # j for the frimware number
        firmware = worksheet.at[j, model]

        last = worksheet[model].iloc[[-1]].astype(str).tolist()
        last = ''.join(last)

        print(model)
        while (str(firmware) != last ):  # while there are more firmwares

            firmware = worksheet.at[j, model]
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
                        if (i == 0):  # Update the model every time
                            dict1[str(headers[i])] = model.strip('\n')
                            i += 1

                        dict1[str(headers[i])] = tmp.strip('\n')  # strip('\n') to cut of /n , inset to the json
                        if (i == 5):
                            json.dump(dict1, output, indent=6, sort_keys=False)
                            i = -1  # Reset the counter

                        i += 1

            j += 1

    print('Finish , File named ' + output.name + ' has created')

    output.close()


if __name__ == "__main__":
    main()
    exit()
