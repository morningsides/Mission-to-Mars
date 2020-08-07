# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt

# Set the executable path and initialize the chrome browser in splinter
executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
browser = Browser('chrome', **executable_path, headless=True)


def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser("chrome", executable_path="chromedriver", headless=True)
    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # try catch for error handling
    try:

        slide_elem = news_soup.select_one('ul.item_list li.slide')
        slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first <a> tag and save it as  `news_title`
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find(
            'div', class_="article_teaser_body").get_text()
    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # ## JPL Space Images Featured Image
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")
    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'
    return img_url


def mars_facts():

    try:
        # use 'read_html" to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns = ['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()


def mars_hemispheres(browser):

    # List to hold our urls
    urlList = []
    urlDictArray = []

    # Base URL
    baseUrl = 'https://astrogeology.usgs.gov'

    # Visit URL
    url = f'{baseUrl}/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("div.full-content", wait_time=1)

    # create an html object to parse
    html = browser.html
    parseHtml = soup(html, 'html.parser')

    # Grab the produt-item divs
    try:
        item_divs = parseHtml.findAll('a', class_='itemLink product-item')
        for item in item_divs:
            if (baseUrl + item['href']) not in urlList:
                urlList.append(baseUrl + item['href'])
    except AttributeError:
        return None

    # Go to child pages to get image url and title
    for url in urlList:
        urlDict = {}
        browser.visit(url)
        html = browser.html
        parseHtml = soup(html, 'html.parser')
        try:
            urlDict['img_url'] = parseHtml.findAll(
                'a', string='Original')[0]['href']
            urlDict['title'] = parseHtml.find('h2', class_='title').text
            urlDictArray.append(urlDict)
        except AttributeError:
            return None
    return urlDictArray


if __name__ == "__main__":
    # If running as script, print scraped data
    print(scrape_all())
