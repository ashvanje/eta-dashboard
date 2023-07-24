# routes.py
import datetime
import requests
from flask import Flask, render_template, request, jsonify
from flask import render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from itertools import groupby
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json
import time
import pytz
from icalendar import Calendar
from datetime import date
from settings import todoist_token
from utils import get_eta_data, get_stop_name, format_eta_timestamp, scrape_reddit, get_news, scrape_reddit_askreddit, scrape_lihkg, get_weather_forecast

HOME_API_URLS = [
    # Add your home API URLs here
]

OFFICE_API_URLS = [
    # Add your office API URLs here
]

def dashboard():
    formatted_eta = []
    now = datetime.datetime.now(datetime.timezone.utc)
    weather_forecast = get_weather_forecast()

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
    return render_template("dashboard.html", eta=formatted_eta, last_refreshed_time=last_refreshed_time, weather_forecast=weather_forecast)

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
    return render_template("dashboard.html", eta=formatted_eta, last_refreshed_time=last_refreshed_time)

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

def get_notepad(notepad_id):
    try:
        file_path = f'temp{notepad_id}.txt'
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

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


