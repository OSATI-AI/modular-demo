from django.shortcuts import render
from django.http import JsonResponse
import yaml
import os
import json
from .conversation_manager import conversation_manager
from django.views.decorators.csrf import csrf_exempt
from jinja2 import Template

tasks_dir = os.path.join(os.path.dirname(__file__), 'data/tasks')
template_dir = os.path.join(os.path.dirname(__file__), 'data/templates')

def load_tasks(tasks_dir, language):
    tasks = []
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.yaml'):
            with open(os.path.join(tasks_dir, task_file), 'r', encoding='utf-8') as file:
                task = yaml.safe_load(file)
                tasks.append((task['title'][language], task_file, task['topic_id']))
    return tasks

def structure_tasks(tasks, topics_lookup, language):
    structured_tasks = {}

    for title, filename, topic_id in tasks:
        topic = topics_lookup['topics'][topic_id]
        key_idea_id = topic['key_idea']
        level_id = topic['level']

        level_name = topics_lookup['levels'][level_id][language]
        key_idea_name = topics_lookup['key_ideas'][key_idea_id][language]
        topic_name = topic['title'][language]

        if level_name not in structured_tasks:
            structured_tasks[level_name] = {}

        if key_idea_name not in structured_tasks[level_name]:
            structured_tasks[level_name][key_idea_name] = {}
        
        if topic_name not in structured_tasks[level_name][key_idea_name]:
            structured_tasks[level_name][key_idea_name][topic_name] = []
        
        structured_tasks[level_name][key_idea_name][topic_name].append((title, filename))
    
    return structured_tasks

def index(request):
    language = request.GET.get('lang', 'english')

    tasks_dir = os.path.join(os.path.dirname(__file__), 'data/tasks')
    tasks = load_tasks(tasks_dir, language)

    with open(os.path.join(os.path.dirname(__file__), 'data/topics_lookup.yaml'), 'r', encoding='utf-8') as file:
        topics_lookup = yaml.safe_load(file)

    structured_tasks = structure_tasks(tasks, topics_lookup, language)

    return render(request, 'index.html', {'structured_tasks': structured_tasks, 'language': language})

def fill_text(yaml_file, language):
    # Convert YAML data to a string
    template_str = yaml.dump(yaml_file)

    # Create a Jinja2 template
    template = Template(template_str)

    # Prepare the context with the selected language
    text_data = yaml_file["text"]
    context = {key: value[language] for key, value in text_data.items()}

    # Render the template with the context
    rendered_str = template.render(text=context)

    # Convert the rendered string back to a dictionary
    return yaml.safe_load(rendered_str)

def load_task(request):
    task_id = request.GET.get('task_id')
    language = request.GET.get('lang', 'english')

    print("LANGUAGE: ", language)

    if task_id:
        task_file = os.path.join(tasks_dir, f'{task_id}')
        with open(task_file, 'r', encoding="utf-8") as file:
            task_yaml = yaml.safe_load(file)
        task_yaml = fill_text(task_yaml, language)

        template_file = os.path.join(template_dir, f'{task_yaml["template_id"]}.yaml')
        with open(template_file, 'r') as file:
            template_yaml = yaml.safe_load(file)

        return JsonResponse({'task': yaml.dump(task_yaml), 'template': yaml.dump(template_yaml)})

    return JsonResponse({'error': 'Task ID not provided'}, status=400)

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        chat_history = data.get('chatHistory', '')
        task_context = data.get('taskContext', '')
        user_message = data.get('message', '')
        action_log = data.get('actionLog', '[No user interactions so far]')
        language = data.get('language', 'english')

        # Simulate a response from the tutor
        tutor_response = conversation_manager.get_response(user_message, chat_history, task_context, action_log, language)

        return JsonResponse({'response': tutor_response})

    return JsonResponse({'error': 'Invalid request'}, status=400)
