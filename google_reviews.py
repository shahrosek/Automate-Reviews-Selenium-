from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pyautogui
import time
import pandas as pd
import csv


class ReviewAutomate:
    def __init__(self, hotel_count, hotels):
        chrome_options = Options()
        chrome_options.add_argument("start-maximized");

        self.hotel_count = hotel_count
        self.hotels = hotels
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)

        #self.driver = webdriver.Chrome(options=chrome_options, service=Service('/home/shahrose/chromedriver_linux64/chromedriver'))


    def get_link(self):

        self.driver.get("http://www.google.com/")
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)

        search_bar = self.driver.find_element(By.XPATH, '//*/form/div[1]/div[1]/div[1]/div/div[2]/input')
        search_bar.send_keys(self.hotels[self.hotel_count-1])
        search_bar.send_keys(Keys.RETURN)

        time.sleep(3)

        self.hotel_name = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'qrShPb')))
        self.hotel_name = self.driver.find_element(By.CLASS_NAME, 'qrShPb').text

        review_link_element = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'Ob2kfd')))

        review_link = self.driver.find_element(By.CLASS_NAME, 'Ob2kfd')

        review_link_html = review_link.get_attribute('innerHTML')

        soup = BeautifulSoup(review_link_html, 'lxml')

        review_link = soup.find('a', {'class': 'hqzQac'})

        self.review_count = review_link.text.split(' ')[0]
        self.review_count = int(self.review_count.replace(',', ''))

        self.link = review_link['href']
        self.link = 'https://www.google.com' + self.link

    def get_reviews(self):

        self.names = []
        self.reviews_list = []
        self.ratings = []

        self.driver.get(self.link)

        df = pd.DataFrame(columns = ['Name', 'Review', 'Rating'])

        speed = -15
        sleep_time = 0.25

        pyautogui.time.sleep(1)

        flag = True

        while flag:

            element = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="reviews"]/c-wiz/c-wiz/div/div')))

            reviews = self.driver.find_element(By.XPATH, '//*[@id="reviews"]/c-wiz/c-wiz/div/div')
            reviews = reviews.get_attribute('innerHTML')

            soup2 = BeautifulSoup(reviews, 'lxml')

            spans = soup2.findAll('span', {'class': 'k5TI0'})

            for span in spans:

                link = span.find('a')

                if link.text not in self.names:
                    self.names.append(link.text)

            if len(self.names) == 20 or len(self.names) == self.review_count:
                flag = False

            pyautogui.scroll(int(speed))
            pyautogui.time.sleep(int(sleep_time))

        divs = soup2.findAll('div', {'class': 'GDWaad'})

        for div in divs:

            self.ratings.append(div.text)

        divs = soup2.findAll('div', {'class': 'K7oBsc'})

        for div in divs:

            span = div.find('span')

            if span:
                review = span.text
            else:
                review = 'NA'

            self.substr = review
            index = self.get_index_substring()

            if index == -1:
                self.reviews_list.append(review)
            else:
                self.reviews_list[index] = review

        df['Name'] = self.names
        df['Review'] = self.reviews_list
        df['Rating'] = self.ratings

        self.hotel_name = self.hotel_name + '.csv'
        df.to_csv(self.hotel_name, index=False)

        self.hotel_count -= 1

        if self.hotel_count == 0:
            self.driver.quit()

    def get_index_substring(self):
        if self.substr == 'NA':
            return -1
        for i in range(len(self.reviews_list)):
            if self.reviews_list[i][:-3] in self.substr:
                return i
        return -1


if __name__ == "__main__":

    hotel_list = ['PC Hotel Lahore', 'Park View Hotel Gulberg', 'New Taj Palace Hotel', 'Park Lane Hotel', 'Hotel Tulip Inn Gulberg']
    hotel_count = len(hotel_list)

    obj = ReviewAutomate(hotel_count=hotel_count, hotels=hotel_list)

    while hotel_count > 0:

        obj.get_link()
        obj.get_reviews()

        hotel_count -= 1
