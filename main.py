# Coded By @NavinJethwani.

# One should install selenium,requests,BeautifulSoup,pandas,webdriver-manager or run pip install -r requirements.txt
# before running the script else the script will give an error of module not found.

# This is a python script to scrap data across all the pages of https://www.stfrancismedicalcenter.com/find-a-provider
# this code uses selenium because the data of doctors changes across all the pages but the url 
# does not change and to catch all the data across all the pages selenium is required to change the pages and
# scrap the data. 
# if this was done through only requests or urllib libraries, the data on only 1st page would have returned.

def main():
    #importing required libraries and packages
    import requests
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
    import pandas as pd
    import time
    from csv import DictWriter

    urls_of_all_doctors = []
    # initializing webdriver.
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    url = 'https://www.stfrancismedicalcenter.com/find-a-provider'
    driver.get(url)
    time.sleep(5)
    total_pages = driver.find_element(By.CLASS_NAME,'end').text
    total_pages = int(total_pages)
    print('-->Total pages: ',total_pages)
    # below for loop will scrap all the data on every page of the url given and append all the links of all
    # the doctors in a variable urls_of_all_doctors.
    for _ in range(total_pages -1):
        page_source = driver.page_source
        soup = BeautifulSoup(page_source,features='html.parser')
        ul = soup.find('div',{"class":'doctor-results'})
        list_items = ul.find_all('li',{"data-role":'tr'})
        for item in list_items:
            link_a = item.find('a')
            link = link_a.attrs['href']
            
            # below if condition is required because if the link of any doctor on any page is not
            # written in html, the script eill continue running. If we remove below if condition the script eill
            # throw an error because one of the docotrs on page 32 id missing link.
            if len(link.split('/'))>1:
                link = link.split('/')[2]
                urls_of_all_doctors.append(url + "/" + link)
        
        next_page_ele = driver.find_element(By.CLASS_NAME, "next")
        next_page_ele.click()
        time.sleep(10)
    driver.close()
    print('\n-->Gathered all the links across all the pages.\n-->Procedding to gather data from links.\n')
    
    # below mentioned field names are required to append each data row in csv file.
    field_names = ['Full Name','Specialty','Add Specialty','Full Address','Practice','Address','City','State','Zip','Phone','URL']
    
    # below for loop sends a get request to each link stored in variable urls_of_all_docotrs and
    # returns the html response in variable response and that response is furthur processed by BeautifulSoup
    print('-->Appending data to a csv file. Please wait till the process completes.')
    for link in urls_of_all_doctors:
        response = requests.get(link)
        soup = BeautifulSoup(response.content,features='html.parser')
        content = soup.find('div',{"class":"content-zone"})
        name = content.find('h1').text
        speciality = speciality = content.find('a')
        speciality = speciality.text.strip()
        keys = content.find_all('strong',{"class":"label-style"})
        values = content.find_all('span',{"class":"two-thirds"})
        
        # this additional for loop is required because some doctors have an additional speciality while
        # some do not.
        for key in keys:
            if "Additional Specialty:" in key.text:
                Additional_Specialty = values[1].text
                Additional_Specialty = Additional_Specialty.strip()
        
        address = content.find('address').text.strip()
        address_list = address.split(',')
        phone_number = address_list[-1].split("\t")[-1]
        address = address[0:-12]
        address = address.strip()
        phone_number = phone_number.strip()
        additional_address = content.find('strong',{"class","title-style-5"}).text
        
        # below if condition is required because some doctors have an additional address while others don't.
        if len(additional_address) > 1:
            full_address = additional_address + ';' +  address
        else:
            full_address = address
        
        splitted_address = address.split(' ')
        zip_code = splitted_address[-1]
        state = splitted_address[-2]
        city = splitted_address[-3]
        city = city.split(',')[0]
        
        # making a dictionary object for each doctor so it is easy to append the data in csv file.
        data = {
        'Full Name':name,
        'Specialty':speciality,
        'Add Specialty':Additional_Specialty,
        'Full Address':full_address,
        'Practice':additional_address,
        'Address':address,
        'City':city,
        'State':state,
        'Zip':zip_code,
        'Phone':phone_number,
        'URL':link
        }
        
        # appending data in csv file using python file handling.
        with open('data.csv', 'a') as f_object:
            dictwriter_object = DictWriter(f_object, fieldnames=field_names)
            dictwriter_object.writerow(data)
    
    # this is done to remopve extra lines from the csv file.  
    df = pd.read_csv('data.csv')
    df.to_csv('data.csv', index=False)
    print('--> Process Completed Successfully. Check file data.csv.')


if __name__ == '__main__':
    main()