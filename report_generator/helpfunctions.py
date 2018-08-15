
from __future__ import print_function
import json  
import os
#import selenium
#from selenium import webdriver
#from selenium.webdriver.common.by import By
from PIL import Image
from io import BytesIO
from apiclient.http import MediaFileUpload
from time import sleep
import time
import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
import selenium
from selenium import webdriver
from django.template import loader

def setup_googleslides_api():
    SCOPES = ['https://www.googleapis.com/auth/presentations',  'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/analytics']
    store = file.Storage('report_generator/credentials/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('report_generator/credentials/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    slides_service = build('slides', 'v1', http=creds.authorize(Http()))
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))
    return slides_service

def initialize_drive():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
  'report_generator/credentials/service_account_creds.json', 'https://www.googleapis.com/auth/drive.file')
  drive_service = build('drive', 'v3', credentials=credentials)
  return drive_service

def setup_googledrive_api():
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('report_generator/credentials/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('report_generator/credentials/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))
    return drive_service


def initialize_analyticsreporting():
    SCOPES = ['https://www.googleapis.com/auth/analytics']
    KEY_FILE_LOCATION ='report_generator/credentials/service_account_creds.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
    KEY_FILE_LOCATION, SCOPES)

  # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


#Service for google slides API
slides_service = setup_googleslides_api()
#Service for google drive API
drive_service =  setup_googledrive_api()


def create_presentation(title):
    service = slides_service
    body = { 
        'title': str(title)
    }
    presentation = service.presentations().create(body=body).execute()
    presentation_id = presentation.get('presentationId')
    return presentation_id




#A function to duplicate a presentation based off of a presentation id, returning the
#presentation id of the copy
def duplicate_presentation(name, presentation_id):
    service = drive_service
    body = {
        'name': name
    }
    drive_response = service.files().copy(
        fileId = presentation_id, body=body).execute()
    presentation_copy_id = drive_response.get('id')
    return presentation_copy_id
    

 #A function to conduct a find and replace for strings in a presentation with a given id   
def find_replace_str(slides_id, before_str, after_str):
    service = slides_service
    body =  {
        "requests" : [
            {
            "replaceAllText" : {
                "containsText" : {
                    "text" : before_str,
                    "matchCase" : False
                },
               # "pageObjectIds": [
                   # "1" ],
                "replaceText": after_str

            }

            }  
            ] 
         }
   
    response = service.presentations().batchUpdate(presentationId = slides_id, body = body).execute()


#A function to conduct a find and replace, replacing a shape with a specific word in it
#with an image in a presentation with a given id
def find_replace_img(slides_id, shape_text, new_img_url):
    service = slides_service
    body = {
        "requests": [
        {
            "replaceAllShapesWithImage":{
            "imageUrl" : new_img_url,
            "containsText":{
                "text": shape_text,
                "matchCase":False
                 }
            }
        }
    ]
    }
    response = service.presentations().batchUpdate(presentationId = slides_id, body = body).execute()



        



"""variables for screenshots"""
#The port which screenshots will be taken from 
port = '8000'
#The list of urls that will be screenshotted
url_list = ['/traffic', '/leads']

"""Variables for uploading flask and ahrefs screenshots into Google Drive API"""
#Folder in which I have permissions to put files into my drive and remove them
folder_id = '1hScQyb1uMLQaBmNgyHa1dlFZAO2mKzxC'
page_id = 'g202ad04c01_0_6'


"""Reading client data so that functions are performed on correct report"""
with open( 'report_generator/data/client_information.json', 'r') as f:
    clients = json.load(f)
"""Reading client name that was previusly stored when running flask_master_script.py"""

client = "321 Web Marketing"

"""Closing and removing file"""
"""Important variables for ahrefs scrape. The ahrefs scrape master function has a lot of arguments"""
domains_image = 'domains_count.png' #file that the domains ahrefs screenshot will be saved in
keywords_image = 'keyword_count.png' #file that the keywords ahrefs screenshot will be saved in 
images = [domains_image, keywords_image] #A list of these image urls to later loop through
ahrefs_pw = os.environ['AHREFS_PW'] #ahrefs password
ahrefs_un = os.environ['AHREFS_UN'] #ahrefs username
domain_name = clients[client]['domain_name'].replace("https://", "").replace("http://", "").replace('www/', 'www.')
#client domain name that will be used to scrape the correct ahrefs page

def charts_master(clients, client):
    now = datetime.datetime.now()
    reporting_month = now - relativedelta(months=1)
    reporting_month = datetime.datetime.strftime(reporting_month, '%Y/%m' )
    reporting_month = datetime.datetime.strptime(reporting_month, '%Y/%m')

    #Assigning the number of months back
    months_back = 6


    """Getting the Google Analytics View ID for the Traffic Charts"""
    view_id = clients[client]['google_analytics']


    """What
    Converts
    Data"""
    #key and token for 321 API
    api_key_general = "273-f91b45f83365ec4b"
    token_general = "26f9d7d7d282599f161076ad2e4eecfd"
    #key and token for Drew
    api_key_drew = "436-3352b7f7894d34ca"
    token_drew = "705405472f1c25e2bb36a7d8252bd4ad"
    #Account IDs based off of client dictionary
    account_id = clients[client]['what_converts']


    #First we've got a function to get the months that we will pull API data from for Google Analytics
    #and What Converts

    def get_months(reporting_month, months_back):
        list_of_months = []
        for i in range(int(months_back)):
            month_behind = reporting_month - relativedelta(months = i)
            month_behind = datetime.datetime.strftime(month_behind, '%Y/%m')
            list_of_months.append(month_behind)
        return list_of_months



    """ API 
    Calls
    To
    Google
    Analytics"""


    #A function to return a dictionary of new users, per month, by channel grouping
    def get_new_users(month, view_id):
        analytics = get_google_analytics_api.initialize_analyticsreporting()
        analytics = analytics
        dict = {}
        startdate = datetime.datetime.strptime(month, '%Y/%m')
        enddate = startdate + relativedelta(months = 1)
        startdate = datetime.datetime.strftime(startdate, '%Y-%m') + '-01'
        enddate = datetime.datetime.strftime(enddate, '%Y-%m') + '-01'
        response = analytics.reports().batchGet(
            body={
            'reportRequests': [
            {
            'viewId': view_id,
            'dateRanges': [{'startDate': startdate, 'endDate': enddate}],
            'metrics': [{'expression':'ga:newUsers'}],
            'dimensions' : [{ 'name' : 'ga:channelGrouping'}],
            }]
        }
        ).execute()
        for report in response.get('reports', []):
            columnHeader = report.get('columnHeader', {})
            dimensionHeaders = columnHeader.get('dimensions', [])
            metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
            for row in report.get('data', {}).get('rows', []):
                dimensions = row.get('dimensions', [])
                dateRangeValues = row.get('metrics', [])
                for header, dimension in zip(dimensionHeaders, dimensions):
                    dict[dimension] = 0
                for i, values in enumerate(dateRangeValues):
                    for metricHeader, value in zip(metricHeaders, values.get('values')):
                        dict[dimension] =value
        new_users_by_channel_grouping = dict
        return new_users_by_channel_grouping

    #This function makes table out of dictionary
    def get_table(list_of_months,view_id):
        data = {}
        for month in list_of_months:
            data[month] = get_new_users(month, view_id)
        return data

        
    #This function makes a list of all of the unique channel groupings
    def get_unique_channel_groupings(data): 
        unique_channel_groupings = []
        months = data.keys()
        for month in months:
            channels = data[month]
            for channel in channels:
                if  channel not in unique_channel_groupings:
                    unique_channel_groupings.append(channel)
        first, organic = 0, unique_channel_groupings.index('Organic Search')
        unique_channel_groupings[organic], unique_channel_groupings[first] = unique_channel_groupings[first], unique_channel_groupings[organic]
        return unique_channel_groupings

    #This function makes a table with all 0s so that no channel grouping gets left behind if a 
    #channel grouping had a value of 0 that month
    def make_zero_table(months, unique_channel_groupings):
        table = {}
        for month in months:
            table[month] = {}
            for cg in unique_channel_groupings:
                table[month][cg] = '0'
        return table
        
        
    #This function fills in the 0 data table
    def make_table(months, unique_channel_groupings,data, table):
        for month in months:
            for cg in unique_channel_groupings:
                if cg in data[month]:
                    table[month][cg] = data[month][cg]
        return table
                

    #This function makes an interestingly structured dictionary containing months, channels, and data
    #from table
    def get_data(reporting_month,months_back, view_id):
        months = get_months(reporting_month, months_back)
        data = get_table(months, view_id)
        unique_channel_groupings = get_unique_channel_groupings(data)
        table = make_zero_table(months, unique_channel_groupings)
        table = make_table(months, unique_channel_groupings,data, table)
        data = {}
        data["months"] = months
        data["channels"] = unique_channel_groupings
        data["data"] = table
        return data

    #Unfortunately, I need this data to work on flask, and didn't feel like going back and changing everything
    #so this function rearranges the dictionary so it can be looped through on the html (bootstrap) template

    def rearrange_traffic_data(data):
        traffic_data = {}
        months = data["months"]
        channels = data["channels"]
        data = data["data"]
        intermediate_list = []
        channel_list = []
        total = 0
        total_lst = [] 
        #The purpose of these loops is to change the structure of the data
        #so that it can be put into a flask html template
        for month in months:
            intermediate_list.append(data[month])
        for item in intermediate_list:
            for key in item.keys():
                channel_list.append(key + ":" + item[key])
        for i in range(len(months)):
            month = datetime.datetime.strptime(months[i], '%Y/%m')
            month = datetime.datetime.strftime(month, '%b')
            months[i] = month     
        traffic_data["months"] = months[::-1]
        for channel in channels:
            lst = []
            for item in channel_list:
                if channel in item:
                    item = item.replace(channel, "").replace(":", "")
                    lst.append(item)
                    traffic_data[channel] = lst[::-1]
        return traffic_data

    #This kinda just does what I said above
    def traffic_data(reporting_month, months_back, view_id):
        data = get_data(reporting_month, months_back, view_id)
        traffic_data = rearrange_traffic_data(data)
        return traffic_data

    """ API 
    Calls
    To 
    What
    Converts"""


    #This function pulls leads data based off of the list of months
    def pull_lead_data(list_of_months, account_id, client):
        n = 0
        month_lead = {}
        lead_dict = {}
        lead_types = ['phone_call', 'web_form']
        lead_dict['months'] = list_of_months
        for month in list_of_months:  
            lead_dict = {} 
            startdate = datetime.datetime.strptime(month, '%Y/%m')
            enddate = startdate + relativedelta(months = 1)
            startdate = datetime.datetime.strftime(startdate, '%Y-%m') + '-01'
            enddate = datetime.datetime.strftime(enddate, '%Y-%m') + '-01'
            for lead in lead_types:
                params = {
                    'lead_type': lead,
                    'start_date': startdate,
                    'end_date': enddate,
                    'lead_status': 'unique',
                    'account_id' : account_id
                }
                if client == "Comfort Home Care" or client == "Presidential Heat and Air":
                    x = requests.get(
                        'https://app.whatconverts.com/api/v1/leads',
                        auth = (api_key_drew,token_drew),
                        params = params
                        )
                else:
                    x = requests.get(
                        'https://app.whatconverts.com/api/v1/leads',
                        auth = (api_key_general,token_general),
                        params = params
                        )
                json_data = json.loads(x.text)
                lead_dict[lead] = json_data[ "total_leads" ]
                month_lead[month] = lead_dict
        return month_lead
    #This function rearranges the data we just got so that it is suitable for the Flask template
    def rearrange_lead_data(list_of_months, month_lead):
        lead_data = {}
        lead_types = ['phone_call', 'web_form']
        phone_call = []
        web_form = []
        for month in list_of_months:
            for lead_type in lead_types:
                if month_lead[month][lead_type] >= 0 and lead_type=='phone_call':
                    phone_call.append(month_lead[month][lead_type])
                else:
                    web_form.append(month_lead[month][lead_type])
        for i in range(len(list_of_months)):
            month = datetime.datetime.strptime(list_of_months[i], '%Y/%m')
            month = datetime.datetime.strftime(month, '%B')
            list_of_months[i] = month
        list_of_months = list_of_months[::-1]
        phone_call = phone_call[::-1]
        web_form = web_form[::-1]
        lead_data['months'] = list_of_months
        lead_data['Phone Call'] = phone_call
        lead_data['Web Form'] = web_form
        return lead_data           
                
        
            
    #This is kindof like the master function, it returns the dictionary of leads data that will
    #later be used in the Flask template.
    def leads_data(reporting_month, months_back, account_id):
        mo_list = get_months(reporting_month, months_back)
        month_lead = pull_lead_data(mo_list, account_id, client)
        lead_data = rearrange_lead_data(mo_list, month_lead)
        return lead_data


    """
    End 
    of
    API
    call
    to
    WhatConverts
    """


    #Collecting data for content posted during reporting month




    """
    consolidating data so that the Analytics data, WhatConverts data, and Content charts are all in 
    proper html templates with specific urls
    """
    traffic_data = traffic_data_for_flask(reporting_month, months_back, view_id)
    leads_data = leads_data_for_flask(reporting_month, months_back, account_id)
    return traffic_data, leads_data

#This function takes screenshots of flask charts and tables and places them into the reports
def screenshots_master(clients, client, url_list, folder_id, drive_service):
    #This function takes screenshots cropped images and returns an image url
    def take_ss(url):
        chromedriver = "/usr/local/bin/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        image_url = 'screenshot.png'
        driver.get(url)
        element = driver.find_element_by_tag_name("body")
        location = element.location
        size = element.size
        png = driver.get_screenshot_as_png()
        driver.quit()
        im = Image.open(BytesIO(png))
        left = location['x']
        top= location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im= im.crop((left, top, right, bottom))
        im.save(image_url)
        return image_url

    # This function posts the image, based on its url, on google drive, and then returns its new file id
    def get_file_id(image_url):
        file_metadata = {'name': image_url,
        'parents': [folder_id]}
        media = MediaFileUpload(image_url, mimetype='image/jpeg', resumable = True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        return file_id

    #This function gets the new file_id and turns it into a useable, global image link
    def get_new_image_url(file_id):
        new_image_url = 'https://drive.google.com/uc?id=' + file_id
        return new_image_url


    #This function removes the saved image
    def delete_png_file(image_url):
        os.remove(image_url)


    #This function removes the google drive file
    def delete_google_drive_file(file_id):
        service = drive_service
        file_metadata = {'trashed':True}
        file = drive_service.files().update(body=file_metadata, fileId = file_id).execute()





    #This function uses all of the functions above to effectively screenshot all of the urls in the
    #url list and place the resulting images into specific shape/texts in the reports
    def master(url_list, port):
        pres_id = clients[client]['presentation_id']
        for url in url_list:
            url = 'http://127.0.0.1:8000/' + url
            image_url = take_ss(url)
            file_id = get_file_id(image_url)
            new_image_url = get_new_image_url(file_id)
            if 'traffic' in url:
                shape_text = '{{traffic}}'
                find_replace_img(pres_id, shape_text, new_image_url)
            else:
                shape_text = '{{leads}}'
                find_replace_img(pres_id, shape_text, new_image_url)
            delete_png_file(image_url)
            delete_google_drive_file(file_id)

    master(url_list, port)





def ahrefs_scrape_master(clients, client, folder_id):
    drive_service = setup_googledrive_api()
    ahrefs_pw = os.environ['AHREFS_PW'] #ahrefs password
    ahrefs_un = os.environ['AHREFS_UN'] #ahrefs username
    domains_image = 'domains_count.png' #file that the domains ahrefs screenshot will be saved in
    keywords_image = 'keyword_count.png' #file that the keywords ahrefs screenshot will be saved in 
    images = [domains_image, keywords_image]
    pres_id = clients[client]['presentation_id']
    referring_domains = '{{domains}}' #string to find and replace with ahrefs data in report
    referring_pages = '{{pages}}' #string to find and replace with ahrefs data in report
    org_keywords = '{{org_keywords}}'#string to find and replace with ahrefs data in report
    traffic_value = '{{traffic_value}}'
    new_keywords = '{{new_keywords}}'
    def take_ahrefs_screenshots():
        domain_name = clients[client]['domain_name'].replace("https://", "").replace("http://", "").replace('www/', 'www.')
        chromedriver = "/usr/local/bin/chromedriver"
        os.environ["webdriver.chrome.driver"] = chromedriver
        driver = webdriver.Chrome(chromedriver)
        driver.implicitly_wait(10) # seconds
        driver.get("https://ahrefs.com/user/login/")
        elem = driver.find_element_by_id("email_input")
        elem.send_keys(ahrefs_un)
        elem = driver.find_element_by_name("password")
        elem.send_keys(ahrefs_pw)
        driver.find_element_by_css_selector('input.btn').click()
        sleep(2)
        driver.implicitly_wait(10) # seconds
        driver.get("https://ahrefs.com/site-explorer/overview/v2/subdomains/fresh?target=" + domain_name)
        sleep(10)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 8);")
        driver.save_screenshot(domains_image)
        #This is a little confusing. I am automatically placing the number of referring domains on
        #the ahrefs page into the report over the string {{domains}}
        r_domains = driver.find_element_by_xpath('//td[@class="text-xs-right highlight-link"][1]').text
        find_replace_str(pres_id, referring_domains, r_domains )
        #I am automatically placing the number of referring pages from the ahrefs page into the
        #report over the string {{pages}}
        r_pages = driver.find_element_by_xpath('//span[@id="ref_pages_val"]/a').text
        find_replace_str(pres_id, referring_pages, r_pages)
        #I am automatically placing the traffic value from the ahrefs page into the report
        #over the string {{traffic_value}}
        t_value = driver.find_element_by_xpath('//h5[@id="numberOfOrganicTrafficCost"]/span').text
        find_replace_str(pres_id, traffic_value, t_value)
        driver.find_element_by_xpath('//li[@name="se-overview-tabs"][2]/a').click()
        sleep(15)
        driver.implicitly_wait(10) # seconds
        if client=="Insure My Drone":
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 6.8);")
        else:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight / 8);")
        driver.save_screenshot(keywords_image)
        #I am automatically placing the number of organic keywords from the ahrefs page into 
        #the report over the string {{org_keywords}}
        o_keywords = driver.find_element_by_xpath('//span[@id="organic_keywords_val"]').text
        find_replace_str(pres_id, org_keywords, o_keywords )
        driver.get('https://ahrefs.com/positions-explorer/new-keywords/v2/subdomains/us/2018-08-08/all/all/1/volume_desc?target=' + domain_name + '%2F')
        try:
            n_keywords = driver.find_element_by_xpath('//div[@name="result_info"]/var').text
            find_replace_str(pres_id, new_keywords, n_keywords)
        except:
            pass
        driver.close()

    #A function to crop the domains image so that it only contains the necessary charts for the reports
    def crop_domains_image(domains_image):
        img = Image.open(domains_image)
        img = img.crop((199,202,935,763))
        img.save(domains_image)
        return domains_image    

        #A function to crop the keywords image so that it only contains the necessary chart for the reports
    def crop_keywords_image(keywords_image):
        img = Image.open(keywords_image)
        img = img.crop((208,408,937,670))
        img.save(keywords_image)
        return keywords_image

        #A function to upload the new image to Google Drive, and then return its file id. This file will later be
        #used to generate a image url.
    def get_file_id(image_url):
        file_metadata = {'name': image_url,
        'parents': [folder_id]}
        media = MediaFileUpload(image_url, mimetype='image/jpeg', resumable = True)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        return file_id

        #A function to get the new images url
    def get_new_image_url(file_id):
        new_image_url = 'https://drive.google.com/uc?id=' + file_id
        return new_image_url

        #a function to delete the image files
    def delete_png_file(image_url):
        os.remove(image_url)


        #A function to delete the google drive file that is created by the get_file_id function
    def delete_google_drive_file(file_id):
        service = drive_service
        file_metadata = {'trashed':True}
        file = drive_service.files().update(body=file_metadata, fileId = file_id).execute()

        #This function takes the ahrefs screenshots and then crops the images. I would recommend running it sparingly
        #as it is frowned upon to crawl ahrefs.
    def take_screenshots_and_crop_images():
        take_ahrefs_screenshots()
        crop_domains_image(domains_image)
        crop_keywords_image(keywords_image)
        images = [domains_image, keywords_image]
        return images
        #The master function where the images  will be inserted into the reports
    def find_and_replace_ahrefs_images_into_reports(images):
        for image in images:
            file_id = get_file_id(image)
            new_image_url = get_new_image_url(file_id)
            if 'domains' in image:
                find_replace_img(pres_id, '{{domains_chart}}', new_image_url)
            else:
                find_replace_img(pres_id, '{{keywords_chart}}', new_image_url)
            delete_png_file(image)
            delete_google_drive_file(file_id)



        #The master function where everything comes together. The screenshots are taken, the images are 
        #cropped, the images are put into google drive, then found and replaced in the reports, then the
        #image files are deleted, and then the google drive files are deleted.
    def master():
        images = take_screenshots_and_crop_images()
        find_and_replace_ahrefs_images_into_reports(images)
    
    master()

def extraneous_find_and_replace_master(clients, client):
    org_website = clients[client]['domain_name'].replace("https://", "").replace("http://", "").replace('www/', 'www.').replace('/', "")
    org_logo = clients[client]['org_logo']
    pres_id = clients[client]['presentation_id']
    org = client

    #Below functions are used to conduct search/replaces on elements in a Google Slides presentation
    #constants
    now = datetime.datetime.now()
    month_current = now
    month_previous = now - relativedelta(months=1)
    month_next = now + relativedelta(months=1)
    mo_3l = month_current.strftime('%B')
    year_4d = month_current.strftime('%Y')
    mo_nxt = month_next.strftime('%B')
    year_nxt_mo= month_next.strftime('%Y')
    mo_last = month_previous.strftime('%B')
    day_last_last_mo = (month_previous + relativedelta(day=31)).strftime('%d')
    year_last_mo = month_previous.strftime('%Y')
    month_before_last = month_previous - relativedelta(months=1)
    mo_before_last = month_before_last.strftime('%B')

    #slide 1 search replace

    find_replace_str(pres_id, '{{mo_3l}}', mo_3l)
    find_replace_str(pres_id, '{{year_4d}}', year_4d)
    find_replace_str(pres_id, '{{org_website}}', org_website)
    find_replace_img(pres_id, '{{org_logo}}', org_logo)

    #slide 2 search replace
    find_replace_str(pres_id, '{{mo_nxt}}', mo_nxt)
    find_replace_str(pres_id, '{{year_nxt_mo}}', year_nxt_mo)

    #slide 3 search replace
    find_replace_str(pres_id, '{{mo_last}}', mo_last)
    find_replace_str(pres_id, '{{day_last_last_mo}}', day_last_last_mo)
    find_replace_str(pres_id, '{{year_last_mo}}', year_last_mo)
    find_replace_str(pres_id, '{{org}}', org)


    #slide 7 search replace
    find_replace_str(pres_id, '{{mo_before_last}}', mo_before_last) 


   

def main(client_id):
    client_id = str(client_id)
    with open( 'report_generator/data/client_information.json', 'r') as f:
        clients = json.load(f)
    drive_service = setup_googledrive_api()
    folder_id = '1hScQyb1uMLQaBmNgyHa1dlFZAO2mKzxC'
    url_list = ['traffic/' + str(client_id), 'leads/' + str(client_id)]
    drive_service = setup_googledrive_api()
    for client in clients:
        if clients[client]["client_id"] == client_id:
            ahrefs_scrape_master(clients, client, folder_id)
            extraneous_find_and_replace_master(clients, client)
            screenshots_master(clients, client, url_list, folder_id, drive_service)

