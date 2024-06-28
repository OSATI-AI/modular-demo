from django.shortcuts import render
from django.http import JsonResponse
import yaml
import os
import json
from .conversation_manager import conversation_manager
from django.views.decorators.csrf import csrf_exempt

tasks_dir = os.path.join(os.path.dirname(__file__), 'data/tasks')
template_dir = os.path.join(os.path.dirname(__file__), 'data/templates')

def load_tasks(tasks_dir):
    tasks = []
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.yaml'):
            with open(os.path.join(tasks_dir, task_file), 'r') as file:
                task = yaml.safe_load(file)
                tasks.append((task['title'], task_file, task['topic_id']))
    return tasks

LANGUAGE = "english"
def structure_tasks(tasks, topics_lookup):
    
    structured_tasks = {}

    for title, filename, topic_id in tasks:
        topic = topics_lookup['topics'][topic_id]
        key_idea_id = topic['key_idea']
        level_id = topic['level']

        level_name = topics_lookup['levels'][level_id][LANGUAGE]
        key_idea_name = topics_lookup['key_ideas'][key_idea_id][LANGUAGE]
        topic_name = topic['title'][LANGUAGE]

        if level_name not in structured_tasks:
            structured_tasks[level_name]={}

        if key_idea_name not in structured_tasks[level_name]:
            structured_tasks[level_name][key_idea_name] = {}
        
        if topic_name not in structured_tasks[level_name][key_idea_name]:
            structured_tasks[level_name][key_idea_name][topic_name] = []
        
        structured_tasks[level_name][key_idea_name][topic_name].append((title, filename))

    return structured_tasks

def index(request):

    tasks_dir = os.path.join(os.path.dirname(__file__), 'data/tasks')
    tasks = load_tasks(tasks_dir)

    # Load topics lookup
    with open(os.path.join(os.path.dirname(__file__), 'data/topics_lookup.yaml'), 'r') as file:
        topics_lookup = yaml.safe_load(file)

    # Structure tasks
    structured_tasks = structure_tasks(tasks, topics_lookup)

    print(structured_tasks)
    return render(request, 'index.html', {'structured_tasks': structured_tasks})

def load_task(request):
    task_id = request.GET.get('task_id')
    if task_id:
        task_file = os.path.join(tasks_dir, f'{task_id}')
        with open(task_file, 'r') as file:
            task_yaml = yaml.safe_load(file)

        template_file = os.path.join(template_dir, f'{task_yaml["template_id"]}.yaml')
        with open(template_file, 'r') as file:
            template_yaml = yaml.safe_load(file)

        return JsonResponse({'task': yaml.dump(task_yaml), 'template': yaml.dump(template_yaml)})

    return JsonResponse({'error': 'Task ID not provided'}, status=400)

def set_task_context(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Task Details:', data)
            conversation_manager.set_context(data)
            return JsonResponse({'status': 'success'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@csrf_exempt
def send_message(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        response = conversation_manager.get_response(message)
        return JsonResponse({'response': response})