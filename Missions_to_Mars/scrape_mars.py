from splinter import Browser
from bs4 import BeautifulSoup as bs
import pandas as pd


def scrape():
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    
    news_title, news_p = mars_news(browser)
    
    scraped_data = {
            'news_title': news_title,
            'news_p': news_p,
            'featured_image': featured_image(browser),
            'facts': mars_facts(),
            'hemispheres': hemispheres(browser)                   
    }
    
    browser.quit()
    return scraped_data

def mars_news(browser):
         
    url ='https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    
    browser.visit(url)

    html = browser.html
    news_soup = bs(html, 'html.parser')

    try:
        title_results = news_soup.find("div", class_='content_title')
        news_title = title_results.text.strip()
        paragraph_results = news_soup.find("div", class_='rollover_description_inner')
        news_p = paragraph_results.text.strip()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    image_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(image_url)
    
    browser.find_by_id('full_image').click()

    browser.links.find_by_partial_text('more info').click()

    html = browser.html
    image_soup = bs(html, 'html.parser')

    try:
        image_results = image_soup.find('figure', class_='lede').\
            find('a').\
            find('img')
        
    except AttributeError:
        return None

    featured_image_url = f"https://www.jpl.nasa.gov/{image_results.get('src')}"

    return featured_image_url

def mars_facts():
    try:
        facts_url = 'https://space-facts.com/mars/'
        facts_df = pd.read_html(facts_url)[0]

    except BaseException:
        return None

    facts_df.columns=['Description','Info']

    return facts_df.to_html(classes="table")


def hemispheres(browser):
    hemispheres_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    
    browser.visit(hemispheres_url)
    
    hemispheres_soup = bs(browser.html, 'html.parser')
    
    hemisphere_image_urls =[]

    for i in range(4):
        hemisphere_data = {}
    
        hemisphere_data['title'] = (hemispheres_soup.find_all('h3')[i].text)
    
        browser.find_by_css('a.product-item h3')[i].click()
    
        hemisphere_data['img_url'] = browser.find_by_text('Sample')['href']
    
        hemisphere_image_urls.append(hemisphere_data)

        browser.back()

    return hemisphere_image_urls


if __name__ == "__main__":

    print(scrape())