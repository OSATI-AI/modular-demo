from django.shortcuts import render
from django.http import JsonResponse
import yaml
import os
import json
from .conversation_manager import conversation_manager
from .generation_manager import generation_manager
from django.views.decorators.csrf import csrf_exempt
from jinja2 import Template
import re 

tasks_dir = os.path.join(os.path.dirname(__file__), 'data/tasks')
template_dir = os.path.join(os.path.dirname(__file__), 'data/templates')
js_dir =  os.path.join(os.path.dirname(__file__), 'static/scripts')


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

def generate(request):
    return render(request, 'generate.html')

def load_templates(template_dir):
    templates = {}
    for template_file in os.listdir(template_dir):
        if template_file.endswith('.yaml'):
            with open(os.path.join(template_dir, template_file), 'r', encoding='utf-8') as file:
                template = yaml.safe_load(file)
                templates[template_file] = template.get('description', '')
    return templates

def extract_description(file_content):
    start_identifier = r'\*\*\* Function Description Start \*\*\*'
    end_identifier = r'\*\*\* Function Description End \*\*\*'
    
    pattern = re.compile(f'{start_identifier}(.*?){end_identifier}', re.DOTALL)
    match = pattern.search(file_content)
    
    if match:
        description = match.group(1).strip()
        return description
    else:
        return None

def get_js_descriptions(path):
    descriptions = {}
    
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.js'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as js_file:
                    content = js_file.read()
                    description = extract_description(content)
                    if description:
                        descriptions[file] = description
    
    return descriptions

@csrf_exempt
def generator_message(request):
    if request.method == "POST":
        # PARSE REQUEST
        data = json.loads(request.body)
        user_message = data.get('message')
        task = data.get('task')       
        dialog = data.get('dialog')
        language = data.get('language')

        # PICK AND LOAD TEMPLATES 
        templates = load_templates(template_dir)
        template_file = generation_manager.get_template( user_message, dialog, templates)
        template_file = template_file.replace(" ", "")
        print("\n\nTEMPLATE: ", template_file)


        # GET EXTERNAL JS FUNCTIONS
        external_js = get_js_descriptions(js_dir)
        
        # GENERATE TASK CODE 
        with open(os.path.join(template_dir, template_file), 'r', encoding='utf-8') as file:
            template = file.read()
        message, task = generation_manager.get_response(user_message, dialog, task, template, external_js)
        
        print("\n\nTASK: ", task)

        # PARSE AND RETURN TASK CODE AND MESSAGE
        try:
            task = task.split("```yaml")[1][:-3]
        except Exception as e:
            print("\n\n\n\n ERROR: Could not split the task")
            print("LLM OUTPUT: ")
            print(task)
            print("error message: ")
            print(e)

        task = fill_text(yaml.safe_load(task), language)

        response = {
            "message":message, 
            "task":yaml.dump(task), 
            "template":template
        }

        return JsonResponse(response)
    return JsonResponse({"error": "Invalid request method."}, status=400)