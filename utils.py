# utils.py
import datetime
import requests
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def get_eta_data(api_url):
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            return []
    except ConnectionError as e:
        print(f"Connection error: {e}")
        return []

def get_stop_name(stop_id):
    stop_url = f"https://rt.data.gov.hk/v2/transport/citybus/stop/{stop_id}"
    response = requests.get(stop_url)
    if response.status_code == 200:
        data = response.json()["data"]
        if data:
            name_tc = data.get("name_tc", "")
            name_en = data.get("name_en", "")
            return name_tc, name_en
    return "", ""

def format_eta_timestamp(timestamp):
    if timestamp:
        try:
            dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
            return dt.strftime("%H:%M:%S")
        except ValueError:
            # Handle invalid timestamp format gracefully
            return "Invalid Timestamp"
    else:
        # Handle empty timestamp gracefully
        return ""
    
def scrape_reddit():
    url = 'https://old.reddit.com/.json'
    response = requests.get(url, headers={'User-agent': 'your bot 0.1'})
    data = response.json()
    reddit_posts = []

    # Check if the response contains the 'data' keyx
    if 'data' in data:
        children = data['data']['children']
        for child in children:
            post_data = child['data']
            title = post_data['title']
            subreddit_name = post_data['subreddit_name_prefixed']
            upvotes = post_data['ups']
            permalink = "https://old.reddit.com" + post_data['permalink']
            reddit_posts.append({'title': title, 'subreddit_name': subreddit_name, 'permalink': permalink, 'upvotes': upvotes})
    print('end')
    return reddit_posts

def get_news():
    # url = "https://newsapi.org/v2/everything?q=tesla&from=2023-06-17&sortBy=publishedAt&apiKey=0a56156f829c4afb9ff706d65e3f97a8"
    # url = "https://newsapi.org/v2/top-headlines?sources=bloomberg&apiKey=0a56156f829c4afb9ff706d65e3f97a8"
    url = "https://newsapi.org/v2/everything?q=apple&sortBy=popularity&apiKey=0a56156f829c4afb9ff706d65e3f97a8"
    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        articles = data["articles"]
        news_data = []  # List to store article data

        for article in articles:
            source = article["source"]["name"]
            author = article["author"]
            title = article["title"]
            description = article["description"]
            url = article["url"]
            published_at = article["publishedAt"]
            content = article["content"]

            article_data = {
                "source": source,
                "author": author,
                "title": title,
                "description": description,
                "url": url,
                "published_at": published_at,
                "content": content
            }

            
            news_data.append(article_data)
        # Convert the list of dictionaries to a JSON array
        # json_array = json.dumps(news_data, indent=4)
        # print(json_array)

    return news_data


def scrape_reddit_askreddit():
    url = 'https://old.reddit.com/r/AskReddit/top.json?sort=top&t=week'
    response = requests.get(url, headers={'User-agent': 'your bot 0.1'})
    data = response.json()
    reddit_posts = []

    # Check if the response contains the 'data' keyx
    if 'data' in data:
        children = data['data']['children']
        for child in children:
            post_data = child['data']
            title = post_data['title']
            subreddit_name = post_data['subreddit_name_prefixed']
            upvotes = post_data['ups']
            permalink = "https://old.reddit.com" + post_data['permalink']
            reddit_posts.append({'title': title, 'subreddit_name': subreddit_name, 'permalink': permalink, 'upvotes': upvotes})
    print('end')
    return reddit_posts

def scrape_lihkg():
    url = 'https://lihkg.com/category/2'
    retry_limit = 5
    retry_count = 0

    # Set up Chrome WebDriver
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    driver = webdriver.Chrome(options=options)

    while retry_count < retry_limit:
        try:
            # Load the page with Selenium
            driver.get(url)

            # Get the page source after JavaScript execution
            html_content = driver.page_source

            # Parse the HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # Close the Selenium WebDriver
            driver.quit()

            # Scrape the post titles
            post_titles = []
            post_elements = soup.select('div[class^="_"] span[class^="_"]')
            link_elements = soup.select('div[class^="_"] a[class^="_2A_7b"]')

            links = []
            if link_elements:
                for link_element in link_elements:
                    print(f"link_element: {link_element}")
                    link = link_element['href']
                    print(f"link: {link}")
                    # print(link)
                    links.append(link)
            else:
                # print(soup.prettify())
                raise ValueError("Failed to find the link_elements on the webpage.")

            data = []
            if post_elements:
                for index, post_element in enumerate(post_elements):
                    post_title = post_element.text

                    # Determine the field based on the index
                    if index % 3 == 0:
                        time = post_title
                    elif index % 3 == 1:
                        upvote = post_title
                    elif index % 3 == 2:
                        title = post_title

                        # Create a dictionary and append to the list
                        entry = {
                            "time": time,
                            "upvote": upvote,
                            "title": title
                        }
                        data.append(entry)

            else:
                # print(soup.prettify())
                raise ValueError("Failed to find the post_elements on the webpage.")
            
            if link_elements:
                for index, link in enumerate(links):
                    # Get the link text

                    # Check if the index is within the range of the data list
                    if index < len(data):
                        # Add the link to the corresponding dictionary entry
                        data[index]["link"] = f"https://lihkg.com{link}"
                    else:
                        # Raise an error if the index is out of range
                        raise IndexError("The number of link elements exceeds the length of post elements.")

            # Convert the dictionary to JSON
            json_data = json.dumps(data, ensure_ascii=False)

            # Print or do further processing with the JSON data
            print(json_data)

            return data

        except ValueError:
            retry_count += 1
            print(f"Retrying ({retry_count}/{retry_limit})...")
            # time.sleep(1)  # Wait for 1 second before retrying

    raise ValueError("Maximum number of retries exceeded. Failed to scrape the webpage.")


def get_weather_forecast():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("weatherForecast", [])
    return []