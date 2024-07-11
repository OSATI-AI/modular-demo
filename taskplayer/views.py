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
js_dir =  os.path.join(os.path.dirname(__file__), 'data/scripts')

def load_tasks(tasks_dir):
    tasks = []
    task_files = []
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.yaml'):
            with open(os.path.join(tasks_dir, task_file), 'r', encoding='utf-8') as file:
                task = yaml.safe_load(file)
                tasks.append(task)
                task_files.append(task_file)
    return tasks, task_files

def load_task_description(tasks_dir):
    tasks = {}
    # Load all tasks in the given directory and create list of tuples (title, filename, topic_id)
    for task_file in os.listdir(tasks_dir):
        if task_file.endswith('.yaml'):
            with open(os.path.join(tasks_dir, task_file), 'r', encoding='utf-8') as file:
                task = yaml.safe_load(file)
                tasks[task_file] = task['description']["english"]
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
    tasks, task_files = load_tasks(tasks_dir)
    tasks =  [(tasks[i]['title'][language], task_files[i], tasks[i]['topic_id']) for i in range(len(tasks))]

    with open(os.path.join(os.path.dirname(__file__), 'data/topics_lookup.yaml'), 'r', encoding='utf-8') as file:
        topics_lookup = yaml.safe_load(file)

    structured_tasks = structure_tasks(tasks, topics_lookup, language)

    return render(request, 'index.html', {'structured_tasks': structured_tasks, 'language': language})

def read_template(template_id):
    template_file = os.path.join(template_dir, template_id)
    with open(template_file, 'r') as file:
        template_yaml = yaml.safe_load(file)
    return template_yaml

def read_task_and_template(task_id, language = "english"):
    task_file = os.path.join(tasks_dir, f'{task_id}')
    with open(task_file, 'r', encoding="utf-8") as file:
        task_yaml = yaml.safe_load(file)
    template_id = f'{task_yaml["template_id"]}.yaml'
    template_yaml = read_template(template_id)
    
    return task_yaml, template_yaml

def load_task(request):
    task_id = request.GET.get('task_id')
    language = request.GET.get('lang', 'english')
    js_code = ""
    if task_id:
        task_yaml, template_yaml = read_task_and_template(task_id, language)
        # load external p5js code
        if "external_scripts" in task_yaml:
            for script_file in task_yaml["external_scripts"]:
                js_code += get_js_code(js_dir, script_file)
            
        return JsonResponse({'task': yaml.dump(task_yaml), 'template': yaml.dump(template_yaml), 'p5js':js_code})

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

        print("\n\n\n--------------------------------")
        print("MESSAGE: ", user_message)
        print("TASK CONTEXT: ", task_context)
        print("ACTION LOG:", action_log)
        print("--------------------------------\n\n\n")

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

def get_js_code(path, filename):
    file_path = os.path.join(path, filename)
    with open(file_path, 'r') as js_file:
        content = js_file.read()
    return content

def get_example_task(path, template_id):
    template_id = template_id.replace(".yaml", "")
    tasks,_ = load_tasks(path)
    task_filtered = [t for t in tasks if t["template_id"] == template_id]
    return task_filtered[0]

def remove_code_identifier(value):
    if value.startswith("```javascript"):
        value = value.replace("```javascript", "")
    elif value.startswith("```json"):
        value =value.replace("```json", "")
    elif value.startswith("```yaml"):
        value =value.replace("```yaml", "")
    #value = value.replace("\n", "")

    return value[:-3]

@csrf_exempt
def generator_message(request):
    if request.method == "POST":
        # PARSE REQUEST
        data = json.loads(request.body)
        user_message = data.get('message')
        current_task = data.get('task')
        current_p5js = data.get('p5js')       
        dialog = data.get('dialog')
        language = data.get('language')

        bool_generate_p5js = False
        bool_update = False
        p5js_code = "None"
        p5js_file = "None"

        # GET EXISTING TASK DESCRIPTIONS
        existing_tasks = load_task_description(tasks_dir)

        # LOAD TEMPLATES 
        templates = load_templates(template_dir)

        # GET EXTERNAL JS FUNCTIONS
        p5js_functions = get_js_descriptions(js_dir)
        
        # TEST
        task_analysis = generation_manager.analyse(user_message,dialog, existing_tasks, templates, p5js_functions)
        if "```json" in task_analysis:
            task_analysis = task_analysis.split("```json")[1][:-3]
        try:
            task_analysis = json.loads(task_analysis)
        except Exception as e:
            print("\n\n ERROR PARSING ANALYSIS AS JSON")
            print("JSON CONTENT: \n")
            print(task_analysis)
            print("\n Error: \n", e)


        #print("\n\n\n---------------ANALYSIS---------------: \n", task_analysis, "\n------------------------------\n\n\n")

        task_id = task_analysis["existing_task"]
        if task_id != "None":
            task_yaml, template_yaml = read_task_and_template(task_id, language)
            message = task_analysis["message"]
            if "external_scripts" in task_yaml:
                p5js_code = ""
                for script_file in task_yaml["external_scripts"]:
                    p5js_code += get_js_code(js_dir, script_file)


        else:
            template_id = task_analysis["template"]
            template_yaml = read_template(template_id) 

            example_task = get_example_task(tasks_dir, template_id)
            if "external_scripts" in example_task:
                example_task.pop('external_scripts')
            example_task.pop('topic_id')
            
            # base generation (no figure, no update)
            prompt = generation_manager.prompt_generate(user_message,dialog,yaml.dump(template_yaml),example_task)

            # Optional Figure Prompt
            figure = task_analysis["figure"] == "True" or task_analysis["figure"] == True
            
            if figure:
                p5js_file = task_analysis["existing_p5js"]
                if p5js_file != "None":
                    # Use existing p5js function
                    function_description = p5js_functions[p5js_file]
                    p5js_code = get_js_code(js_dir, p5js_file)
                    prompt += generation_manager.prompt_existing_p5js(function_description)
                else:
                    # Generate new p5js function
                    #print("NEW P5JS")
                    figure_details = task_analysis["figure_details"]
                    prompt += generation_manager.prompt_new_p5js(figure_details)
                    bool_generate_p5js = True
            
            # Optional update existing task
            if current_task != "None":
                prompt += generation_manager.prompt_generate_update(yaml.safe_load(current_task), current_p5js)
                bool_update = True

            #print("bool_update: ", bool_update)

            prompt += generation_manager.prompt_output_format(bool_update, bool_generate_p5js)
            response = generation_manager.generate(prompt)
            response = remove_code_identifier(response)
            
            print("response: \n\n", response)

            response = json.loads(response, strict=False)
            
            #print("\n\n\n---------------RESPONSE---------------: \n", response, "\n------------------------------\n\n\n")
            
            message = response["message"]

            if bool_update:
                current_task = yaml.safe_load(current_task)
                if response["script"] == "[NO_CHANGE]":
                    script = current_task["script"]
                else:
                    script = remove_code_identifier(response["script"])
                if response["events"] == "[NO_CHANGE]":
                    events = current_task["events"]
                else:
                    events = yaml.safe_load(remove_code_identifier(response["events"]))
                if response["text"] == "[NO_CHANGE]":
                    text = current_task["text"]
                else:
                    text = yaml.safe_load(remove_code_identifier(response["text"]))
                if response["title"] == "[NO_CHANGE]":
                    title = current_task["title"]
                else:
                    title = yaml.safe_load(remove_code_identifier(response["title"]))
                if response["description"] == "[NO_CHANGE]":
                    description = current_task["description"]
                else:
                    description = yaml.safe_load(remove_code_identifier(response["description"]))
                if response["task_id"] == "[NO_CHANGE]":
                    task_id = current_task["task_id"]
                else:
                    task_id = response["task_id"]
            else:
                script = remove_code_identifier(response["script"])
                events = yaml.safe_load(remove_code_identifier(response["events"]))
                text = yaml.safe_load(remove_code_identifier(response["text"]))
                title = yaml.safe_load(remove_code_identifier(response["title"]))
                description = yaml.safe_load(remove_code_identifier(response["description"]))
                task_id =response["task_id"]

            task_yaml = {}
            task_yaml["title"] = title
            task_yaml["description"] = description
            task_yaml["task_id"] = task_id
            task_yaml["template_id"] = template_id[:-5]
            task_yaml["events"] = events
            task_yaml["text"] = text
            task_yaml["script"] = script
            task_yaml["topic_id"] = 1

            if "p5js" in response:
                p5js_code = response["p5js"]
                if p5js_code == "[NO_CHANGE]":
                    p5js_code = current_p5js
                else:
                    p5js_code = remove_code_identifier(p5js_code)

            if p5js_file != "None":
                task_yaml["external_scripts"] = [p5js_file]
                p5js_code = get_js_code(js_dir, p5js_file)
            task_yaml = yaml.safe_load(yaml.dump(task_yaml))

        response = {
            "message":message, 
            "task":yaml.dump(task_yaml), 
            "template":yaml.dump(template_yaml), 
            "p5js": p5js_code
        }

        return JsonResponse(response)
    return JsonResponse({"error": "Invalid request method."}, status=400)


@csrf_exempt
def save_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        task_yaml = data.get('task', '')
        p5js = data.get('p5js', 'None')

        task_dict = yaml.safe_load(task_yaml)

        # if new p5js was generated, save it to a js file
        if p5js != 'None' and "external_scripts" not in task_dict:
            filename = "script_"+str(len(os.listdir(js_dir)))+".js"
            with open(os.path.join(js_dir, filename), "w") as file:
                file.write(p5js)
            task_dict["external_scripts"] = [filename]

        # find topic id and save task
        task_id = task_dict.get('task_id', 'untitled_task')
        task_path = os.path.join(tasks_dir, f'{task_id}.yaml')
        with open(os.path.join(os.path.dirname(__file__), 'data/topics_lookup.yaml'), 'r', encoding='utf-8') as file:
            topics_lookup = yaml.safe_load(file)
        topic_id = generation_manager.find_topic_id(task_dict["description"]["english"], yaml.safe_dump(topics_lookup))
        topic_id = int(topic_id)
        task_dict["topic_id"] = topic_id

        with open(task_path, 'w') as task_file:
            yaml.dump(task_dict, task_file, default_flow_style=False)

        return JsonResponse({'status': 'success', 'message': 'Task saved successfully.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})