# conversation_manager.py


import os
import json
from openai import OpenAI
import time

OPENROUTER_API_KEY = os.environ["OPENROUTER_API_KEY"]

EXAMPLE_P5JS = """
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
EXAMPLE_DESCRIPTION = """
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
    """

MODEL = "gpt-4o-2024-08-06"#"anthropic/claude-3.5-sonnet"#"meta-llama/llama-3.1-405b-instruct"#"gpt-4o"#"openai/gpt-4o-mini"#""#"" 

class GenerationManager:
    def __init__(self, api_key, model_name=MODEL, api_base='https://openrouter.ai/api/v1'):
        self.client = OpenAI(
            base_url=api_base,
            api_key=api_key)
        self.model = model_name

    def intro(self, user_message, dialog):
        return f"""You are a helpfull AI assistant, designed to help teachers to design learning tasks
        for their students. Your job is to listen to the description and requirements of the teacher
        and create a task according to certain design rules. You will your previous dialog with the user and 
        have to perform the described actions according to the content of the dialog.
        
        PREVIOUS_MESSAGE: {user_message}
        FULL_DIALOG: {dialog}
        """

    def check_existing_tasks(self, user_message, dialog, existing_tasks):
        # Build Prompt
        prompt = f"""
            Check the following list of task descriptions and decide, if any of those tasks matches all of the 
            requirements of the task, described by the user. If you found a task that implements all features
            exactly as the user asked for, set "existing_task" to the id of the task you have selected.
            If no task matches the requirements, set this field to null. 
            LIST OF EXISTING TASKS:
            {existing_tasks}
        """
        prompt = self.intro(user_message, dialog)+"\n"+prompt


        print("\n\n\n EXISTING TASKS: ")
        print(existing_tasks)

        # LLM call 
        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format = {
                "type": "json_schema",
                "json_schema": {
                "name": "check_existing_tasks",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "existing_task": {
                            "type": ["string", "null"]
                        },
                    },
                    "required": ["existing_task"],
                    "additionalProperties": False
                    }
                }
            }
        )
        response_time = round(time.time()-start,2)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)
        
        print("\n\n\n### CHECK EXISTING TASKS ###")
        print("  - Time: ", response_time)
        print("  - Input Tokens: ", input_tokens)
        print("  - Output Tokens: ", output_tokens)
        print("\n",obj)
        print("\n#################################\n\n\n")

        return obj

    def choose_template(self, user_message, dialog, templates):
        # Build Prompt
        prompt = f"""
            Select a template for this type of task that matches the requirements of the user.
            You are only allowed to pick exactly one template out of the provided lists of templates and their description.
            Add a field "template" to your answer and give the name of the template as value. 
            LIST OF TEMPLATES:
            {templates}
        """
        prompt = self.intro(user_message, dialog)+"\n"+prompt

        # LLM call 
        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format = {
                "type": "json_schema",
                "json_schema": {
                "name": "choose_template",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "template": {
                            "type": ["string"]
                        },
                    },
                    "required": ["template"],
                    "additionalProperties": False
                    }
                }
            }
        )
        response_time = round(time.time()-start,2)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)
        
        print("\n\n\n### CHOOSE TEMPLATE ###")
        print("  - Time: ", response_time)
        print("  - Input Tokens: ", input_tokens)
        print("  - Output Tokens: ", output_tokens)
        print("\n",obj)
        print("\n#################################\n\n\n")
        
        return obj

    def check_p5js(self, user_message, dialog, p5js_functions):
        prompt = f"""
            Analyse if the task requires to display a figure. Add a field "figure" to your answer and set its value
            to true if a figure is required and to false if no figure is required.
            A figure is only required if the user explicitly asks for it or if the context of 
            the dialog makes it clear that the task requires a figure.  

            You are only allowed to use p5js for creating figures.
            Below, there is a list of existing p5js functions with their according descriptions. Check each of them
            and decide if any of them provides a figure that matches the requirements. Add a field "existing_p5js"
            to your answers. If you found an existing function that you will use, give its filename as value, if not
            give null as value.

            Add a field "figure_details" to your answer. If there was an existing p5js function or there is no figure at all set the value of 
            the field to null. If no existing function matches the requirements, give a 
            detailed description of how the function should be designed (no code yet) as value for the field. If you describe
            how a new function should look like, I would like to create functions that are as general as possible
            in order to reuse them later. So e.g. if the user wants a figure of a linear function, instead of describing
            a p5js function that only can render linear functions, instead try to describe a function that can plot
            any kind of mathematical function. 

            LIST OF EXISTING P5JS FUNCTIONS:
            {p5js_functions}            
        """
        prompt = self.intro(user_message, dialog)+"\n"+prompt

        # LLM call 
        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format = {
                "type": "json_schema",
                "json_schema": {
                "name": "check_figure_code",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "figure":{
                            "type": "boolean"
                        },
                        "existing_p5js":{
                            "type": ["string", "null"]
                        },
                        "figure_details":{
                            "type": ["string", "null"]
                        },
                    },
                    "required": ["figure", "existing_p5js", "figure_details"],
                    "additionalProperties": False
                    }
                }
            }
        )
        response_time = round(time.time()-start,2)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)
        
        print("\n\n\n### CHECK P5JS ###")
        print("  - Time: ", response_time)
        print("  - Input Tokens: ", input_tokens)
        print("  - Output Tokens: ", output_tokens)
        print("\n",obj)
        print("\n#################################\n\n\n")
        
        return obj
    
    def generate_p5js(self, function_description):
        prompt = f"""
        Create p5js code according to render the following figure: 
        {function_description}

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
        Example Code: 
        {EXAMPLE_P5JS}

        Example Documentation: 
        {EXAMPLE_DESCRIPTION}
        
        Please also provide a documentation as shown above and add it to the field "description". 
        If your code contains multiple functions you only should provide a documentation for the main function that can be 
        called from other scripts. Provide a description of what the fuctions does as well as a short example code on how 
        to use it.
        """

        # LLM call 
        start = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            response_format = {
                "type": "json_schema",
                "json_schema": {
                "name": "create_p5js",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "p5js_code":{
                            "type": "string"
                        },
                        "description":{
                            "type": "string"
                        },
                    },
                    "required": ["p5js_code", "description"],
                    "additionalProperties": False
                    }
                }
            }
        )
        response_time = round(time.time()-start,2)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)
        
        print("\n\n\n### CREATE P5JS ###")
        print("  - Time: ", response_time)
        print("  - Input Tokens: ", input_tokens)
        print("  - Output Tokens: ", output_tokens)
        print("\n",obj)
        print("\n#################################\n\n\n")
        
        return obj

    def generate_new(self, user_message, dialog, template_documentation, subject, example, p5js_description = None):

        prompt_script = f""" 
        SCHOOL SUBJECT: {subject}

        In "script", create a javascript function "create_exercise". This function should 
        generate parameters that contain the content and correct answer of the current task.
        These parameters are then passed to a function "createLayout" which will create and
        display the task to the student. 

        The function should generate new random parameters on every call, such that the 
        learning task can be repeated with different content several times. Read out of 
        the users description if and how these new values should be generated.   
        See the function documentation below to understand how the generateLayout function
        has to be called an what parameters are required. The function must not be called 
        with a normal function call but in the following way: 

        playerApi.callTemplateScript('createLayout', args);
        
        Where args is a object containing the function parameters as key value pairs. 

        Also create a function "get_task_details" which will return a single string which describes
        the current task. This description should only contain the information that are relevant
        for the current task. So in general it should contain all the randomly generated elements 
        as well as the current correct answer. Formulate the string as a full sentence as it 
        should be used to give the current context to a LLM which can't see the task and only 
        can work with the information provided by this function.

        You are NOT allowed to create additional functions or add other commands outside of the functions.
        The only exception are global variables that need to be available in both functions.
        But their values have to be set in "create_exercise" to make sure that the value 
        changes everytime we call create_exercise again.

        In the script field only give pure javascript code without any html tags. Do not add any comments to the code. 
         
        
        FUNCTION DOCUMENTATION FOR CALLING "createLayout"
        {template_documentation}
        """
        if p5js_description:
            prompt_script += f"""
                The task requires to display a figure. You have to use an existing, external function for this.
                You can assume that the function exists in the current scope. 
                You can further assume that a div element with the id "image_placeholder" is available in the current scope.
                Call it from your script according to the the following code documentation:
                {p5js_description} """

        prompt_text = """All texts that appears in the parameters have to be  be referenced within the script
        by using double curly brackets like {{text_question}}. Every text element has to be 
        declared in an object in the "text" field in your json output and need a unique identifier
        to reference it in the javascript code. Add a english and german translation.
        """

        prompt_example = f"EXAMPLE OUTPUT:\n{example}"
 
        prompt = self.intro(user_message, dialog) + prompt_script + prompt_text + prompt_example

        start = time.time()
        response = self.client.chat.completions.create(
        model=self.model,
        messages=[{"role": "user", "content": prompt}], 
        response_format = {
                "type": "json_schema",
                "json_schema": {
                "name": "generate_task",
                #"strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "object"
                        },
                        "script":{
                            "type":"string"
                        },
                    },
                    "required": ["text", "script"],
                    "additionalProperties": False
                    }
                }
            }
        )

        response_time = round(time.time()-start,2)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)

        print("\n\n\n### CREATE TASK ###")
        print("  - Time: ", response_time)
        print("  - Input Tokens: ", input_tokens)
        print("  - Output Tokens: ", output_tokens)
        print("\n",obj)
        print("\n#################################\n\n\n")


        # Add additional fields and code

        obj["script"] += """
            playerApi.receiveEvent('refresh', function() {
                create_exercise();
            });

            playerApi.receiveEvent('get_task_details', function() {
            const taskDetails = playerApi.getTaskDetails();
            const dynamicDetails = get_task_details(); 
            playerApi.sendEvent('task_details', {
                staticInfo: taskDetails.description,
                dynamicDetails: dynamicDetails
                });
            });

            create_exercise()"""
        
        obj["events"] = {
            "send": ["task_details"],
            "receive": ["get_task_details", "refresh"]
            }

        return obj

    def generate_description(self, dialog, template_description, figure_description = None):

        # TODO Add figure description

        prompt_description = f"""
        A learning task was generated based on the descriptions of a user. Below you find the
        dialog between the user and an AI assistant that generated the task:        
        {dialog}

        For this task a predefined, general layout was used. Below you can find a description
        of the layout:
        {template_description}

        Your task is to find a title and a description for this task.

        "title": Create a short title for the task. Output an object and add an english and german version. It will be the first thing a student will see when opening the task, so make sure it is short, descriptive and informative
        "description": Create a short description for the task. The description must always be written in english. It should only contain information about what the task is about and important requirements or limitations that are stated in the dialog. 
        """
        
        prompt_example ="""" 
        EXAMPLE 1: 
        title: {
            "english": "Linear Function Gradient Task",
            "german": "Steigung der linearen Funktion"
        },
        description: "This task requires the user to determine the gradient of a linear function. The user will see a graph of the function and an input field to enter the gradient. The student only sees the graph and does not know the function. He should determine the gradient just by looking at the graph"
        
        EXAMPLE 2:
        title: {
            english: "Addition in 10 Range",
            german: "Addition im 10er Raum"
        },
        description: "In this task, the studen needs to add two numbers together. Both numbers will be between 1 and 9."
        """

        prompt = prompt_description + prompt_example

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format = {
                "type": "json_schema",
                #"strict": True,
                "json_schema": {
                "name": "create_json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title":{
                            "type": "object"
                            },
                        "description":{
                            "type":"string"
                        },
                    },
                    "required": ["title", "description"],
                    "additionalProperties": False
                    }
                }
            }
        )
        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)

        print("\n\n\nDescription: ")
        print(response)

        return obj



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

    def find_topic_id(self, task_description, topics_lookup):
        prompt = self.prompt_topic_id(task_description, topics_lookup)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            response_format = {
                "type": "json_schema",
                #"strict": True,
                "json_schema": {
                "name": "create_json",
                "schema": {
                    "type": "object",
                    "properties": {
                        "topic_id": {
                            "type": "integer"
                        },
                    },
                    "required": ["topic_id"],
                    "additionalProperties": False
                    }
                }
            }
        )

        print("\n\n\nTOPIC ID: ")
        print(response)

        obj_str = response.choices[0].message.content
        obj = json.loads(obj_str)
        return obj["topic_id"]
    
# Create an instance of the conversation manager
generation_manager = GenerationManager(api_key=OPENROUTER_API_KEY)

