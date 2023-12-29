from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import csv
from datetime import datetime as dt
from datetime import timedelta
import pytz
import schedule
import time

start_time = dt(2023, 12, 31, 11)
target_time = dt(2024, 1, 1, 0)
expiry_time = dt(2024, 1, 1, 12)
default_message = "Heyyyyyy thereeeee! Oh my gosh, can you believe it? Another whirlwind of a year has zoomed " \
                  "by us like a shooting star in a hyperloop!  And here we are, on the brink of a brand new " \
                  "chapter - 365 blank pages waiting for our adventures, mishaps, and all the craziness we're yet to " \
                  "uncover! \nFirst and foremost, let me shower you with the most electrifying, euphoric, and " \
                  "insanely fantastic New Year's wishes EVER! May this upcoming year be filled to the brim with " \
                  "laughter that makes your tummy ache (in the best possible way), friendships that are stronger " \
                  "than Captain America's shield, and moments that make your heart dance a salsa! \nI hope " \
                  "your New Year’s Eve is an absolute blast! May it be a kaleidoscope of shimmering fireworks, " \
                  "sparklers dancing in the night sky like cosmic ballerinas, and confetti that falls like a gentle " \
                  "snowfall but somehow ends up EVERYWHERE - because, you know, the messier, the merrier! \n" \
                  "Let’s toast to the crazy roller coaster ride of 365 days ahead! May your dreams take flight on " \
                  "the wings of determination, your goals be as solid as Dwayne Johnson's biceps, and your happiness " \
                  "shine brighter than a thousand suns. Remember, you're the artist of your own life, so paint it " \
                  "the most vibrant colors from the palette of possibilities! \nOh, and let's not forget the" \
                  "resolutions! Embrace them like a long-lost friend who shows up at your doorstep with a pizza. " \
                  "Embrace change, growth, and all those promises you make to yourself at midnight (even if they " \
                  "involve eating fewer cookies… but hey, no judgment if the cookie jar magically refills itself, " \
                  "right?) \nAs we bid adieu to the past and embrace the future with open arms, here's to the " \
                  "memories we've shared, the ones we’re about to create, and the incredible journey that lies ahead." \
                  "May your 2024 be a masterpiece painted with love, laughter, and all the good stuff that dreams" \
                  "are made of! Cheers to you, my fabulous friend! \nSending you heaps of virtual hugs, a galaxy" \
                  "full of good vibes, and enough positivity to power a supernova! Happy New Year, friend!\n" \
                  "_This is an automated message. Please do not reply._"

user = ""


def get_gmt_offset(timezone_name: str):  # Convert timezone name to integer offset in hours
    try:
        tz = pytz.timezone(timezone_name)
        utc_offset = tz.utcoffset(dt.now())
        offset_hours = int(utc_offset.total_seconds() / 3600)
        return offset_hours
    except pytz.exceptions.UnknownTimeZoneError:
        return None


def send_whatsapp_message(friend_name: str, message: str, wait):
    if not len(message):
        message = default_message

    # Click on search box (inspect element, copy XPath)
    search_box_path = '//*[@id="side"]/div[1]/div/div[2]/div[2]/div/div[1]'
    search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_box_path)))
    search_box.send_keys(friend_name)
    time.sleep(0.2)

    # Search HTML to open target contact chat
    contact_path = '//span[contains(@title,"' + friend_name + '")]'
    contact = wait.until(EC.presence_of_element_located((By.XPATH, contact_path)))
    contact.click()

    # Click on message box (inspect element, copy XPath)
    message_box_path = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]'
    message_box = wait.until(EC.presence_of_element_located((By.XPATH, message_box_path)))

    # Send message
    message_box.send_keys(message + Keys.ENTER)
    time.sleep(5)  # Time delay

    # Clear search box for next friend
    clear_search_box_path = '//*[@id="side"]/div[1]/div/div[2]/span/button/span'
    clear_search_box = wait.until(EC.presence_of_element_located((By.XPATH, clear_search_box_path)))
    clear_search_box.click()


def launch_whatsapp(active: list):
    service = Service()
    options = webdriver.ChromeOptions()

    # Load Chrome options
    # options.add_argument("user-data-dir=C:\Users\" + user + "\AppData\Local\Google\Chrome\User Data")  # Windows
    # options.add_argument("user-data-dir=/Users/" + user + "/Library/Application Support/Google/Chrome")  # Mac

    # Open Chrome browser and go to Whatsapp Web
    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://web.whatsapp.com")
    wait = WebDriverWait(driver, 100)

    for friend in active:
        send_whatsapp_message(friend[0], friend[1], wait)

    driver.quit()
    time.sleep(3540)  # Sleep for 59 minutes


def check_time(data: list):
    active_list = []
    for x in data:
        # If friend local time is between 0000 and 0100 of 01/01/2024
        if target_time <= dt.now() + timedelta(hours=x[1]) < target_time + timedelta(hours=1):
            active_list.append([x[0], x[2]])

    if len(active_list):
        launch_whatsapp(active_list)


with open('friend_list.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    data = list(reader)

unique_timezones = (x[1] for x in data[1:])  # Filter unique timezones of friends
tz_dict = {x: get_gmt_offset(x) for x in unique_timezones}  # Create dict to convert tz to int
friend_list = [[x[0], tz_dict[x[1]], x[2]] for x in data[1:]]  # Save friend list with

schedule.every().hour.at(":00").do(lambda: check_time(friend_list))  # Runs at every hour at xx:00

while dt.now() < expiry_time:
    schedule.run_pending()
    time.sleep(1)  # Runs every second


# TODO
# Eject from active/friend list after message sent to prevent double sending
# May send to groups?
