from flask import Flask, render_template
import datetime
import requests
import time
import os

import os
import requests
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, render_template
from itertools import groupby
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import openai
from dotenv import load_dotenv
load_dotenv()
from icalendar import Calendar
from datetime import date
import pytz

from flask import Flask, request, jsonify

openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)


todoist_token = os.getenv("TODOIST_TOKEN")

app = Flask(__name__)

HOME_API_URLS = [
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001081/18x",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001003/A10",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/1",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/10",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/5B",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/5X",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001081/904",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001081/971",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/002764/18",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001081/18P"
    # Add more API URLs as needed
]


OFFICE_API_URLS = [
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001273/18X",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001076/5X",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001033/18",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001033/18X",
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001033/18P",
    # Add more API URLs as needed
]

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



@app.route("/")
def dashboard():
    try:
        formatted_eta = []
        now = datetime.datetime.now(datetime.timezone.utc)
        weather_forecast_arr = get_weather_forecast()
        if(get_weather_forecast):
            weather_forecast = weather_forecast_arr[:3]
        current_weather = get_current_weather()

        last_refreshed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for api_url in HOME_API_URLS:
            eta_data = get_eta_data(api_url)
            if eta_data:
                route = eta_data[0]["route"]
                stop_id = eta_data[0]["stop"]
                stop_name_tc, stop_name_en = get_stop_name(stop_id)
                print(f"ETA print: {eta_data[0]}")
                etas = [format_eta_timestamp(item["eta"]) for item in eta_data]
                print(f"ETA print: finish ^^^^^")
                formatted_eta.append({
                    "route": route,
                    "stop_name_tc": stop_name_tc,
                    "stop_name_en": stop_name_en,
                    "etas": etas
                })
        return render_template("eta-dashboard.html", eta=formatted_eta, last_refreshed_time=last_refreshed_time, weather_forecast=weather_forecast, current_weather = current_weather)
    except:
        return render_template("eta-dashboard.html", eta=[], last_refreshed_time='', weather_forecast=[], current_weather = {})


@app.route("/office")
def dashboard2():
    formatted_eta = []
    now = datetime.datetime.now(datetime.timezone.utc)

    last_refreshed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for api_url in OFFICE_API_URLS:
        eta_data = get_eta_data(api_url)
        if eta_data:
            route = eta_data[0]["route"]
            stop_id = eta_data[0]["stop"]
            stop_name_tc, stop_name_en = get_stop_name(stop_id)
            etas = [format_eta_timestamp(item["eta"]) for item in eta_data]
            formatted_eta.append({
                "route": route,
                "stop_name_tc": stop_name_tc,
                "stop_name_en": stop_name_en,
                "etas": etas
            })
    return render_template("eta-dashboard.html", eta=formatted_eta, last_refreshed_time=last_refreshed_time)


def get_current_weather():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=tc"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data
        return []
        # Process the response data here
        # ...

        return response.json()  # Or whatever response data you need to return
    except requests.exceptions.ReadTimeout as e:
        # Handle the ReadTimeout error
        print("The request to the weather API timed out. Please try again later.")
        return None  # Or any other appropriate action you want to take
    except requests.exceptions.RequestException as e:
        # Handle any other request-related errors
        print(f"An error occurred during the request: {e}")
        return None  # Or any other appropriate action you want to take
    
def get_weather_forecast():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get("weatherForecast", [])
        return []
        # Process the response data here
        # ...

        return response.json()  # Or whatever response data you need to return
    except requests.exceptions.ReadTimeout as e:
        # Handle the ReadTimeout error
        print("The request to the weather API timed out. Please try again later.")
        return None  # Or any other appropriate action you want to take
    except requests.exceptions.RequestException as e:
        # Handle any other request-related errors
        print(f"An error occurred during the request: {e}")
        return None  # Or any other appropriate action you want to take



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


@app.route('/news')
def hacker_news():
    top_stories_url = 'https://hacker-news.firebaseio.com/v0/topstories.json?print=pretty'
    item_url = 'https://hacker-news.firebaseio.com/v0/item/{}.json?print=pretty'
    tasks_url = 'https://api.todoist.com/rest/v2/tasks'
    projects_url = 'https://api.todoist.com/rest/v2/projects'

    # Fetch the top story IDs
    response = requests.get(top_stories_url)
    top_stories = response.json()

    posts = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create a list of executor.submit() tasks for concurrent API calls
        api_calls = [executor.submit(requests.get, item_url.format(post_id)) for post_id in top_stories[:10]]

        # Process the completed tasks and retrieve the results
        for task in api_calls:
            response = task.result()
            post = response.json()

            title = post.get('title')
            url = post.get('url')
            score = post.get('score')

            # Fetch the first comment, if available
            comment = ''
            # if 'kids' in post and post['kids']:
            #     comment_id = post['kids'][0]
            #     comment_response = requests.get(item_url.format(comment_id))
            #     comment_data = comment_response.json()
            #     comment = comment_data.get('text', '')

            posts.append({'title': title, 'url': url, 'comment': comment, 'score': score})

    # Fetch tasks from Todoist API
    headers = {
        'Authorization': f'Bearer {todoist_token}'
    }
    response = requests.get(tasks_url, headers=headers)
    tasks = response.json()

    # Fetch project names from Todoist API
    response = requests.get(projects_url, headers=headers)
    projects = response.json()

    # Group tasks by project name
    tasks = sorted(tasks, key=lambda task: task['project_id'])
    grouped_tasks = groupby(tasks, key=lambda task: task['project_id'])

    # Create a dictionary of project names
    project_names = {project['id']: project['name'] for project in projects}

    # Map the project names to the tasks
    tasks_by_project = {}
    for project_id, project_tasks in grouped_tasks:
        project_name = project_names.get(project_id, 'Unknown Project')
        tasks_by_project[project_name] = list(project_tasks)

    # TODO: CALL OPENAI

    conversation2 = []

    # Scrape Reddit and LIHKG
    reddit_posts = scrape_reddit()
    reddit_posts_askreddit = scrape_reddit_askreddit()
    lihkg_post_titles = []
    lihkg_post_titles = scrape_lihkg()
    weather_forecast = get_weather_forecast()
    # prompt3 = f"""
    # based on the title, categorize the LIHKG hot posts for me, and give me a few paragraph what's so interesting today (in chinese)
    # {lihkg_post_titles}
    # """
    # conversation2.append({"role": "user", "content": prompt3})

    # response2 = openai.ChatCompletion.create(
    #     model='gpt-3.5-turbo',
    #     messages=conversation2
    # )

    # ai_response2 = response2.choices[0].message.content

    # print(ai_response2)
    news = get_news()
    return render_template('index.html', posts=posts, tasks_by_project=tasks_by_project, reddit_posts=reddit_posts, lihkg_post_titles=lihkg_post_titles, reddit_posts_askreddit=reddit_posts_askreddit, weather_forecast=weather_forecast, news=news)


def get_weather_forecast():
    url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=tc"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("weatherForecast", [])
    return []

@app.route('/planner')
def planner():
   
    tasks_url = 'https://api.todoist.com/rest/v2/tasks'
    projects_url = 'https://api.todoist.com/rest/v2/projects'

    # Fetch the top story IDs

    posts = []
    # Fetch tasks from Todoist API
    headers = {
        'Authorization': f'Bearer {todoist_token}'
    }
    response = requests.get(tasks_url, headers=headers)
    tasks = response.json()

    # Fetch project names from Todoist API
    response = requests.get(projects_url, headers=headers)
    projects = response.json()

    # Group tasks by project name
    tasks = sorted(tasks, key=lambda task: task['project_id'])
    grouped_tasks = groupby(tasks, key=lambda task: task['project_id'])

    # Create a dictionary of project names
    project_names = {project['id']: project['name'] for project in projects}

    # Map the project names to the tasks
    
    tasks_by_project = {}



    tasks_url = 'https://api.todoist.com/rest/v2/tasks'
    response = requests.get(tasks_url, headers=headers)
    tasks = response.json()
    print("tasks:")
    print(json.dumps(tasks, indent=4))  # Use indent parameter for pretty formatting
    # Filter tasks that are due today
    today = date.today().isoformat()
    tasks_due_today = [task for task in tasks if task.get('due') and task['due'].get('date') == today]
    tasks_due_today = sorted(tasks_due_today, key=lambda x: x["due"]["date"])
    tasks_top3_today = [task for task in tasks if task.get('labels') and "top3" in task.get('labels')]
    tasks_top3_today = sorted(tasks_top3_today, key=lambda x: x["due"]["date"])
    tasks_by_project["TOP3"] = tasks_top3_today
    tasks_by_project["TODAY"] = tasks_due_today

    for project_id, project_tasks in grouped_tasks:
        print(f"project_id: {project_id}")

        project_name = project_names.get(project_id, 'Unknown Project')
        print(f"project_name: {project_name}")
        tasks_by_project[project_name] = list(project_tasks)

    # TODO: CALL OPENAI

    conversation2 = []

    # Scrape Reddit and LIHKG
    reddit_posts = scrape_reddit()
    lihkg_post_titles = []
    # lihkg_post_titles = scrape_lihkg()
    # prompt3 = f"""
    # based on the title, categorize the LIHKG hot posts for me, and give me a few paragraph what's so interesting today (in chinese)
    # {lihkg_post_titles}
    # """
    # conversation2.append({"role": "user", "content": prompt3})

    # response2 = openai.ChatCompletion.create(
    #     model='gpt-3.5-turbo',
    #     messages=conversation2
    # )

    # ai_response2 = response2.choices[0].message.content

    # print(ai_response2)


    # Fetch tasks from Todoist API
    headers = {
        'Authorization': f'Bearer {todoist_token}'
    }
    return render_template('planner2.html', posts=posts, tasks_by_project=tasks_by_project, reddit_posts=reddit_posts, lihkg_post_titles=lihkg_post_titles)


@app.route('/smallplanner')
def smallplanner():
   
    tasks_url = 'https://api.todoist.com/rest/v2/tasks'
    projects_url = 'https://api.todoist.com/rest/v2/projects'

    # Fetch the top story IDs

    posts = []
    # Fetch tasks from Todoist API
    headers = {
        'Authorization': f'Bearer {todoist_token}'
    }
    response = requests.get(tasks_url, headers=headers)
    tasks = response.json()

    # Fetch project names from Todoist API
    response = requests.get(projects_url, headers=headers)
    projects = response.json()

    # Group tasks by project name
    tasks = sorted(tasks, key=lambda task: task['project_id'])
    grouped_tasks = groupby(tasks, key=lambda task: task['project_id'])

    # Create a dictionary of project names
    project_names = {project['id']: project['name'] for project in projects}

    # Map the project names to the tasks
    
    tasks_by_project = {}



    tasks_url = 'https://api.todoist.com/rest/v2/tasks'
    response = requests.get(tasks_url, headers=headers)
    tasks = response.json()

    # Filter tasks that are due today
    today = date.today().isoformat()
    tasks_due_today = [task for task in tasks if task.get('due') and task['due'].get('date') == today]
    tasks_due_today = sorted(tasks_due_today, key=lambda x: x["due"]["datetime"])
    tasks_top3_today = [task for task in tasks if task.get('labels') and "top3" in task.get('labels')]
    tasks_top3_today = sorted(tasks_top3_today, key=lambda x: x["due"]["datetime"])
    tasks_by_project["TOP3"] = tasks_top3_today
    tasks_by_project["TODAY"] = tasks_due_today

    for project_id, project_tasks in grouped_tasks:
        print(f"project_id: {project_id}")

        project_name = project_names.get(project_id, 'Unknown Project')
        print(f"project_name: {project_name}")
        tasks_by_project[project_name] = list(project_tasks)

    # TODO: CALL OPENAI

    conversation2 = []

    # Scrape Reddit and LIHKG
    # reddit_posts = scrape_reddit()
    # lihkg_post_titles = []
    # lihkg_post_titles = scrape_lihkg()
    # prompt3 = f"""
    # based on the title, categorize the LIHKG hot posts for me, and give me a few paragraph what's so interesting today (in chinese)
    # {lihkg_post_titles}
    # """
    # conversation2.append({"role": "user", "content": prompt3})

    # response2 = openai.ChatCompletion.create(
    #     model='gpt-3.5-turbo',
    #     messages=conversation2
    # )

    # ai_response2 = response2.choices[0].message.content

    # print(ai_response2)


    # Fetch tasks from Todoist API
    headers = {
        'Authorization': f'Bearer {todoist_token}'
    }
    return render_template('planner3.html', posts=posts, tasks_by_project=tasks_by_project)




@app.route('/api/agenda', methods=['GET'])
def get_agenda():
    # Fetch the iCal data
    url = 'https://calendar.google.com/calendar/ical/81cs0kbhi51u8rfv3gn65u2ks8%40group.calendar.google.com/private-c97f1dae6921e626221f02a4897d42ee/basic.ics'
    response = requests.get(url)
    data = response.text

    # Parse the iCal data
    calendar = Calendar.from_ical(data)
    print(f"calendar: {calendar}")
    # Get today's date    
    
    # Get today's date and the date 15 days from now
    today = datetime.combine(date.today(), datetime.min.time()).replace(tzinfo=pytz.UTC)
    # future_date = today + timedelta(days=15)

    # Filter events within the 15-day range
    events = []
    for component in calendar.walk():
        if component.name == 'VEVENT':
            start_date = component.get('DTSTART').dt
            summary = component.get('SUMMARY')

            # Convert start_date to string representation
            start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')

            events.append({
                'summary': summary,
                'start_date': start_date_str
            })

    return jsonify(events)
   
# @app.route('/update-due-date', methods=['POST'])
# def update_due_date():
#     task_id = request.json.get('task_id')
#     due_datetime = request.json.get('due_datetime')
#     duration = request.json.get('duration')

#     # Construct the URL for updating the task
#     url = f'https://api.todoist.com/rest/v2/tasks/{task_id}'


#     if (duration):
#         # Prepare the request payload
#          payload = {
#             'due_datetime': due_datetime,
#             'duration': duration,
#             'duration_unit': 'minute'
#         }
#     else:
#         # Prepare the request payload
#         payload = {
#             'due_datetime': due_datetime
#         }

#     # Set the necessary headers
#     headers = {
#         'Content-Type': 'application/json',
#         'Authorization': f'Bearer {todoist_token}'
#     }

#     # Send the POST request to update the task
#     response = requests.post(url, json=payload, headers=headers)

#     if response.status_code == 200:
#         print('success')
#         updated_task = response.json()
#         return jsonify({'status': 'success', 'task': updated_task})
#     else:
#         print('error')
#         return jsonify({'status': 'error'})
    
@app.route('/update-due-date', methods=['POST'])
def update_due_date():
    task_id = request.json.get('task_id')
    due_datetime = request.json.get('due_datetime')
    duration = request.json.get('duration')
    labels = request.json.get('labels')
    content = request.json.get('content')

    # Construct the URL for updating the task
    url = f'https://api.todoist.com/rest/v2/tasks/{task_id}'

    payload = {}
    # if duration:
    #     # Prepare the request payload
    #     payload = {
    #         'due_datetime': due_datetime,
    #         'duration': duration,
    #         'duration_unit': 'minute',
    #         'labels': labels
    #     }
    # else:
    #     # Prepare the request payload
    #     payload = {
    #         'due_datetime': due_datetime,
    #         'labels': labels
    #     }
    
    if duration:
        payload['duration'] = duration
        payload['duration_unit'] = 'minute'
    
    if labels:
        payload['labels'] = labels

    if due_datetime:
        payload['due_datetime'] = due_datetime

    
    if content:
        payload['content'] = content

    print(payload)
    # Set the necessary headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {todoist_token}'
    }

    # Send the POST request to update the task
    response = requests.post(url, json=payload, headers=headers)

    # print(response.json())
    if response.status_code == 200:
        print("Success")
        updated_task = response.json()
        return jsonify({'status': 'success', 'task': updated_task})
    else:
        print("Fail")
        print("Error:", response.text)  # Print the error message
        return jsonify({'status': 'error'})

@app.route('/createTask', methods=['POST'])
def create_task():
    content = request.json.get('content')
    due_datetime = request.json.get('due_datetime')

    # Construct the URL for updating the task
    url = f'https://api.todoist.com/rest/v2/tasks'

    payload = {}
    # if duration:
    #     # Prepare the request payload
    #     payload = {
    #         'due_datetime': due_datetime,
    #         'duration': duration,
    #         'duration_unit': 'minute',
    #         'labels': labels
    #     }
    # else:
    #     # Prepare the request payload
    #     payload = {
    #         'due_datetime': due_datetime,
    #         'labels': labels
    #     }
    
    if content:
        payload['content'] = content
        payload['project_id'] = '2235380405'

    if due_datetime:
        payload['due_datetime'] = due_datetime

    print(payload)
    # Set the necessary headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {todoist_token}'
    }

    # Send the POST request to update the task
    response = requests.post(url, json=payload, headers=headers)

    # print(response.json())
    if response.status_code == 200:
        print("Success")
        updated_task = response.json()
        return jsonify({'status': 'success', 'task': updated_task})
    else:
        print("Fail")
        print("Error:", response.text)  # Print the error message
        return jsonify({'status': 'error'})



@app.route('/saveNotepad', methods=['POST'])
def save_notepad():
    content = request.json.get('content')
    noteId = request.json.get('noteId')
    print(f'temp{noteId}.txt')
    try:
        with open(f'temp{noteId}.txt', 'w') as file:
            file.write(content)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/getNotepad/<int:notepad_id>')
def get_notepad(notepad_id):
    try:
        file_path = f'temp{notepad_id}.txt'
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/closeTask', methods=['POST'])
def close_task():
    print(f'request.json {request.json}')

    taskId = request.json.get('task_id')
    print(f'closing task {taskId}')

    # Construct the URL for updating the task
    url = f'https://api.todoist.com/rest/v2/tasks/{taskId}/close'

    # Set the necessary headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {todoist_token}'
    }

    # Send the POST request to update the task
    response = requests.post(url, headers=headers)

    # print(response.json())
    if response.status_code == 204:
        print("Success!!")
        # updated_task = response.json()
        return jsonify({'status': 'success'})
    else:
        print("Fail")
        print("Error:", response.text)  # Print the error message
        return jsonify({'status': 'error'})





if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)

# https://rt.data.gov.hk/v2/transport/citybus/stop/001080
# https://rt.data.gov.hk/v2/transport/citybus/route-stop/CTB/10/outbound
# https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001215/10
