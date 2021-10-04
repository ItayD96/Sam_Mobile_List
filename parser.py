#!/isr/bin/python3

import json
import pandas as pd
from optparse import OptionParser


def main():
    parser = OptionParser()
    parser.add_option('-i', '--input', type='string', help='Name of Input - txt File')
    parser.add_option('-o', '--outfile', help='Name of the Output - JSON File')

    (options, args) = parser.parse_args()

    # open the files
    if (options.outfile is None):
        output = open("output.json", "w")
    else:
        if (str(options.outfile).endswith('.json')):
            output = open(options.outfile, 'w')
        else:
            output = open(options.outfile + '.json', 'w')

    if (options.input is None):
        f = open('output.txt', 'r')
    else:
        if (options.input[-4:] == '.txt'):
            f = open(options.input, 'r')
        else:
            f = open(options.input.endswith('.txt'), 'r')


    # Json headers
    headers = ["Model", "Firmware", "Country", "Date", "PDA", "Version"]
    # Tmp dict
    dict1 = {}
    # Get the file path+name.
    worksheet = pd.read_excel('getFrim/Models and Firmwares.xls', sheet_name='Models and Firmwares')

    i = 0  # For filling right the Json file
    j = 0  # For check next model

    model = worksheet.columns
    curr_model = model[0].strip('\n')
    #print(model[j + 1].strip('\n'))
    for line in f.readlines():

        if (line.strip('\n') == curr_model):  # For the first case
            continue

        if (line.strip('\n') == model[j + 1].strip('\n')):  # check if needed to update curr model
            curr_model = model[j + 1]
            j += 1
            print(curr_model,file=output)
            continue

        if (i == 0):  # Update the model every time
            dict1[str(headers[i])] = curr_model
            i += 1

        dict1[str(headers[i])] = line.strip('\n')  # strip('\n') to cut of /n , inset to the json
        if (i == 5):
            json.dump(dict1, output, indent=6, sort_keys=False)
            i = -1  # Reset the counter

        i += 1

    # closing the files
    f.close()

    print('Finish , File named ' + output.name + ' has created')

    output.close()



if __name__ == "__main__":
    main()
    exit()
