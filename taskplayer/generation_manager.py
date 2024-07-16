# conversation_manager.py


import os
import json
from openai import OpenAI
import time

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

EXAMPLE_TEMPLATE = """template_id: "template_multiple_choice"
        title: "Multiple Choice Template"
        description: "A template for multiple choice questions."
        events:
        send: ["choice_selected"]
        receive: ["refresh"]
        html: |
        <div class="question-container">
            <p id="question"></p>
            <div id="choices-container"></div>
        </div>
        styles: |
        .choice {
            padding: 10px;
            border: 1px solid #ccc;
            cursor: pointer;
            margin: 5px 0;
        }

        .choice.selected {
            background-color: #d3d3d3;
            border-color: #000;
        }

        .choice:hover {
            background-color: #f0f0f0;
        }
        scripts: |
        let selectedChoice = null;

        function createLayout(details) {
            const questionElement = document.getElementById('question');
            const choicesContainer = document.getElementById('choices-container');
            choicesContainer.innerHTML = '';
            const choiceElements = [];
            for (let i = 0; i < details.choices; i++) {
            const choiceElement = document.createElement('div');
            choiceElement.classList.add('choice');
            choiceElement.addEventListener('click', () => selectChoice(choiceElement, i, details.choicesData[i]));
            choicesContainer.appendChild(choiceElement);
            choiceElements.push(choiceElement);
            }
            return { questionElement, choiceElements };
        }

        function selectChoice(choiceElement, id, content) {
            if (selectedChoice) {
            selectedChoice.classList.remove('selected');
            }
            choiceElement.classList.add('selected');
            selectedChoice = choiceElement;
            playerApi.sendEvent('choice_selected', { id, content });
        }

        playerApi.callTemplateScript = (method, details) => {
            if (method === 'createLayout') {
            return createLayout(details);
            }
        };

        playerApi.receiveEvent('refresh', function() {
            selectedChoice = null;
        });"""

EXAMPLE_TASK = """task_id: "task_estimate_addition"
        template_id: "template_multiple_choice"
        title:
        english: "Estimate Addition"
        german: "Schätze Addition"
        description:
        english: "The student has to estimate the solution of an addition problem with two floating point numbers by rounding them and adding the rounded numbers together. This is a multiple choice exercise where only one choice is the correct answer."
        german: "Der Schüler muss die Lösung eines Additionsproblems mit zwei Gleitkommazahlen schätzen, indem er sie aufrundet und die gerundeten Zahlen zusammenzählt. Dies ist eine Multiple-Choice-Aufgabe, bei der nur eine Wahl die richtige Antwort ist."
        topic_id: 18
        events:
        send: ["evaluationResult", "task_details", "task_loaded"]
        receive: ["evaluate", "refresh", "get_task_details"]
        text:
            text_question:
                english: "Estimate: "
                german: "Schätze: "
            text_no_choice:
                english: "No choice selected"
                german: "Keine Auswahl getroffen"
        script: |
        let num1, num2, answer, choices;
        const NUM_CHOICES = 4;
        const { questionElement, choiceElements } = playerApi.callTemplateScript('createLayout', { choices: NUM_CHOICES, choicesData: [] });

        function generateExercise() {
            num1 = (Math.random() * 98 + 1).toFixed(2);
            num2 = (Math.random() * 98 + 1).toFixed(2);

            const correct = Math.round(num1) + Math.round(num2);
            choices = [correct];
            for (let i = 0; i < NUM_CHOICES - 1; i++) {
            let delta;
            do {
                delta = Math.floor(Math.random() * 21) - 10;
            } while (choices.includes(correct + delta));
            choices.push(correct + delta);
            }

            choices.sort((a, b) => a - b);
            answer = choices.indexOf(correct);
            questionElement.innerText = `{{text.text_question}} ${num1} + ${num2} = `;
            choices.forEach((choice, index) => {
            choiceElements[index].innerText = choice;
            choiceElements[index].onclick = () => selectChoice(index);
            });

            playerApi.sendEvent('task_loaded', {});
        }

        function selectChoice(index) {
            choiceElements.forEach((choice, i) => {
            if (i === index) {
                choice.classList.add('selected');
            } else {
                choice.classList.remove('selected');
            }
            });
            playerApi.selectedChoice = index;
        }

        function init() {
            playerApi.receiveEvent('get_task_details', function() {
            const taskDetails = playerApi.getTaskDetails();
            const dynamicDetails = `The exercise is ${num1} + ${num2}. The possible choices are: ${choices}. The correct answer is choice number ${answer + 1}, which is ${choices[answer]}.`;
            playerApi.sendEvent('task_details', {
                staticInfo: taskDetails.description,
                dynamicDetails: dynamicDetails
            });
            });

            playerApi.receiveEvent('evaluate', function() {
            const selectedChoiceElement = document.querySelector('.choice.selected');
            if (!selectedChoiceElement) {
                playerApi.sendEvent('evaluationResult', { result: '{{text.text_no_choice}}' });
                return;
            }
            const selectedId = Array.from(choiceElements).indexOf(selectedChoiceElement);
            const isCorrect = selectedId === answer;
            playerApi.sendEvent('evaluationResult', {
                selectedId,
                selectedContent: selectedChoiceElement.innerText,
                isCorrect
            });
            });

            playerApi.receiveEvent('refresh', function() {
            choiceElements.forEach(choice => choice.classList.remove('selected'));
            generateExercise();
            });
        }

        init();
        generateExercise();"""

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

class GenerationManager:
    def __init__(self, api_key, model_name='gpt-4o', api_base='https://openrouter.ai/api/v1'):
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key)
        self.model = model_name

    def persona(self):
        return """You are a helpfull AI assistant, designed to help teachers to design learning tasks
        for their students. Your job is to listen to the description and requirements of the teacher
        and create a task according to certain design rules."""
        
    def prompt_analyse(self, user_message,dialog, existing_tasks, templates, p5js_functions):
        return f""" You will receive the user's message and the complete previous dialog which includes 
        the description of the learning task that should be created. Work through the following steps and give your answer in json format.

        PREVIOUS_MESSAGE: {user_message}
        FULL_DIALOG: {dialog}

        STEP 1:
        Below you find a list of descriptions of tasks that already exists. Check all of them and decide,
        if any of those tasks matches all of the requirements of the described task. If you found a task
        that implements all features of what the user asked for, add the field "existing_task" to your
        answer and give the name of the task as value. 
        Example: 
        "existing_task": "task_gradient.yaml"
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
        "template": "template_multiple_choice.yaml"
        LIST OF TEMPLATES:
        {templates}

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

        Now give your answer in json format and only use the fields as described in the steps above. 
        """

    def prompt_generate(self, user_message,dialog, template, example_task):

        script = example_task["script"]
        text = example_task["text"]
        events = example_task["events"]
        title = example_task["title"]
        description = example_task["description"]
        task_id = example_task["task_id"]

        return f""" 
        You will receive the user's message and the complete previous dialog which includes 
        the description of the learning task that should be created. Work through the following steps and give your answer in json format.

        PREVIOUS_MESSAGE: {user_message}
        FULL_DIALOG: {dialog}

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
        "title": {title}
        "description": {description}
        "task_id": "{task_id}"

        Text elements can be referenced within the script by using double curly brackets:
        Example: answerLabel.innerHTML = "<b>{{text.text_answer}}: </b>";

        You are not supposed to handle feedback to the user. The only thing you have to take care is to handle the evaluation
        event and return an object in the format: 
        userInput: [INPUT OF THE USER]
        result: [CORRECT ANSER]
        isCorrect: [TRUE or FALSE]

        Whenever you generate random numbers in the javascript code, make sure that the variables 
        are really saved as numbers. Use functions like parseFloat or parseInt to ensure that.

        Try to implement every task in a way, that we can have multiple exercises. Fore example by
        randomly generating certain numbers or other aspects of the function. When doin this, 
        always make sure to handle the refresh event correctly and generate new random details for the
        task. Also make sure to update the correct result to ensure that the evaluate event is handled correctly.

        Always try to implement the user request as accurately as possible, but always stick to
        format given by the template and the provided examples. 
        """

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
        Always answer in english.]
        "events":[YOUR EVENTS OBJECT][Here you will creat a object that contains all outgoing and incoming events that are handled in the script]
        "text":[YOUR TEXT OBJECT][Here you will specify all texts that are used in the script. Output a object that contains english and german translations for every text element. For text that contains "you", always use the "Du" in the german translation instead of "Sie"]
        "script":"[YOUR JAVASCRIPT CODE]"[Here you will write your javascript code for the task. NEVER use comments on your javascript code!]
        "title": [YOUR TITLE OBJECT][Create a short title for the task. Output an object and add an english and german version]
        "description": [YOUR DESCRIPTION OBJECT][Create a brief description for the task.  Output an object and add an english and german version]
        "task_id": [YOUR TASK ID] [As task id use the english title, put task_ in front of it, make all characters lower case and replace all whitespaces with underscores]
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
        """

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

    def analyse(self, user_message,dialog, existing_tasks, templates, p5js_functions):
        prompt = self.persona()+"\n"+self.prompt_analyse(user_message,dialog, existing_tasks, templates, p5js_functions)
        
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
                            "message":{
                                "type":"string"
                            }

                        },
                        "required": ["existing_task", "template","figure", "existing_p5js","figure_details"]
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
                        "title":{
                            "type": "object"
                        },
                        "description":{
                            "type":"object"
                        },
                        "task_id":{
                            "type":"string"
                        },
                        "p5js":{
                            "type":"string"
                        }
                    },
                    "required": ["message", "events","text", "script","title", "description", "task_id"]
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
