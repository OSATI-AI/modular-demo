# conversation_manager.py


import os
import json
from openai import OpenAI
import time

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

EXAMPLE_P5JS = """
        /* 
        *** Function Description Start ***
        Description: 
        The plot_graph function uses p5.js to plot any arbitrary mathematical function. It takes in the x and y range in which the function should be displayed and a callback function to determine the function term for the graph.

        How to use:
        1. Define a mathematical function as a callback.
        2. Call the plot_graph function with the container ID, the callback function, and the x and y ranges.

        Example:
        function quadraticFunction(x) {
            return x * x;
        }

        plot_graph('container', quadraticFunction, [-10, 10], [-10, 100]);
        *** Function Description End ***
        */
        function drawGrid(sketch, xRange, yRange) {
            sketch.stroke(200); // Light grey color for grid lines
            sketch.strokeWeight(1);

            // Draw vertical grid lines
            for (let x = 0; x < sketch.width; x += sketch.width / (xRange[1] - xRange[0])) {
                sketch.line(x, 0, x, sketch.height);
            }

            // Draw horizontal grid lines
            for (let y = 0; y < sketch.height; y += sketch.height / (yRange[1] - yRange[0])) {
                sketch.line(0, y, sketch.width, y);
            }
        }

        function drawAxes(sketch) {
            sketch.stroke(0); // Black color for axes
            sketch.strokeWeight(3);
            // Draw X axis
            sketch.line(0, sketch.height / 2, sketch.width, sketch.height / 2);
            // Draw Y axis
            sketch.line(sketch.width / 2, 0, sketch.width / 2, sketch.height);
        }

        function drawFunction(sketch, func, xRange, yRange) {
            sketch.stroke(255, 0, 0); // Red color for the function line
            sketch.strokeWeight(2);
            sketch.noFill();
            sketch.beginShape();
            for (let x = xRange[0]; x <= xRange[1]; x += 0.1) {
                let y = func(x);
                let canvasX = sketch.map(x, xRange[0], xRange[1], 0, sketch.width);
                let canvasY = sketch.map(y, yRange[0], yRange[1], sketch.height, 0);
                sketch.vertex(canvasX, canvasY);
            }
            sketch.endShape();
        }

        function plot_graph(container, func, xRange, yRange){
            document.getElementById(container).innerHTML = ""
            var s = function( sketch ) {
                sketch.setup = function() {
                    canvas = sketch.createCanvas(400, 400);
                    canvas.parent(container);
                    sketch.background(255);
                    drawGrid(sketch, xRange, yRange);
                    drawAxes(sketch);
                    drawFunction(sketch, func, xRange, yRange);
                };
            };

            new p5(s);
        };"""


MODEL = "gpt-4o"#"meta-llama/llama-3.1-405b-instruct"#"gpt-4o"#"openai/gpt-4o-mini"#""#"" 

class GenerationManager:
    def __init__(self, api_key, model_name=MODEL, api_base='https://openrouter.ai/api/v1'):
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key)
        self.model = model_name

    def persona(self):
        return """You are a helpfull AI assistant, designed to help teachers to design learning tasks
        for their students. Your job is to listen to the description and requirements of the teacher
        and create a task according to certain design rules."""
        
    def prompt_analyse(self, user_message,dialog, existing_tasks, templates, p5js_functions, img_path, subject):
        prompt =  f""" You will receive the user's message and the complete previous dialog which includes 
        the description of the learning task that should be created. Work through the following steps and give your answer in json format.

        PREVIOUS_MESSAGE: {user_message}
        FULL_DIALOG: {dialog}
        SCHOOL_SUBJECT: {subject}

        STEP 1:
        Below you find a list of descriptions of tasks that already exists. Check all of them and decide,
        if any of those tasks matches all of the requirements of the described task. If you found a task
        that implements all features of what the user asked for, add the field "existing_task" to your
        answer and give the name of the task as value. 
        Example: 
        "existing_task": "task_gradient.json"
        If you found and existing task, add a field "message" to your answer as well and describe that 
        found an existing task that could match the requirements, then ask if the user is happy with this
        choice or if he/she wants to change someting. Do not mention the filename of the task, the user
        will see the task in a preview window.If you found an existing task, you do not have to perform
        any of the following steps, just give your answer in json format and include the "existing_task" 
        and "message" fields. If you did not find a task that matches the requirements, set the value of "existing_task"
        to null and continue with STEP 2.
        IMPORTANT: If the given dialog shows, that you already found an existing task but the user wants to change 
        something, set "existing_task" to null and proceed as if you did not found an existing task.
        LIST OF EXISTING TASKS:
        {existing_tasks}

        STEP 2:
        Select a template for this type of task that matches the requirements of the user.
        You are only allowed to pick exactly one template out of the provided lists of templates and their description.
        Add a field "template" to your answer and give the name of the template as value.
        Example:
        "template": "template_multiple_choice.json"
        LIST OF TEMPLATES:
        {templates}

        NOTE: 
        The template "template_default" is a fallback solution. Only if no other template
        would be possible to solve the requirements, choose thise template. It provides only an empty
        container which can be filled with arbitrary elements to be able to implement every possible layout. 
        But only use this one as the last fallback. 
        """



        if img_path:
            prompt += f"""
            IMAGE:
            In addition to the message, the user also uploaded an image, which is available 
            under the relative url: {img_path}
            Set the fields of the output object as follows:
            "image": true, 
            "existing_p5js":null,
            "figure_details":null,
            "figure_path": [Give here the relative url of the image]
            """

        else: 
            prompt += f"""
            STEP 3:
            Analyse if the task requires to display a figure. This is only possible if the selected template
            provide a container to display images/figures. Add a field "figure" to your answer and set its value
            to true if a figure is required and to false if no figure is required.  
            You are only allowed to use p5js for creating figures.
            Below, there is a list of existing p5js functions with their according descriptions. Check each of them
            and decide if any of them provides a figure that matches the requirements. Add a field "existing_p5js"
            to your answers. If you found an existing function that you will use, give its filename as value, if not
            give null as value.
            Examples:
            "existing_p5js":"figure.js"
            "existing_p5js":null
            Add a field "figure_details" to your answer. If there was an existing p5js function or there is no figure at all set the value of 
            the field to null. If no existing function matches the requirements, give a 
            detailed description of how the function should be designed (no code yet) as value for the field. If you describe
            how a new function should look like, I would like to create functions that are as general as possible
            in order to reuse them later. So e.g. if the user wants a figure of a linear function, instead of describing
            a p5js function that only can render linear functions, instead try to describe a function that can plot
            any kind of mathematical function. 
            LIST OF EXISTING P5JS FUNCTIONS:
            {p5js_functions}            
            IMPORTANT: 
            Set "figure_path" always to null.
            """
        return prompt

    def prompt_generate(self, user_message,dialog, template, example_task, img_path, subject):

        script = example_task["script"]
        text = example_task["text"]
        events = example_task["events"]

        prompt = f""" 
        You will receive the user's message and the complete previous dialog which includes 
        the description of the learning task that should be created. Work through the following steps and give your answer in json format.

        PREVIOUS_MESSAGE: {user_message}
        FULL_DIALOG: {dialog}
        SCHOOL SUBJECT: {subject}

        You will create a object that contains certain descriptive fields as well as javascript code that controlls the elements of the task.
        The object also defines and handles certain events that manages communication with the application
        that renders the task. A task is always connected to a certain template. The template defines 
        the overall layout of the task and creates container elements. The task is only allow to work and
        generate things inside these elements. Below, you can find the code of the template that you have to use
        an an EXAMPLE_TASK to show you how to use the framework. Always stick to this framework and only use the fields as shown in the examples. 

        TEMPLATE:
        {template}
        
        EXAMPLE_TASK:
        "events": {events}
        "text":{text}
        "script":"{script}"

        Text elements can be referenced within the script by using double curly brackets:
        Example: answerLabel.innerHTML = "<b>{{name}}: </b>";
        Every text element has to be declared in the "text" field and need a unique identifier to reference it in the javascript code.
        So even if we have a list of text elements that should be displayed somewhere, every text element need an id and has to be
        referenced with double curly brackets. 

        You are not supposed to handle feedback to the user. The only thing you have to take care is to handle the evaluation
        event and return an object in the format: 
        userInput: [INPUT OF THE USER]
        result: [CORRECT ANSER]
        isCorrect: [TRUE or FALSE]
        Please note: The evaluation function ALWAYS have to return a single object with those three parameters. Even if the task
        is e.g. a multiple choice task with several correct answers, decide based on the logic of the task and the description of the user
        when a task is either correct or not correct. There is no way to describe partially correct answers or lists of booleans.
        You have to decide and pick one boolean to set as value. 

        Whenever you generate random numbers in the javascript code, make sure that the variables 
        are really saved as numbers. Use functions like parseFloat or parseInt to ensure that.

        Try to implement every task in a way, that we can have multiple exercises. Fore example by
        randomly generating certain numbers or other aspects of the function. When doin this, 
        always make sure to handle the refresh event correctly and generate new random details for the
        task. Also make sure to update the correct result to ensure that the evaluate event is handled correctly.

        It is very important that you handle the getTaskDetails event and return a very detailed description of every information connected
        to the task. This includes all static information that do not change when refreshing the task as well as dynamic information like
        the reandom generated numbers, or the correct solution. This details are later used to explain an AI tutor the whole situation as exact as possible.

        Whenever a user is required to input numbers or other mathematical terms, use "math-field" from the mathlive library whenever possible. (You can always assume that it is available in the current context)
        If you are using "math-field" elements and want to display the calculation inside of it, make sure to use "setValue" to
        really add the equation to the math field. 
        Example Code:

        n1 = Math.floor(Math.random() * 9 + 1) * 10;
        n2 = Math.floor(Math.random() * 9 + 1) * 10;
        answer = n1 * n2;
        const equation = `${{n1}} \\cdot ${{n2}} = \\placeholder[answer]{{}}`;
        questionElement.innerText = "{{question}}";
        const answerField = document.createElement("math-field");
        answerField.id = "equation";
        // THIS IS THE IMPORTANT PART:
        answerField.setValue(equation);
        
        answerField.mathVirtualKeyboardPolicy = "manual";
        answerField.readonly = true;
        answerElement.append(answerField);

        Always try to implement the user request as accurately as possible, but always stick to
        format given by the template and the provided examples. 
        """

        if img_path:
            prompt += f"""
            IMAGE:
            In addition to the message, the user also uploaded an image, which is available 
            under the relative url: {img_path}
            """
        return prompt

    def prompt_generate_update(self, task, p5js=None):
        script = task["script"]
        text = task["text"]
        events = task["events"]
        
        prompt = f"""Below I will provide the object of an existing task. Use this code as a starting point update it
        to implement the described task. 
        CURRENT TASK:
        "events": "{events}"
        "text":"{text}"
        "script":"{script}"
        """
        if p5js is not None and p5js != "None": 
            prompt += f"""
            There is existing p5js code for the figure. If changes to the figure are required, 
            use this code as a starting point and update it accordingly. If there are changes to 
            the p5js code, always provide the full updated code (not just the changes). 
            CURRENT P5JS CODE:
            {p5js}
            """

        return prompt 

    def prompt_output_format(self, update = False, p5js = False):
        prompt = """You always answer in json format and use the following keys:
        message: "[YOUR MESSAGE]" [Give a short answer to the previous user message in which you explain what you 
        just did and what changes you have added. But keep it short and simple and do not provide
        technical details like code. Just stick to what happend to the task layout or behavior.
        Always answer in the same language as the previous user message was written in.]
        "events":[YOUR EVENTS OBJECT][Here you will creat a object that contains all outgoing and incoming events that are handled in the script]
        "text":[YOUR TEXT OBJECT][Here you will specify all texts that are used in the script. Output a object that contains english and german translations for every text element. For text that contains "you", always use the "Du" in the german translation instead of "Sie"]
        "script":"[YOUR JAVASCRIPT CODE]"[Here you will write your javascript code for the task. NEVER use comments on your javascript code!]
        """
        if p5js:
            prompt += """
            "p5js":"[YOUR Javascript CODE]"[here you will provide any p5js javascript code 
            for the figure. Stick to the provided example.]
            """
        
        if update:
            prompt += """
            Only give updated code for the fields that had changed. If a field e.g. text or script was not affected by your update,
            just give null as value. For example:
            "script": null
            """
            if p5js:
                prompt += """
                Always try to change as less fields as possible. For example, if the users wants you to change the figure,
                try to only update the p5js code and leave the script unchanged. Only if the change is not possible without
                changing the script as well, provide updates to both fields.
                """
        return prompt
    
    def prompt_existing_p5js(self, function_description):
        return f"""The task should contain a figure, that should be drawn using p5js. There is an existing
        p5js function that you have to use. Do not provide any new p5js code but just call the given function
        from inside your javascript code. You can assume that the function is available in the current context.
        Here is a detailed description of the p5js function and how to use it:
        {function_description}
        """
    
    def prompt_new_p5js(self, figure_details):
        return f"""The task should contain a figure, that should be drawn using p5js. You have to create
        the p5js code to render the required figure. Here is a detailed description: 
        {figure_details}

        I would like to create functions that are as general as possible
        in order to reuse them later. So e.g. if the user wants a figure of a linear function, instead of describing
        a p5js function that only can render linear functions, instead try to describe a function that can plot
        any kind of mathematical function. Also make the p5js code as independent from the current task as possible.
        You can create multiple functions to make the code more structured but make sure, that there is only one
        function that will be called from the task code. You can assume that the p5js function will later be 
        available to the task code, but not vice versa, so you are not allowed to use any variables or functions
        from the task code inside your p5js code.  

        When creating p5js code, stick to the following style, where a new p5js object is created 
        inside the function and a parent element is given to set as the container p5js should render the figure into.
        Example: 
        {EXAMPLE_P5JS}

        As you can see, the javascript code contains a small documentation as a comment on top of the code. Please 
        also provide such a documentation in the same format as in the example. It is important to use the exact same
        format including the marker that shows where the documentation starts and ends.
        /* 
        *** Function Description Start ***
        [YOUR]
        *** Function Description End ***
        */
        If your code contains multiple functions
        you only should provide a documentation for the main function that can be called from other scripts. Provide a description
        of what the fuctions does as well as a short example code on how to use it.
        
        Then you should call your created p5js function from the javascript code inside the task to display it.
        You can always assume that your p5js code is available in the current scope, so you can just call the function from your
        task script. Please put no other p5js related code inside the task script but allm of the p5js code should be put into a
        separate field in the output object as described below. 
        """

    def prompt_description(self, task,template, dialog):
        return f"""
        Below you will find a json object that defines a learning task. This task was created based on the
        following dialog between a user and an assistant:

        {dialog}

        Here is the task that was created based on this dialog:

        {task}

        And here is the template that defines the overall layout of the task

        {template}

        Your task is to find a title, a description and a task_id for this task.

        "title": [YOUR TITLE OBJECT][Create a short title for the task. Output an object and add an english and german version]
        "description": [YOUR DESCRIPTION OBJECT][Create a detailed description for the task.  Output an object and add an english and german version]
        "task_id": [YOUR TASK ID] [As task id use the english title, put task_ in front of it, make all characters lower case and replace all whitespaces with underscores]
        
        The title will be the first thing a student will see when opening the task, so make sure it is short, descriptive and informative

        The student will never see your generated "description". This description is used to tell an AI Tutor the context
        of the current task. Since the tutor can not see the screen, your description should be very detailed and contain
        all information that you have and that are important about the task. What not should be included are the dynamic details
        so everything which is randomly generated on refresh. But everything wich is static such as the layout, the general task description,
        colors, input fields etc. should be described here. 

        EXAMPLE: 
        """ + """"
        task_id": "task_gradient"

        "title": {
            "english": "Linear Function Gradient Task",
            "german": "Steigung der linearen Funktion"
        }

        "description": {
            "english": "This task requires the user to determine the gradient of a linear function. The user will see a graph of the function and an input field to enter the gradient. The student only sees the graph and does not know the function. He should determine the gradient just by looking at the graph",
            "german": "Diese Aufgabe erfordert, dass der Benutzer die Steigung einer linearen Funktion bestimmt. Der Benutzer sieht einen Graphen der Funktion und ein Eingabefeld, um die Steigung einzugeben. Der Schüler sieht nur den Graphen und kennt die Funktion nicht. Er soll die Steigung allein durch Betrachten des Graphen bestimmen"
        }"""
    
    def prompt_topic_id(self, task_description, topics_lookup):
        return f"""
        Below you will receive a description of a learning task followed by a list of 
        topics. Every topic has a title, as well as a level and key_idea it is assigned to.
        Your task is to assign the described task to exactly one topic which is the best fit
        for the task. Your answer should be a json object that contain a single number which is the 
        id of the topic you choose.

        TASK_DESCRIPTION: 
        {task_description}

        TOPICS: 
        {topics_lookup}
        """

    def analyse(self, user_message,dialog, existing_tasks, templates, p5js_functions, img_path, subject):
        prompt = self.persona()+"\n"+self.prompt_analyse(user_message,dialog, existing_tasks, templates, p5js_functions, img_path, subject)
        
        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            functions=[
                {
                    "name": "create_json",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "existing_task": {
                                "type": "string"
                            },
                            "template": {
                                "type": "string"
                            },
                            "figure":{
                                "type":"boolean"
                            },
                            "existing_p5js":{
                                "type": "string"
                            },
                            "figure_details":{
                                "type":"string"
                            },
                            "figure_path":{
                                "type":"string"
                            },
                            "message":{
                                "type":"string"
                            }

                        },
                        "required": ["existing_task", "template","figure", "existing_p5js","figure_details", "figure_path"]
                    }
                }
            ],
            function_call={"name": "create_json"}
        )
        response_time = round(time.time()-start,3)

        input_token = response.usage.prompt_tokens
        output_token = response.usage.completion_tokens

        print("\n\n\n------------------------\n")
        print("ANALYSIS")
        print("   - Time: ", response_time, "s")
        print("   - Input Token: ", input_token)
        print("   - Output Token: ", output_token)
        
        print("\n------------------------\\n\n\n")
        
        obj_str = response.choices[0].message.function_call.arguments
        obj = json.loads(obj_str)
        
        print("\n\n",obj, "\n\n")
        return obj

    def generate(self, prompt):
        prompt = self.persona() + "\n" + prompt
        start = time.time()
        response = self.client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        functions=[
            {
                "name": "create_json",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message":{
                            "type":"string"
                        },  
                        "events": {
                            "type": "object"
                        },
                        "text": {
                            "type": "object"
                        },
                        "script":{
                            "type":"string"
                        },
                        "p5js":{
                            "type":"string"
                        }
                    },
                    "required": ["message", "events","text", "script"]
                }
            }
        ],
        function_call={"name": "create_json"}
        )
        response_time = round(time.time()-start,3)

        input_token = response.usage.prompt_tokens
        output_token = response.usage.completion_tokens

        print("\n\n\n------------------------\n")
        print("GENERATE")
        print("   - Time: ", response_time, "s")
        print("   - Input Token: ", input_token)
        print("   - Output Token: ", output_token)
        print("\n------------------------\\n\n\n")
    
        obj_str = response.choices[0].message.function_call.arguments
        obj = json.loads(obj_str)
        return obj
    
    def generate_description(self, task, template, dialog):
        prompt = self.prompt_description(task,template, dialog)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            functions=[
                {
                    "name": "create_json",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title":{
                                "type": "object"
                            },
                            "description":{
                                "type":"object"
                            },
                            "task_id":{
                                "type":"string"
                            }
                        },
                        "required": ["title", "description","task_id"]
                    }
                }
            ],
            function_call={"name": "create_json"}
        )
        obj_str = response.choices[0].message.function_call.arguments
        obj = json.loads(obj_str)
        return obj

    def find_topic_id(self, task_description, topics_lookup):
        prompt = self.prompt_topic_id(task_description, topics_lookup)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            functions=[
                {
                    "name": "create_json",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic_id": {
                                "type": "integer"
                            },
                        },
                        "required": ["topic_id"]
                    }
                }
            ],
            function_call={"name": "create_json"}
        )
        
        obj_str = response.choices[0].message.function_call.arguments
        obj = json.loads(obj_str)
        return obj["topic_id"]
    
# Create an instance of the conversation manager
generation_manager = GenerationManager(api_key=OPENROUTER_API_KEY)
