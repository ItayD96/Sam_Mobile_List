#!/isr/bin/python3

import json
import os
# Mail library
import smtplib
import subprocess as sp
# Import date class from datetime module
# Check diff and sent a mail to myself
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Call function
from optparse import OptionParser

# Csv options
import pandas as pd
# Url get info
import requests
from bs4 import BeautifulSoup
# Progress bar
from tqdm import tqdm

import config

# Json headers
Headers = ["Model", "Firmware", "Country/Carrier", "Date", "PDA", "Version"]


def main():
    # parser options to choose the output name
    parser = OptionParser()
    parser.add_option('-o', '--outfile', help='Final csv file name [Defulte = output.csv]')
    parser.add_option('-c', '--csv', help='If you want csv file add the name [Optional]')
    parser.add_option('-e', '--email', help='optional to get email if there is diff , Enter your mail.')
    parser.add_option('-C', '--country', help='optional to check for specific **country code**.')
    (options, args) = parser.parse_args()

    # create the output json file
    if options.outfile is None:
        output = open('output_' + str(date.today()) + '.csv', 'w')
    else:
        if options.outfile[-5:] == '.csv':
            output = open(options.outfile, 'w')
        else:
            output = open(options.outfile + '.csv', 'w')
    # init json file
    # output.write('[\n')

    # receiver_address = options.email
    receiver_address = 'itaydahan96@gmail.com'

    # Header counter
    i = 0
    # Tmp dict
    dict1 = {}
    # Sam-mobile link
    sam_mobile_models = 'https://www.sammobile.com/samsung/'

    # Get the models from sam-mobile site
    models = get_all_models_from_link(sam_mobile_models)

    for model in tqdm(models):
        # TODO : Remove !
        if model != 'galaxy-a10':
            continue
        # Get the main model page for the firmwares check valid address
        result_main = requests.get(sam_mobile_models + model + '/firmware/')
        if result_main.status_code != 200:  # Check valid page
            # print('Error , status code != 200,Model :' + model)
            continue
        else:
            # get all the buttons that mean avail options for firmware
            firmwares = get_all_firmwares_from_button(result_main)
            for firmware in firmwares:
                if options.country is None:
                    result = requests.get(sam_mobile_models + str(model) + "/firmware/#" + str(firmware))
                else:
                    result = requests.get(sam_mobile_models + str(model) + "/firmware/" + str(firmware) + "/" +
                                          str(options.country).upper() + "/#" + str(firmware))
                if result.status_code != 200:  # Check valid page
                    continue
                # get all data from the main table
                df_list = pd.read_html(result.text)  # this parses all the tables in webpages to a list
                df = df_list[0]
                # print(df.to_string())
                output.write(df.to_string())
                df.to_csv(str(output.name).replace('json','csv'))

    print('Finish , File named ' + output.name + ' has created')
    output.close()

    print('check diff with output.json and ' + output.name)
    diff = sp.getoutput('diff output.json ' + output.name)
    diff = ''
    if diff != '':
        print('There is a diff - Mail Sent')
        if options.email is not None:
            sent_email(receiver_address, output.name)
    else:
        print('There is nothing new :)')

    os.system('cp ' + output.name + ' output.json')

    # print('Check if --csv is needed')
    if options.csv is not None:
        get_csv(options.csv, output.name)


def get_all_models_from_link(link: str) -> list:
    model_list = requests.get(link)
    src_model_list = model_list.content
    soup_model_list = BeautifulSoup(src_model_list, 'lxml')
    model_list = soup_model_list.find_all("strong")  # Choose the bold options
    models = []
    for model in model_list:
        if str(model.get_text())[:6].lower() == 'galaxy':  # Only thats starts with galaxy
            model = model.get_text().replace(' ', '-').replace('+', '-plus').lower()  # Same variable
            models.append(model)
    return models


# get all the buttons that mean avail options for firmware
def get_all_firmwares_from_button(result_main: requests.models.Response) -> list:
    src_main = result_main.content
    soup_main = BeautifulSoup(src_main, 'lxml')
    # Get firmwares as buttons
    firmware_list = soup_main.find('div', attrs={'class': "main-content-item__subtitle nav"})
    unselected_firms = firmware_list.find_all('button', {'class': 'nav-link badge badge-success-outline'})
    curr_firm = firmware_list.find_all('button', {'class': 'nav-link badge badge-success-outline active'})
    firmware_list = curr_firm + unselected_firms
    firmwares = []
    for firmware_button in firmware_list:
        firmware = firmware_button.get_text().strip('\n').strip(' ')
        firmwares.append(firmware)
    return firmwares


def sent_email(receiver_address: str, diff: str):
    # Setup the MIME
    message = MIMEMultipart()
    message['From'] = config.sender_address
    message['To'] = receiver_address
    message['Subject'] = 'My script just found a new firmware !'  # The subject line

    diff = diff.replace('<', '').replace('\'', '').replace('},{\n', '').replace('---', '') \
               .replace('\ No newline at end of file\n', '').replace('}]', '').replace('>', '').split()[1:-1]
    mail_content = ''.join(diff)
    message.attach(MIMEText(mail_content, 'plain'))
    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.starttls()  # enable security
    session.login(config.sender_address, config.sender_pass)  # login with mail_id and password
    text = message.as_string()
    session.sendmail(config.sender_address, receiver_address, text)
    session.quit()


def get_csv(csv_name: str, output_name: str):
    with open(output_name) as f:
        output = json.load(f)
    if csv_name[-4:] != '.csv':
        csv_name = csv_name + '.csv'
    print('csv file named : ' + csv_name + ' has created')
    csv_data = pd.DataFrame(output)
    csv_data.to_csv(str(csv_name))
    f.close()


if __name__ == "__main__":
    main()
    exit()


"""

                src = result.content
                soup = BeautifulSoup(src, 'lxml')
                table = soup.find('div', attrs={'id': firmware})  # find the main table
                if table is None:
                    continue
                else:
                    today = "".join(str(date.today()))
                    last_update = today
                    for row in table.findAll('td'):  # find all the rows
                        tmp = row.get_text()
                        if tmp not in Headers:
                            if i == 0:  # Update the model every time
                                dict1[str(Headers[i])] = model
                                i += 1
                            # for some reason its duplicate
                            elif i == 3:  # the date field
                                ver_date = tmp.strip('\n')
                                if ver_date < last_update:
                                    # don't add ',' at the beginning
                                    if last_update is not today:
                                        output.write(',')
                                    last_update = ver_date
                                else:
                                    # to get out from this model
                                    break
                            dict1[str(Headers[i])] = tmp.strip('\n')  # strip('\n') to cut of \n , inset to the json
                            if i == 5:
                                json.dump(dict1, output, indent=6, sort_keys=False)
                                i = -1  # Reset the counter
                            i += 1
    output.write(']')

"""
