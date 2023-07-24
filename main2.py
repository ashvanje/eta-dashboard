# app.py
from flask import Flask, render_template
from routes import dashboard, dashboard2, get_agenda, update_due_date, create_task, save_notepad, get_notepad, close_task, hacker_news, planner, smallplanner
from settings import todoist_token
import os

app = Flask(__name__)

app.add_url_rule('/', 'dashboard', dashboard)
app.add_url_rule('/office', 'dashboard2', dashboard2)
app.add_url_rule('/api/agenda', 'get_agenda', get_agenda, methods=['GET'])
app.add_url_rule('/update-due-date', 'update_due_date', update_due_date, methods=['POST'])
app.add_url_rule('/createTask', 'create_task', create_task, methods=['POST'])
app.add_url_rule('/saveNotepad', 'save_notepad', save_notepad, methods=['POST'])
app.add_url_rule('/getNotepad/<int:notepad_id>', 'get_notepad', get_notepad)
app.add_url_rule('/closeTask', 'close_task', close_task, methods=['POST'])
app.add_url_rule('/news', 'hacker_news', hacker_news, methods=['GET'])
app.add_url_rule('/planner', 'planner', planner, methods=['GET'])
app.add_url_rule('/smallplanner', 'smallplanner', smallplanner, methods=['GET'])

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
