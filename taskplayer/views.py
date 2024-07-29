from django.shortcuts import render
from django.http import JsonResponse
import os
import json
from .conversation_manager import conversation_manager
from .generation_manager import generation_manager
from django.views.decorators.csrf import csrf_exempt
import re 
from django.core.files.storage import FileSystemStorage

TASK_DIR = os.path.join(os.path.dirname(__file__), 'data/tasks')
template_dir = os.path.join(os.path.dirname(__file__), 'data/templates')
js_dir =  os.path.join(os.path.dirname(__file__), 'data/scripts')


def load_tasks(tasks_dir):
    tasks = []
    task_files = []
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.json'):
            with open(os.path.join(tasks_dir, task_file), 'r', encoding='utf-8-sig') as file:
                task = json.load(file)
                tasks.append(task)
                task_files.append(task_file)
    return tasks, task_files

def load_task_description(tasks_dir):
    tasks = {}
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.json'):
            with open(os.path.join(tasks_dir, task_file), 'r', encoding='utf-8') as file:
                task = json.load(file)
                tasks[task_file] = task['description']["english"]
    return tasks

def structure_tasks(tasks, topics_lookup, language):
    structured_tasks = {}

    for title, filename, topic_id in tasks:
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
        
        structured_tasks[level_name][key_idea_name][topic_name].append((title, filename))
    
    return structured_tasks

def index(request):
    language = request.GET.get('lang', 'english')
    subject =  request.GET.get('subject', 'math')
    tasks_dir = os.path.join(TASK_DIR,subject)
    tasks, task_files = load_tasks(tasks_dir)
    tasks =  [(tasks[i]['title'][language], task_files[i], tasks[i]['topic_id']) for i in range(len(tasks))]
    topics_lookup = get_topics_lookup(subject)

    structured_tasks = structure_tasks(tasks, topics_lookup, language)
    return render(request, 'index.html', {'structured_tasks': structured_tasks, 'language': language})

def read_template(template_id):
    template_file = os.path.join(template_dir, template_id)
    with open(template_file, 'r') as file:
        template = json.load(file)
    return template

def read_task_and_template(task_id, subject, language = "english"):
    if ".json" not in task_id:
        task_id+=".json"
    tasks_dir = os.path.join(TASK_DIR,subject)
    task_file = os.path.join(tasks_dir, f'{task_id}')
    with open(task_file, 'r', encoding="utf-8") as file:
        task = json.load(file)
    template_id = f'{task["template_id"]}.json'
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

def load_templates(template_dir):
    templates = {}
    for template_file in os.listdir(template_dir):
        if template_file.endswith('.json'):
            with open(os.path.join(template_dir, template_file), 'r', encoding='utf-8') as file:
                template = json.load(file)
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

def get_js_code(path, filename):
    file_path = os.path.join(path, filename)
    with open(file_path, 'r') as js_file:
        content = js_file.read()
    return content

def get_example_task(template,subject="math"):
    task_file = template["example_task"]+".json"
    tasks_dir = os.path.join(TASK_DIR,subject)
    filepath = os.path.join(tasks_dir, task_file)
    if not os.path.exists(filepath):
        # example task does not exist
        # Fallback 1 choose first task that uses this template
        tasks, task_files = load_tasks()
        task_files_template = [task_files[i] for i in range(len(task_files)) if tasks[i]["template_id"] == template["template_id"]]
        if len(task_files_template)>0:
            filepath = os.path.join(tasks_dir, task_files_template[0])
        else:
            # no tasks for this template
            # Fallback 2 choose first task in list of all tasks 
            filepath = os.path.join(tasks_dir, task_files[0])
    with open(filepath, 'r', encoding='utf-8') as file:
        task = json.load(file)
            

    return task

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

        bool_generate_p5js = False
        bool_update = False
        p5js_code = None
        p5js_file = None

        

        tasks_dir = os.path.join(TASK_DIR,subject)

        print(tasks_dir)

        # GET EXISTING TASK DESCRIPTIONS
        existing_tasks = load_task_description(tasks_dir)

        print(existing_tasks)

        # LOAD TEMPLATES 
        templates = load_templates(template_dir)

        # GET EXTERNAL JS FUNCTIONS
        p5js_functions = get_js_descriptions(js_dir)
        
        # TEST
        task_analysis = generation_manager.analyse(user_message,dialog, existing_tasks, templates, p5js_functions, img_path, subject)
        task_id = task_analysis["existing_task"]
        if task_id:
            task, template = read_task_and_template(task_id, subject, language)
            message = task_analysis["message"]
            if "external_scripts" in task:
                p5js_code = ""
                for script_file in task["external_scripts"]:
                    p5js_code += get_js_code(js_dir, script_file)

        else:
            template_id = task_analysis["template"]
            template = read_template(template_id) 
            example_task = get_example_task(template)
            if example_task != None:
                if "external_scripts" in example_task:
                    example_task.pop('external_scripts')
                example_task.pop('topic_id')
            
            # base generation (no figure, no update)
            prompt = generation_manager.prompt_generate(user_message,dialog,json.dumps(template),example_task, img_path, subject)

            # Optional Figure Prompt
            if task_analysis["figure"] and task_analysis["figure_path"] is None:
                p5js_file = task_analysis["existing_p5js"]
                if p5js_file:
                    # Use existing p5js function
                    function_description = p5js_functions[p5js_file]
                    p5js_code = get_js_code(js_dir, p5js_file)
                    prompt += generation_manager.prompt_existing_p5js(function_description)
                else:
                    # Generate new p5js function
                    figure_details = task_analysis["figure_details"]
                    prompt += generation_manager.prompt_new_p5js(figure_details)
                    bool_generate_p5js = True
            
            # Optional update existing task
            if current_task:
                prompt += generation_manager.prompt_generate_update(current_task, current_p5js)
                bool_update = True
            prompt += generation_manager.prompt_output_format(bool_update, bool_generate_p5js)
            response = generation_manager.generate(prompt)
   
            message = response["message"]

            if bool_update:
                if response["script"] is None:
                    script = current_task["script"]
                else:
                    script = response["script"]
                    
                if response["events"]  is None:
                    events = current_task["events"]
                else:
                    events = response["events"]
                if response["text"]  is None:
                    text = current_task["text"]
                else:
                    text = response["text"]
            else:
                script = response["script"]
                events = response["events"]
                text = response["text"]
            script.replace("\\\\\\\\", "\\\\")
            script.replace("\\\\\\", "\\\\")
            task = {}
            task["template_id"] = template_id[:-5]
            task["events"] = events
            task["text"] = text
            task["script"] = script
            task["topic_id"] = 1

            if "p5js" in response:
                p5js_code = response["p5js"]
                if p5js_code is None:
                    p5js_code = current_p5js
                else:
                    p5js_code = p5js_code

            if p5js_file:
                task["external_scripts"] = [p5js_file]
                p5js_code = get_js_code(js_dir, p5js_file)

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
        data = json.loads(request.body)
        task = data.get('task', None)   
        template = data.get('task', None)  
        dialog = data.get('dialog', None)

        description_obj = generation_manager.generate_description(json.dumps(task), json.dumps(template), dialog)

        task["title"] = description_obj["title"]
        task["description"] = description_obj["description"]
        task["task_id"] = description_obj["task_id"]

        return JsonResponse({'status': 'success', 'task': task})
    return JsonResponse({'status': 'error', 'task': None})

@csrf_exempt
def topic_lookup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task = data.get('task', None)
        subject = data.get('subject', None)
        topics_lookup = get_topics_lookup(subject)
        topic_id = generation_manager.find_topic_id(task["description"]["english"], json.dumps(topics_lookup))

        return JsonResponse({'status': 'success', 'topic_id': topic_id, 'lookup': topics_lookup})
    return JsonResponse({'status': 'error', 'topic_id': None})

@csrf_exempt
def task_ids(request):
    if request.method == 'GET':
        subject = request.GET.get('subject')
        tasks_dir = os.path.join(TASK_DIR,subject)
        _, task_files = load_tasks(tasks_dir)
        task_ids = [f[:-5] for f in task_files]

        return JsonResponse({'status': 'success', 'task_ids': task_ids})
    return JsonResponse({'status': 'error', 'task_ids': None})

@csrf_exempt
def save_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task = data.get('task', None)
        p5js = data.get('p5js', None)
        subject = data.get('subject', None)

        tasks_dir = os.path.join(TASK_DIR,subject)

        # if new p5js was generated, save it to a js file
        if p5js and "external_scripts" not in task:
            filename = "script_"+str(len(os.listdir(js_dir)))+".js"
            with open(os.path.join(js_dir, filename), "w") as file:
                file.write(p5js)
            task["external_scripts"] = [filename]

        # find topic id and save task
        task_id = task.get('task_id', 'untitled_task')
        task_path = os.path.join(tasks_dir, f'{task_id}.json')

        with open(task_path, 'w') as task_file:
            json.dump(task, task_file, ensure_ascii=True, indent=4)

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