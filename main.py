from flask import Flask, render_template
import datetime
import requests
import time
import os


app = Flask(__name__)

API_URLS = [
    "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001081/18x",
    # "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/1",
    # "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/10",
    # "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/5B",
    # "https://rt.data.gov.hk/v2/transport/citybus/eta/CTB/001080/5X",
    # Add more API URLs as needed
]

def get_eta_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()["data"]
    else:
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
    dt = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
    return dt.strftime("%H:%M:%S")

@app.route("/")
def dashboard():
    formatted_eta = []
    now = datetime.datetime.now(datetime.timezone.utc)

    last_refreshed_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for api_url in API_URLS:
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

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)