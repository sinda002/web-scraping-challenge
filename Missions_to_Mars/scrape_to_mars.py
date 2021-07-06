import pymongo
import requests
from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

# DB Setup

client = pymongo.MongoClient('mongodb://localhost:27017')
db = client.mars_db
collection = db.mars 

def init_browser():

#Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape():
    browser = init_browser()
    collection.drop()

# Nasa Mars news
    news_url = 'https://redplanetscience.com/'
    browser.visit(news_url)
    news_html = browser.html
    news_soup = bs(news_html,'lxml')
    news_title = news_soup.find("div",class_="content_title").text
    news_para = news_soup.find("div", class_="rollover_description_inner").text

# JPL Mars Space Images - Featured Image
    jurl = 'https://spaceimages-mars.com'
    browser.visit(jurl)
    jhtml = browser.html
    jpl_soup = bs(jhtml,"html.parser")
    image_url = jpl_soup.find('div',class_='carousel_container').article.footer.a['data-fancybox-href']
    base_link = "https:"+jpl_soup.find('div', class_='jpl_logo').a['href'].rstrip('/')
    feature_url = base_link+image_url
    featured_image_title = jpl_soup.find('h1', class_="media_feature_title").text.strip()

# Mars fact
    murl = 'https://galaxyfacts-mars.com/'
    table = pd.read_html(murl)
    mars_df = table[0]
    mars_df =  mars_df[['Mars - Earth Comparison', 'Mars']]
    mars_fact_html = mars_df.to_html(header=False, index=False)

# Mars Hemispheres
    mhurl = 'https://marshemispheres.com/'
    browser.visit(mhurl)  
    mhtml = browser.html 
    mh_soup = bs(mhtml,"html.parser") 
    results = mh_soup.find_all("div",class_='item')
    hemisphere_image_urls = []
    for result in results:
            product_dict = {}
            titles = result.find('h3').text
            end_link = result.find("a")["href"]
            image_link = "https://marshemispheres.com/" + end_link    
            browser.visit(image_link)
            html = browser.html
            soup= bs(html, "html.parser")
            downloads = soup.find("div", class_="downloads")
            image_url = downloads.find("a")["href"]
            product_dict['title']= titles
            product_dict['image_url']= image_url
            hemisphere_image_urls.append(product_dict)

# Close the browser after scraping
    browser.quit()


# Return results
    mars_data ={
		'news_title' : news_title,
		'summary': news_para,
        'featured_image': feature_url,
		'featured_image_title': featured_image_title,
		'weather': mars_weather,
		'fact_table': mars_fact_html,
		'hemisphere_image_urls': hemisphere_image_urls,
        'news_url': news_url,
        'jpl_url': jurl,
        'weather_url': turl,
        'fact_url': murl,
        'hemisphere_url': mhurl,
        }
    collection.insert(mars_data)