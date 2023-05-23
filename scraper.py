from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# import calendar
import datetime
# import pandas as pd
import re
import time


BASE_URL = "https://www.golfnow.com"
URL_PREFIX = "https://www.golfnow.com/tee-times/facility/"
URL_SUFFIX = "/search#sortby=Date&view=Grouping&holes=3&timeperiod=3&timemax=30&timemin=10&players=0&pricemax=10000&pricemin=0&promotedcampaignsonly=false"
URL_TEMPLATE = URL_PREFIX + "{course_id}-{course_tag}" + URL_SUFFIX

PLAYER_COUNT = 2

COURSES = [
    {
        'id': '12203',
        'tag': 'rancho-park-golf-course',
        'name': 'Rancho Park Golf Course'
    },
]

browser = webdriver.Chrome()

def loadLandingPage(course_id, course_tag):
    browser.get(URL_TEMPLATE.format(course_id=course_id, course_tag=course_tag))
    browser.maximize_window()

    time.sleep(2)


# TODO(vifong)
def computeTargetDates():
    return [datetime.date(2023, 5, 27)]


# TODO(vifong)
def filterTime():
    pass


def filterPlayerCount():
    golfers_btn = browser.find_element(By.XPATH, "//a[@title='Golfers']")
    golfers_btn.click()
    time.sleep(1)

    two_golfers_radio_input = browser.find_element(By.XPATH, "//input[@type='radio' and @value='{players}']".format(players=PLAYER_COUNT))
    parent_element = two_golfers_radio_input.find_element(By.XPATH, "..")
    parent_element.click()
    time.sleep(1)


def filterDate(target_date):
    date_btn = browser.find_element(By.ID, "fed-search-big-date")
    date_btn.click()
    time.sleep(1)

    picker_month = browser.find_element(By.CLASS_NAME, "picker__month")
    picker_year = browser.find_element(By.CLASS_NAME, "picker__year")
    picker_nav_next = browser.find_element(By.CLASS_NAME, "picker__nav--next")

    # Check the month
    month = '{0:%b}'.format(target_date)
    print("target_month:", month)
    print("picker_month:", picker_month.text)
    while picker_month.text != month:
        print("\ttarget_month: ", month)
        print("\tpicker_month: ", picker_month.text)
        picker_nav_next.click()

    # Check the year
    print("target_year:", target_date.year)
    print("picker_year:", picker_year.text)
    if picker_year.text != str(target_date.year):
        print("TODO: error")

    # Select the day
    picker_day = browser.find_element(By.XPATH, "//div[@aria-label='{date}']".format(date=target_date.strftime("%a, %b %d")))
    print("target_day:", target_date.day)
    print("picker_day:", picker_day.text)
    picker_day.click()
    time.sleep(1)


def filterCourse(target_course):
    search_bar = browser.find_element(By.ID, "fed-search-big")
    search_bar.clear()
    search_bar.send_keys(target_course)
    search_btn = browser.find_element(By.ID, "btn-search-tee-time")
    search_btn.click()
    time.sleep(1)

    # WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "search-header-date")))
    # print("Search results rendered.")   


def selectListView():
    list_view_btn = browser.find_element(By.XPATH, "//a[@title='List view']")
    list_view_btn.click()


# TODO(vifong)
def validateResults(target_course, target_date):
    course_result = browser.find_element(By.ID, "fedresults").text
    date_result = browser.find_element(By.ID, "search-header-date").text
    styled_date = target_date.strftime("%a, %b %d")
    print("Validating results...")
    print("\ttarget_course:", target_course)
    print("\tcourse_result:", course_result)
    print("\tdate_result:", date_result)
    print("\ttarget_date:", styled_date)

    assert target_course == course_result and styled_date == date_result


# TODO(vifong)
def hasDiffs():
    return True


def snapshotResults(course_tag, target_date, results):
    file_name = 'snapshots/{course_tag}_{date}.html'.format(course_tag=course_tag, date=target_date.strftime("%Y%m%d"))
    with open(file_name, 'w') as f:
        f.write("Timestamp: {date} \n".format(date=str(datetime.datetime.now())))
        f.write(results)
        print("Snapshot written to ", file_name)


def parseResults(html_text):
    results = re.findall('<time class=" time-meridian">(.+?)</time>', html_text, re.DOTALL)
    print(results)
    if not results:
        return []

    # Clean time results
    cleaned_times = []
    for result in results:
        cleaned_str = result.strip()
        cleaned_str = re.sub('<script (.+?)</script>', '', cleaned_str)
        cleaned_str = re.sub('<sub>', '', cleaned_str)
        cleaned_str = re.sub('</sub>', '', cleaned_str)
        print(cleaned_str)
        cleaned_times.append(cleaned_str)

    return cleaned_times



def scrape(date):
    filterDate(date)
    filterCourse(target_course=COURSES[0]["name"])
    # validateResults(target_course=COURSES[0]["name"], target_date=date)
    filterPlayerCount()
    selectListView()
        
    # if hasDiffs():
    results = parseResults(browser.page_source)
    snapshotResults(course_tag=COURSES[0]["tag"], target_date=date, results=str(results))

    
    print(results)
    return results


def writeMessage(course, target_date, results):
    message = "\nTee Time Alert!\n{course_name} - {date}\n{results}\n{link}".format(
        course_name=course['name'], date=target_date, results=results, link="https://cityoflapcp.ezlinksgolf.com/")
    print(message)

    file_name = "message.txt"
    with open(file_name, 'w') as f:
        f.write(message)
        print("Message written to ", file_name)





if __name__ == '__main__':
    loadLandingPage(course_id=COURSES[0]["id"], course_tag=COURSES[0]["tag"])
    target_dates = computeTargetDates()
    for date in target_dates:
        results = scrape(date)
        writeMessage(COURSES[0], date.strftime("%a, %b %d"), results)

    time.sleep(600)
    browser.close()




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