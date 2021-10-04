#!/isr/bin/python3

import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlrd
from openpyxl import Workbook, load_workbook



def main():
    #model = input("Enter your galaxy model (ex s9):")
    #sub_model = input("Enter galaxy sub Model (ex SM-G9600):")
    #country = input("Enter the Country code ( ex iraq = MID) :")
  
    # Data to be written

   
    result = requests.get("https://www.sammobile.com/samsung/galaxy-s5/firmware/#SC-04F")
    
    #worksheet = pd.read_excel('getFrim/Models and Firmwares.xls', sheet_name='Models and Firmwares')
    
            #print(model)
            #result = requests.get("https://www.sammobile.com/samsung/"+model+'/firmware/#' + firmware )
    if(result.status_code != 200):
                print("Error , status code != 200,Exit.")
                exit()

    src = result.content
    soup = BeautifulSoup(src ,'lxml')
    table = soup.find('div' , attrs = {'id' :"SC-04F"})
    #print(table.prettify())
    for row in table.findAll('td'):        
        tmp=row.get_text()
        if tmp != 'Model' and tmp != 'Country/Carrier'and tmp != 'Date' and tmp != 'PDA' and tmp != 'Version' :
            print(tmp)
    

if __name__ == "__main__":
    main()
    exit()
