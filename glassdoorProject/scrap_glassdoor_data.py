from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
import json
import os

def get_jobs(title, location , num_jobs, slp_time , verbose, folder_name):
        
    '''Gathers jobs as a dataframe, scraped from Glassdoor'''
    
    #Initializing the webdriver
    options = webdriver.ChromeOptions()

    
    #Uncomment the line below if you'd like to scrape without a new Chrome window every time.
#     options.add_argument('headless')
    
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)
    driver.set_window_size(1120, 1000)
    url = 'https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword=&typedLocation=&locT=&locId=&jobType=&context=Jobs&sc.keyword=&dropdown=0'
    driver.get(url)
    time.sleep(10)

    # Input job and location
    job_title = driver.find_element_by_id('KeywordSearch')
    job_location = driver.find_element_by_id('LocationSearch')
    print(job_title , job_location)
    job_title.clear()
    job_location.clear()
    time.sleep(3)
    job_title.send_keys(title)
    job_location.send_keys(location)
    job_location.send_keys(Keys.ENTER)    
        
    jobs = []
    count = 0  
    while len(jobs) < num_jobs:  #If true, should be still looking for new jobs.        
        #Let the page load. Change this number based on your internet speed.
        #Or, wait until the webpage is loaded, instead of hardcoding it.
        time.sleep(slp_time)
        job_buttons = driver.find_elements_by_xpath('//div[@class="d-flex justify-content-between align-items-start"]') #These are the buttons we're going to click.
        time.sleep(2)
        print(len(job_buttons))
        for job_button in job_buttons:
            try:
                try:
                    driver.find_element_by_xpath('//span[@alt="Close"]').click()
                    print(' x out worked 1')
                except NoSuchElementException:
                    print(' x out failed 1')
                    pass
                job_button.click()
                print('clicked job')
                time.sleep(1)
                try:
                    driver.find_element_by_xpath('//span[@alt="Close"]').click()
                    print(' x out worked 2')
                except NoSuchElementException:
                    print(' x out failed 2')
                    pass
                
                time.sleep(1)
                collected_successfully = False

                while not collected_successfully:
                    print('in loop')
                    try:
                        company_name = driver.find_element_by_xpath('//div[@class="css-xuk5ye e1tk4kwz5"]').text
                        job_title = driver.find_element_by_xpath('//div[@class="css-1j389vi e1tk4kwz2"]').text
                        location = driver.find_element_by_xpath('//div[@class="css-56kyx5 e1tk4kwz1"]').text
                        job_description = driver.find_element_by_xpath('//div[@class="jobDescriptionContent desc"]').text
                        collected_successfully = True
                    except:
                        print('not found company or job or location')
                        time.sleep(5)
                try:
                    salary_estimate = driver.find_element_by_xpath('//span[@class="css-56kyx5 css-16kxj2j e1wijj242"]').text
                except :
                    salary_estimate = -1 #You need to set a "not found value. It's important."

                try:
                    rating = driver.find_element_by_xpath('.//span[@data-test="detailSalary"]').text
                except :
                    rating = -1 #You need to set a "not found value. It's important."

                    
                job_detials = {"Job Title" : job_title,
                "Salary Estimate" : salary_estimate,
                "Job Description" : job_description,
                "Rating" : rating,
                "Company Name" : company_name,
                "Location" : location          
                }
                try:      
                    time.sleep(2)
                    driver.find_element_by_xpath('//div[@class="css-1ap6ha9 ef7s0la0" or @data-test="overview"]').click()
                    time.sleep(1)
                    
                    blocks = driver.find_elements_by_xpath("//div[@class='d-flex justify-content-start css-daag8o e1pvx6aw2']")
                    
                    for block in blocks:
                        name = block.find_element_by_xpath("./span[@class='css-1pldt9b e1pvx6aw1']")
                        value = block.find_element_by_xpath("./span[@class='css-1ff36h2 e1pvx6aw0']")
                        job_detials[name.text] = value.text                    

                except :
                    # Some job postings do not have the "Company" tab.
                     pass
                
                #add job to jobs
                jobs.append(job_detials)
                if verbose:
                    print(job_detials)
                

                count=count+1
                print(count)  # To see how many record scraped
                
                # if your internet not stable so run code below that turn dict to json and save it 
# =============================================================================
#                 os.mkdir(folder_name)
#                 with open(folder_name+"/"+str(count)+'.json', 'w', encoding='utf8') as fp:
#                     json.dump(job_detials, fp, ensure_ascii = False)
# =============================================================================
            except:
                pass
        
        #Clicking on the "next page" button
        try:
            driver.find_element_by_xpath('//a[@data-test="pagination-next"]').click()
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs, len(jobs)))
            break

    return pd.DataFrame(jobs)  #This line converts the dictionary object into a pandas DataFrame.



title = 'data science'    # Job you want to scrap
location = 'usa'           # Location 
verbose = 1                 # If you want to print dictionary 
num_jobs = 1000            # number of jobs you want
slp_time = 5             # sleep time for load page depend on your internet
folder_name = f"{title}_{location}_jsons"
folder_name = folder_name.replace(" ","")
# Put data in dataFrame 
df = get_jobs(title,location, num_jobs , slp_time , verbose , folder_name)

# Save data
df.to_csv(folder_name+'.csv' , index=False)

# If use json then uncomment
# To load json files into DataFrame

# =============================================================================
# path_to_json = 'jobs_json'
# json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
# job_list = []
# for i in range(len(json_files)):
#     with open(path_to_json+'/'+json_files[i] , encoding='utf-8') as f:
#         d = json.load(f )
#         job_list.append(d)
# df = pd.DataFrame.from_dict(job_list, orient='columns')
# df.to_csv(folder_name+'.csv' , index=False)
# =============================================================================
