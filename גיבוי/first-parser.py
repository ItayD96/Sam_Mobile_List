#!/isr/bin/python3

import json

def main():
    # Json header
    headers =["Model","Country","Date","PDA","Version"]
    # tmp dict
    dict1 ={}
    
    # open the files
    output = open("output.json", "w")
    f = open('output.txt','r')
    
    i = 0
    for line in f.readlines() :
        #print(line)
        dict1[str(headers[i])] = line[:-1]      # [:-1] to cut of /n
        if(i == 4):
            json.dump(dict1,output,indent = 5, sort_keys = False)
            i =-1
            #print ('-------Finish 1 dict ----------------')
        i+=1

    # closing the files
    f.close()
    output.close()
    
    print('Finish , File named output.json has created')

if __name__ == "__main__":
    main()
    exit()

