import json
import requests
from bs4 import BeautifulSoup

# Writing to an excel 
# sheet using Python
import xlwt
  
def main():
    # Workbook is created
    wb = xlwt.Workbook()

    # add_sheet is used to create sheet.
    sheet1 = wb.add_sheet('Models and Firmwares',cell_overwrite_ok=True)
    bold = xlwt.easyxf('font: bold 1')
    col=0
    f = open('inputModelList.txt','r')
    for line in f.readlines() :
        #use req.get with dynamic url from the list
        model =line.replace(' ','-').replace('+','-plus').lower()[:-1] 
        result = requests.get('https://www.sammobile.com/samsung/' + model + '/firmware/')
        
        #check valid address
        if(result.status_code != 200):
            print('Error , status code != 200,Model :' + model )
            continue
        else:
            row=0
            sheet1.write(row,col, model,bold)
            #get all the buttons that mean avail options for firmware
            src = result.content
            soup = BeautifulSoup(src ,'lxml')
            button_list= soup.find('div' , attrs = {'class' :"main-content-item__subtitle nav"})    
            button_list = button_list.find_all('button', {'class': 'nav-link badge badge-success-outline'})
            for button in button_list:
                row+=1
                sheet1.write(row, col,button.get_text().strip('\n').strip(' '))        #Slicing using strip because write with \n at the beginning 
            col +=1
   
    f.close()
    wb.save("Models and Firmwares.xls")

if __name__ == '__main__':
    main()
    exit()
