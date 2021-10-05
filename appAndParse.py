#!/isr/bin/python3

import json
from optparse import OptionParser

import requests
from bs4 import BeautifulSoup


def main():
    # Data to be written
    parser = OptionParser()
    parser.add_option('-i', '--input_list', type='string',
                      help='The Available samsung models https://www.sammobile.com/samsung/')
    parser.add_option('-o', '--outfile', help='Final Json file name')

    (options, args) = parser.parse_args()

    if options.input_list is None:
        print('Must enter list of models visit here : https://www.sammobile.com/samsung/')
        model_list = open('inputModelList.txt', 'r')  # Just for me
        # exit()
    else:
        if options.outfile[-4:] == '.txt':
            model_list = open(options.input_list, 'r')
        else:
            model_list = open(options.input_list + '.txt', 'r')

    if options.outfile is None:
        output = open("output.json", "w")
    else:
        if options.outfile[-5:] == '.json':
            output = open(options.outfile, 'w')
        else:
            output = open(options.outfile + '.json', 'w')

    # Json headers
    headers = ["Model", "Firmware", "Country", "Date", "PDA", "Version"]
    # Header counter
    i = 0
    # Tmp dict
    dict1 = {}

    for line in model_list.readlines():
        # use req.get with dynamic url from the list
        model = line.replace(' ', '-').replace('+', '-plus').lower()[:-1]
        result_main = requests.get('https://www.sammobile.com/samsung/' + model + '/firmware/')
        print(model)
        # check valid address
        if result_main.status_code != 200:
            print('Error , status code != 200,Model :' + model)
            continue

        else:

            # get all the buttons that mean avail options for firmware
            src_main = result_main.content
            soup_main = BeautifulSoup(src_main, 'lxml')
            firmware_list = soup_main.find('div', attrs={'class': "main-content-item__subtitle nav"})
            firmware_list = firmware_list.find_all('button', {'class': 'nav-link badge badge-success-outline'})
            for firmware_button in firmware_list:
                firmware = firmware_button.get_text().strip('\n').strip(' ')

                result = requests.get("https://www.sammobile.com/samsung/" + str(model) + "/firmware/#" + str(firmware))

                if result.status_code != 200:
                    print('Error , status code != 200,Model : ' + str(model + ' Firmware : ' + firmware))

                    exit()

                src = result.content
                soup = BeautifulSoup(src, 'lxml')
                table = soup.find('div', attrs={'id': firmware})
                if table is None:
                    # print('Table is None !!')
                    break
                else:
                    for row in table.findAll('td'):
                        tmp = row.get_text()
                        if [tmp != 'Model' and
                            tmp != 'Country/Carrier' and
                            tmp != 'Date' and
                            tmp != 'PDA' and
                            tmp != 'Version']:
                            if i == 0:  # Update the model every time
                                dict1[str(headers[i])] = model.strip('\n')
                                i += 1

                            dict1[str(headers[i])] = tmp.strip('\n')  # strip('\n') to cut of /n , inset to the json
                            if i == 5:
                                json.dump(dict1, output, indent=6, sort_keys=False)
                                i = -1  # Reset the counter

                            i += 1

    print('Finish , File named ' + output.name + ' has created')

    output.close()
    model_list.close()


if __name__ == "__main__":
    main()
    exit()
