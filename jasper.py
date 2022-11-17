#!/usr/bin/env python3

# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
import random
import pandas as pd
import datetime
import os
import os.path
import time
import csv
import creds
import glob

def user_agent():
    user_agent_list = []
    with open('user_agents.csv', 'r') as f:
        for agents in f:
            user_agent_list.append(agents)
    return user_agent_list

def convert_row( row ):
    row_dict = {}
    for key, value in row.items():
        keyAscii = key.encode('ascii', 'ignore' ).decode()
        valueAscii = value.encode('ascii','ignore').decode()
        row_dict[ keyAscii ] = valueAscii
    return row_dict

def work_jasper():
    time_start = datetime.datetime.now().replace(microsecond=0)
    directory = os.path.dirname(os.path.realpath(__file__))

    user_agents = user_agent()

    # Setup random proxy and user-agent
    random_user_agents = random.randint(1, len(user_agents) - 1)
    print(user_agents[random_user_agents])
    options = {
        'user-agent': user_agents[random_user_agents],
        'suppress_connection_errors': True,
        'verify_ssl': True
    }

    options = {
        'user-agent': user_agents[random_user_agents]
        # 'suppress_connection_errors': True
    }

    driver_path = os.path.join(directory, glob.glob('./chromedriver*')[0])
    browser = webdriver.Chrome(executable_path=driver_path, seleniumwire_options=options)

    browser.set_window_size(1920, 1080)

    composed_list = []
    prompt_list = []
    city_list =[]
    url_list = []

    browser.get('https://app.jasper.ai/')
    uname = browser.find_element(By.ID, "email")

    uname.send_keys(creds.USERNAME)

    # Click Recaptcha
    # WebDriverWait(browser, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']")))
    # WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="recaptcha-anchor"]'))).click()
    
    # browser.switch_to.default_content()

    time.sleep(2)

    uname.submit()

    time.sleep(10)

    signincode = browser.find_element(By.ID, "signInCode")
    time.sleep(20)
    signincode.submit()
    time.sleep(20)

    # WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div/nav[1]/ul[2]/li/a'))).click()
    template_click = browser.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div/nav[1]/ul/li[2]/a')
    template_click.click()
    time.sleep(7)
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="template-card"][12]'))).click()
    time.sleep(7)

    # change the input from 3 to 1
    change_input = WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[1]/div[3]/div/div[1]/form/div[3]/div/div/input')))
    change_input.clear()
    time.sleep(2)
    change_input.send_keys(1)

    with open('query.csv') as f:
        reader = csv.DictReader(f)

        for line in reader:

            converted_row = convert_row(line)
            url = converted_row['URL']
            city = converted_row['City']
            prompt = converted_row['prompt']
            try:
                
    
                # input_editor = browser.find_element(By.CLASS_NAME, 'ql-editor')
                #input command jasper
                input_editor = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.ID, 'form-field-command')))
                input_editor.clear()
                time.sleep(2)
                input_editor.send_keys(prompt)
                time.sleep(2)
                
                # click the generate button
            
                WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="generateBtn1"]/div[1]'))).click()
                time.sleep(7)
                # compose = browser.find_element(By.XPATH, '//*[@id="app"]/div[1]/div[1]/div/div/div[5]/div/div[2]/div/div/button')
                # compose.click()
                # WAIT FOR PROMT DIV
                # get the result/prompted text
                # composed_prompt = browser.find_element((By.CLASS_NAME, 'w-full mt-2 mb-3'))
                
                composed_prompt_text = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.XPATH, '//div[@class="w-full mt-2 mb-3 text-base font-medium leading-7 text-gray-800 whitespace-pre-wrap pre"]')))
                composed_prompt = composed_prompt_text.get_attribute("textContent")
               
                composed_list.append(composed_prompt)
                print(f'{composed_prompt}\n')
                prompt_list.append(prompt)
                city_list.append(city)
                url_list.append(url)
                time.sleep(2)
                # click the clear button to remove all the text in prompted input
                click_clear = browser.find_element(By.XPATH,'//button[@class="relative transition-all duration-150 before:transition-all before:duration-150 before:absolute before:inset-0 px-3 py-2 text-xs font-medium leading-4 text-gray-400 hover:text-gray-600 before:bg-gray-100 before:rounded-lg before:scale-50 before:opacity-0 hover:before:scale-100 hover:before:opacity-100"]')
                click_clear.click()
                time.sleep(3)
               
            except:
                composed_list.append('Unexpected error')
                prompt_list.append(prompt if prompt != '' else 'Unexpected error')
                url_list.append(url if url != '' else 'Unexpected error')
                city_list.append(city if city != '' else 'Unexpected error')
                pass

    time_end = datetime.datetime.now().replace(microsecond=0)
    runtime = time_end - time_start
    print(f"Script runtime: {runtime}.\n")

    # Save scraped URLs to a CSV file
    now = datetime.datetime.now().strftime('%Y%m%d-%Hh%M')
    print('Saving to a CSV file...\n')
    data = { "Url":url_list, "City":city_list, "Prompt": prompt_list,"Composed": composed_list}
    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.transpose()

    filename = f"jasper_composed{ now }.csv"

    print(f'{filename} saved sucessfully.\n')

    file_path = os.path.join(directory, 'csvfiles/', filename)
    df.to_csv(file_path)

    browser.quit()

    time_end = datetime.datetime.now().replace(microsecond=0)
    runtime = time_end - time_start
    print(f"Script runtime: {runtime}.\n")

if __name__ == '__main__':
    work_jasper()
