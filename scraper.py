from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import pandas as pd
import re
import time

# REQUEST_URL = "https://cityoflapcp.ezlinksgolf.com/app/search/searchResult.html"
BASE_URL = "https://cityoflapcp.ezlinksgolf.com/index.html#/preSearch"

browser = webdriver.Chrome()

def loadLandingPage():
    browser.get(BASE_URL)
    browser.maximize_window()

    time.sleep(2)

    landingPageHtml = browser.page_source
    assert 'City of LA' in browser.title 


def fillSearchForm():

    # Select 2 people
    peopleDropdown = browser.find_element(By.ID, "pc")
    peopleDropdown.click()
    twoOption = browser.find_element(By.XPATH, "//option[@label='2']")
    twoOption.click()

    # Select date
    dateInput = browser.find_element(By.XPATH, "//input[@placeholder='Click here for date']")
    dateInput.clear()
    dateInput.send_keys('05/27/2023')
    time.sleep(1)
    # datePicker = browser.find_element(By.CLASS, "ui-datepicker-calendar")


    # Select course(s)
    courseLabel = browser.find_element(By.XPATH, "//label[@title='Select a course' and contains(., 'Rancho Park')]")
    courseLabel.click()


    # dateInput.send_keys('Keys.ESCAPE')

    

    # Click Search button
    searchBtn = browser.find_element(By.XPATH, "//button[@type='submit' and contains(., 'Search')]")
    browser.execute_script("arguments[0].scrollIntoView(true);", searchBtn);

    time.sleep(2)

    searchBtn.click()

    time.sleep(15)



if __name__ == '__main__':
    loadLandingPage()
    fillSearchForm()

    # searchPageHtml = browser.page_source
    # with open('test/search_page.html', 'w') as f:
    #     f.write(searchPageHtml)

    browser.close()







# time.sleep(2)

# with open('test/landing_page.html', 'w') as f:
#     f.write(landingPageHtml) 


# browser.close() 

#####################################################
 
# html_string = """
#     <html>
#     <head><title>Latest PPRA Tenders</title></head>
#     <body>
#         <style>
#         table {
#             border-collapse: collapse;
#             border: 1px solid silver;
#         }
#         table tr:nth-child(even) {
#             background: #E0E0E0;
#         }
#         </style>
#         %s
#     </body>
#     </html>
# """

# def download_parse_table(url):
#     html = r.get(url)
#     details = re.findall('<td bgcolor="(?:.+?)" width="305">(.+?)</td>', html.text, re.DOTALL)
#     details = [detail.replace('\r\n','') for detail in details]
#     dfs = pd.read_html(html.text, attrs={'width': '656'}, header=0, parse_dates=['Advertised Date'])
#     download_links = re.findall('<a target="_blank" href="(.+?)"><img border="0" src="images/(?:.+?)"></a>',html.text)
#     download_links = ["<a href='https://ppra.org.pk/"+link+"' style='display: block;text-align: center;'> <img src='https://ppra.org.pk/images/download_icon.gif'/></a>" for link in download_links]
#     tender_table = dfs[0]
#     tender_table['Download'] = download_links
#     tender_table["Tender  Details"] = details
#     return tender_table

# combined_df = []
# for index in range(1,8):
#     df = download_parse_table(url_template+str(index))
#     combined_df.append(df)

# combined_df = pd.concat(combined_df).reset_index(drop=True)
# latest_date = combined_df.iloc[0]['Advertised Date']
# filtered_df = combined_df[combined_df['Advertised Date'] == latest_date]

# table_html = filtered_df.to_html(index=False,render_links=True, justify="center", escape=False, border=4)
# with open('ppra.html', 'w') as f:
#     f.write(html_string %(table_html))


####################################################################