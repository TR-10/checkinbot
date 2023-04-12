from RPA.Browser.Selenium import Selenium
from dotenv import load_dotenv
from pendulum import period
from selenium.webdriver.common.by import By
load_dotenv()
import os
import time as tm
import airportsdata
from pytz import timezone
from datetime import datetime, timedelta
from tzlocal import get_localzone
import json
airports = airportsdata.load('IATA')


jetnet_url = "https://newjetnet.aa.com/"
username = os.environ.get('username')
password = os.environ.get('password')

driver = Selenium()

def open_tp_home(driver: Selenium = driver):
    driver.open_available_browser(url=jetnet_url)
    tm.sleep(10)
    driver.wait_until_page_contains_element("name:userID")
    driver.input_text("name:userID",os.environ.get('username'))
    driver.input_text("name:password",os.environ.get('password'))
    driver.press_key("name:submitButton","\ue007")
    tm.sleep(40)
    driver.click_element_if_visible('xpath:/html/body/div[4]/section/div/div[1]/div[2]/div/div/div/div[2]/div/div[2]/div/div[3]/div/div/div/div[2]/div[1]/a')
    tm.sleep(10)
    driver.switch_window('Travel Planner')



def get_checkin_time(row,driver: Selenium = driver):
    driver.click_link(row.find_element(By.CSS_SELECTOR,'.data.pnr-description'))
    tm.sleep(10)
    flight_date=datetime.strptime(driver.get_webelement('class:date').get_attribute('innerHTML'),'%A, %B %d, %Y')
    flight = driver.get_webelements('class:flight-time')[0]
    airport = flight.find_element(By.CLASS_NAME,('airport-code')).text
    dept_time_str = flight.find_element(By.CLASS_NAME,('hour')).text
    ampm = flight.find_element(By.CLASS_NAME,('period')).text
    dept_time = datetime.strptime(f"{dept_time_str} {ampm}", '%I:%M %p')
    dept_datetime = datetime.combine(flight_date.date(),dept_time.time())
    airporttz = timezone(airports[airport]['tz'])
    dept_datetime = airporttz.localize(dept_datetime)
    checkin_time = dept_datetime - timedelta(hours=24)
    checkin_time = checkin_time.astimezone(get_localzone())
    driver.click_link('id:home')
    tm.sleep(10)
    return (checkin_time)


def get_flights_info(driver: Selenium = driver):
    # try:
        rows = driver.get_webelements('css:.card.desktopView.tripDescFonts')
        flightinfo = []
        with open('data.json', 'r') as myfile:
             prevdata = json.load(myfile)
        for i in range(len(rows)):
            rows = driver.get_webelements('css:.card.desktopView.tripDescFonts')
            tripName = rows[i].find_element(By.CSS_SELECTOR,'.data.pnr-description').text
            recordLocator = rows[i].find_element(By.CSS_SELECTOR,'.data.currtrip-pad-o').text
            check_time = get_checkin_time(rows[i], driver)
            data = {
                'flight_name' : tripName,
                'recordLocator' : recordLocator,
                'checkin_time' : check_time.strftime('%Y-%m-%d %H:%M:%S.%f')
            }
            if not data in prevdata:
                print('appending')
                flightinfo.append(data)
        with open('data.json', 'w+') as myfile:
            json.dump(flightinfo,myfile,indent=2)
            print(tripName, recordLocator, check_time)
        return flightinfo
    # except Exception:
        # print('no flights')

def checkin(flight, driver: Selenium = driver):
    driver.click_link(flight)
    tm.sleep(7)
    driver.click_button('Check in')
    tm.sleep(7)
    driver.click_button('Check in')
    tm.sleep(7)
    driver.click_element('class:icon-email')
    tm.sleep(7)
    driver.click_button('Send')
    tm.sleep(7)
    driver.click_button('OK')
    tm.sleep(7)
    driver.click_link('id:home')

def closeBrowser(driver: Selenium = driver):
     driver.close_browser()

