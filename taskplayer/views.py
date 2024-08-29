from django.shortcuts import render
from django.http import JsonResponse
import os
import json
from .conversation_manager import conversation_manager
from .generation_manager import generation_manager
from .db_manager import DB
from django.views.decorators.csrf import csrf_exempt
import re 
from django.core.files.storage import FileSystemStorage
import base64
from django.conf import settings

template_dir = os.path.join(os.path.dirname(__file__), 'data/templates_test')
js_dir =  os.path.join(os.path.dirname(__file__), 'data/scripts')
db = DB()


def load_tasks(subject):
   tasks = db.get_tasks_by_subject(subject) 
   return tasks

def load_task_description(subject):
    tasks = {}
    for task in db.get_tasks_by_subject(subject):
        tasks[task["fauna_id"]] = task['description']        
    return tasks

def structure_tasks(tasks, topics_lookup, language):
    structured_tasks = {}

    for title, fauna_id, topic_id in tasks:
        if topic_id < 0:
            continue
        topic = topics_lookup['topics'][str(topic_id)]
        key_idea_id = topic['key_idea']
        level_id = topic['level']

        level_name = topics_lookup['levels'][str(level_id)][language]
        key_idea_name = topics_lookup['key_ideas'][str(key_idea_id)][language]
        topic_name = topic['title'][language]

        if level_name not in structured_tasks:
            structured_tasks[level_name] = {}

        if key_idea_name not in structured_tasks[level_name]:
            structured_tasks[level_name][key_idea_name] = {}
        
        if topic_name not in structured_tasks[level_name][key_idea_name]:
            structured_tasks[level_name][key_idea_name][topic_name] = []
        
        structured_tasks[level_name][key_idea_name][topic_name].append((title, fauna_id))
    
    return structured_tasks

def index(request):
    language = request.GET.get('lang', 'english')
    subject =  request.GET.get('subject', 'math')
    tasks = load_tasks(subject)
    tasks =  [(tasks[i]['title'][language], tasks[i]["fauna_id"], tasks[i]['topic_id']) for i in range(len(tasks))]
    
    topics_lookup = get_topics_lookup(subject)

    structured_tasks = structure_tasks(tasks, topics_lookup, language)
    return render(request, 'index.html', {'structured_tasks': structured_tasks, 'language': language})

def read_template(template_id):
    template_folder = os.path.join(template_dir, template_id)
    meta_path = os.path.join(template_folder, "meta.json")
    script_path = os.path.join(template_folder, "script.js")
    layout_path = os.path.join(template_folder, "layout.html")
    doc_path = os.path.join(template_folder, "doc.json")
    example_path = os.path.join(template_folder, "example.json")

    with open(meta_path, 'r') as file:
        template = json.load(file)
    with open(script_path, 'r', encoding='utf-8') as file:
        script = file.read()
        template["scripts"] = script
    with open(layout_path, 'r', encoding='utf-8') as file:
        layout = file.read()
        template["html"] = layout
    with open(doc_path, 'r') as file:
        doc = json.load(file)
        template["documentation"] = doc
    with open(example_path, 'r') as file:
        example = json.load(file)
        template["example"] = example
    
    return template

def load_templates(template_dir):
    templates = {}
    for template_id in os.listdir(template_dir):
        template =read_template(template_id)
        templates[template_id] = template['description']
    return templates

def read_task_and_template(task_id, subject, language = "english"):
    task = db.get_task_by_id(task_id)
    template_id = task["template_id"]
    template = read_template(template_id)
    
    return task, template

def load_task(request):
    task_id = request.GET.get('task_id')
    language = request.GET.get('lang', 'english')
    subject = request.GET.get('subject')
    js_code = ""
    if task_id:
        task, template = read_task_and_template(task_id, subject, language)
        # load external p5js code
        if "external_scripts" in task:
            for script_file in task["external_scripts"]:
                js_code += get_js_code(js_dir, script_file)
        return JsonResponse({'task': task, 'template': template, 'p5js':js_code})
    return JsonResponse({'error': 'Task ID not provided'}, status=400)

def get_topics_lookup(subject="math"):
    with open(os.path.join(os.path.dirname(__file__), f'data/topics_lookup_{subject}.json'), 'r', encoding='utf-8') as file:
            topics_lookup = json.load(file)
    return topics_lookup

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

def get_js_code(path, filename):
    file_path = os.path.join(path, filename)
    with open(file_path, 'r') as js_file:
        content = js_file.read()
    return content

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_message_existing_task(language):
    if language == "english":
        return """I found an existing task which is similar to your description. Does this task match your requirements
        or do you want to make changes?"""
    elif language == "german":
        return """Ich habe eine bestehende Aufgabe gefunden, die Ihrer Beschreibung ähnlich ist. Entspricht diese Aufgabe Ihren Anforderungen
        oder möchten Sie Änderungen vornehmen?"""

@csrf_exempt
def generator_message(request):
    if request.method == "POST":
        # PARSE REQUEST
        data = json.loads(request.body)
        user_message = data.get('message', None)
        current_task = data.get('task', None)
        current_p5js = data.get('p5js', None)       
        dialog = data.get('dialog', None)
        language = data.get('language', None)
        img_path = data.get('image', None)
        subject = data.get('subject', None)

        # GET EXISTING TASK DESCRIPTIONS
        existing_tasks = load_task_description(subject)

        # LOAD TEMPLATES 
        templates = load_templates(template_dir)

        # GET EXTERNAL JS FUNCTIONS
        p5js_functions = get_js_descriptions(js_dir)

        p5js_code = None
        message = "Default Message"
        task = None

        # Check existing tasks
        print("\n[Checking existing tasks]")
        response_existing_tasks = generation_manager.check_existing_tasks(user_message, dialog, existing_tasks)
        task_id = response_existing_tasks['existing_task']
        if task_id:
            # existing task found --> Open the task and send a generic message
            message = get_message_existing_task(language)
            task, template = read_task_and_template(task_id, subject, language) 
            if "external_scripts" in task:
                p5js_code = ""
                for script_file in task["external_scripts"]:
                    p5js_code += get_js_code(js_dir, script_file)

        else:
            # Choose template
            print("\n[Choosing Template...]")
            response_template = generation_manager.choose_template(user_message, dialog, templates)
            template_id = response_template["template"]
            template = read_template(template_id) 
            

            # TODO SKIP FIGURE FOR NOW.
            p5js_description = None
            # Check if figure is required
            print("\n[Checking Figure Code]")
            response_p5js = generation_manager.check_p5js(user_message, dialog, p5js_functions)
            if response_p5js["figure"] == True:
                # figure required 
                print("\n[Figure required]")
                p5js_file = response_p5js["existing_p5js"] 
                if p5js_file:
                    # load existing p5js code
                    print("\n[Found existing p5js Code]")
                    p5js_description = p5js_functions[p5js_file]
                    p5js_code = get_js_code(js_dir, p5js_file)
                else:
                    # create new p5js code
                    print("\n[Creating new p5js Code...]")
                    response_p5js_code = generation_manager.generate_p5js(response_p5js["figure_details"])
                    p5js_description = response_p5js_code["description"]
                    p5js_code = response_p5js_code["p5js_code"]

            # Generate Task
            print("\n[Create Task...]")
            response_generate = generation_manager.generate_new(user_message, dialog, template["documentation"], subject, template["example"], p5js_description)


            script = response_generate["script"]
            events = response_generate["events"]
            text = response_generate["text"]
            task = {}
            task["template_id"] = template_id
            task["events"] = events
            task["text"] = text
            task["script"] = script
            task["topic_id"] = 1
            
        
        response = {
            "message":message, 
            "task":task, 
            "template":template, 
            "p5js": p5js_code
        }

        return JsonResponse(response)
    return JsonResponse({"error": "Invalid request method."}, status=400)

@csrf_exempt
def generate_description(request):
    if request.method == "POST":
        # PARSE REQUEST
        # TODO task is not required anymore

        data = json.loads(request.body)
        task = data.get('task', None)   
        template = data.get('template', None)  
        dialog = data.get('dialog', None)

        description_obj = generation_manager.generate_description(dialog, template["description"])

        task["title"] = description_obj["title"]
        task["description"] = description_obj["description"]

        return JsonResponse({'status': 'success', 'task': task})
    return JsonResponse({'status': 'error', 'task': None})

@csrf_exempt
def topic_lookup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task = data.get('task', None)
        subject = data.get('subject', None)
        topics_lookup = get_topics_lookup(subject)
        topic_id = generation_manager.find_topic_id(task["description"], json.dumps(topics_lookup))

        return JsonResponse({'status': 'success', 'topic_id': topic_id, 'lookup': topics_lookup})
    return JsonResponse({'status': 'error', 'topic_id': None})

@csrf_exempt
def save_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task = data.get('task', None)
        p5js = data.get('p5js', None)
        subject = data.get('subject', None)
        

        # if new p5js was generated, save it to a js file
        if p5js and "external_scripts" not in task:
            filename = "script_"+str(len(os.listdir(js_dir)))+".js"
            with open(os.path.join(js_dir, filename), "w") as file:
                file.write(p5js)
            task["external_scripts"] = [filename]

        task["subject"] = subject
        db.save_task(task)

        return JsonResponse({'status': 'success', 'message': 'Task saved successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

@csrf_exempt
def upload_image(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)
        file_url = fs.url(filename)
        return JsonResponse({'path': file_url})
    return JsonResponse({'error': 'Invalid request'}, status=400)