#!/isr/bin/python3

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


def main():
    # parser options to choose the output name
    parser = OptionParser()
    parser.add_option('-o', '--outfile', help='Final csv file name [Defulte = output.csv]')
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

    # receiver_address = options.email
    receiver_address = 'itaydahan96@gmail.com'


    # Tmp dict
    dict1 = {}
    # Sam-mobile link
    sam_mobile_models = 'https://www.sammobile.com/samsung/'

    # Get the models from sam-mobile site
    models = get_all_models_from_link(sam_mobile_models)
    df_list = []
    for model in tqdm(models):
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
                data = pd.read_html(result.text, header=None)
                df_list.append(data[0])

    merged = pd.concat(df_list, ignore_index=True)
    # df_list.to_csv(str(output.name), index=False)
    merged.to_csv(str(output.name), index=False)
    print('Finish , File named ' + output.name + ' has created')
    output.close()

    # TODO - diff with another version or the last one
    print('check diff with output.csv and ' + output.name)
    diff = sp.getoutput('diff output.csv ' + output.name)
    if diff != '':
        if options.email is not None:
            print('There is a diff - Mail Sent')
            sent_email(receiver_address, diff)
        else:
            print('There is a diff')

    else:
        print('There is nothing new :)')

    # Move current to output.csv to check with it later
    os.system('cp ' + output.name + ' output.csv')


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


if __name__ == "__main__":
    main()
    exit()
