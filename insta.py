from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import json

def read_visited_json():
  try:
    with open('visited.json') as json_file:
      return json.load(json_file)
  except FileNotFoundError as e:
    return {}
  except json.decoder.JSONDecodeError as e:
    return {}

def write_visited_json(content):
  with open('visited.json', 'w') as outfile:
    json.dump(content, outfile)

def switch_window(bot):
  for window_handle in bot.driver.window_handles:
    if window_handle != bot.main_window:
      bot.driver.switch_to.window(window_handle)
      return
  bot.driver.switch_to.window(bot.main_window)

class Bot:
  def __init__(self, username, password, target):
    visited = read_visited_json()
    self.driver = webdriver.Chrome()
    self.driver.maximize_window()
    self.wait = Wait(self.driver, 30)
    self.main_window = self.driver.current_window_handle

    self.driver.get("https://instagram.com")
    self.wait.until(lambda d: d.find_element_by_xpath("//input[@name=\"username\"]"))
    
    self.driver.find_element_by_xpath("//input[@name=\"username\"]").send_keys(username)
    self.driver.find_element_by_xpath("//input[@name=\"password\"]").send_keys(password)
    self.driver.find_element_by_xpath("//button[@type=\"submit\"]").click()
    
    not_now = self.wait.until(lambda d: d.find_element_by_xpath("//button[text()='Save Info']"))
    not_now.click()

    self.wait.until(lambda d: d.find_element_by_xpath("//a[text()='" + username + "']"))
    
    self.driver.get("https://instagram.com/" + target)
    self.driver.find_element_by_xpath("/html/body/div/section/main/div/header/section/ul/li[2]/a").click()
    
    followers_div = self.wait.until(lambda d: d.find_element_by_xpath('/html/body/div[5]/div/div/div[2]'))
    
    self.driver.execute_script("arguments[0].scrollTop += 300", followers_div)
    sleep(0.5)
    self.driver.execute_script("arguments[0].scrollTop = 0", followers_div)
    index = 1

    while (self.driver.execute_script("return arguments[0].scrollTop < arguments[0].scrollHeight", followers_div)):
      self.driver.execute_script("arguments[0].scrollTop += 54", followers_div)
      followerDiv = self.driver.find_element_by_xpath('/html/body/div[5]/div/div/div[2]/ul/div/li[' + str(index) + ']/div/div[1]/div[2]/div[1]')
      followerUsername = followerDiv.text
      if (visited.get(followerUsername)):
        sleep(0.25)
      else:
        self.driver.execute_script("window.open('http://instagram.com/' + arguments[0].textContent, '_blank');", followerDiv)
        switch_window(self)

        self.wait.until(lambda d: d.find_element_by_xpath("//h2[text()='" + followerUsername + "']"))
        
        try:
          self.driver.find_element_by_xpath("//h2[text()='This Account is Private']")
        except NoSuchElementException:
          picture = self.driver.find_element_by_class_name("_9AhH0")
          picture.click()
          like_button = self.wait.until(lambda d: d.find_element_by_xpath('/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button'))
          like_button.click()

        self.driver.close()
        switch_window(self)

        visited[followerUsername] = True
        write_visited_json(visited)
        sleep(1)

      index += 1
