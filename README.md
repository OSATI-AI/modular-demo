# Modular Task Player Framework

## Overview

The Task Player Framework allows you to create and render arbitrary learning tasks within a web application. The framework consists of three main components:

1. **Templates**: Define the structure and layout of different types of tasks.
2. **Tasks**: Provide the content and logic for specific tasks, using templates.
3. **Player**: Renders tasks using templates and handles communication between the tasks and the parent application via an event system.

## Templates

Templates define the overall layout and behavior of tasks. They are responsible for creating the structure and returning references to the elements that the tasks will fill with content.

### Example:
```yaml
template_id: "template_example"
title: "Example Template"
description: "A template with a question and multiple choice options."
events:
  send: ["choice_selected"]  # Events that this template can send
  receive: []  # Events that this template can receive
html: |
  <div class="question-container">
    <p id="question"></p>  # Placeholder for the question
    <div id="choices-container"></div>  # Placeholder for the choices
  </div>
scripts: |
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
  ```

## Tasks
Tasks use templates and fill them with specific content and logic. They define the content to be displayed and handle the task-specific logic, such as evaluating user input.

### Example
```yaml
task_id: "task_example"
template_id: "template_example"
title: "Example Task"
description: "A task that asks a multiple choice question."
events:
  send: ["evaluationResult"]  # Events that this task can send
  receive: ["evaluate"]  # Events that this task can receive
script: |
  const questionText = "What is the capital of France?";
  const choices = [
    { text: "Berlin", value: "Berlin" },
    { text: "Madrid", value: "Madrid" },
    { text: "Paris", value: "Paris" },
    { text: "Rome", value: "Rome" }
  ];
  const correctAnswerId = 2;  # Index of the correct answer

  const { questionElement, choiceElements } = playerApi.callTemplateScript('createLayout', {
    choices: choices.length,
    choicesData: choices
  });

  questionElement.innerText = questionText;

  choices.forEach((choice, index) => {
    choiceElements[index].innerText = choice.text;
    choiceElements[index].dataset.choice = choice.value;
  });

  playerApi.receiveEvent('evaluate', function() {
    const selectedChoiceElement = document.querySelector('.choice.selected');
    if (!selectedChoiceElement) {
      playerApi.sendEvent('evaluationResult', { result: 'No choice selected' });
      return;
    }
    const selectedId = Array.from(choiceElements).indexOf(selectedChoiceElement);
    const isCorrect = selectedId === correctAnswerId;
    playerApi.sendEvent('evaluationResult', {
      selectedId,
      selectedContent: selectedChoiceElement.innerText,
      isCorrect
    });
  });
```

## External scripts
Tasks and templates can have a **external_scripts** field that can contain a list of filenames. The scripts are loaded dynamically when this task is loaded and all functions inside this file can then be called from the template or task script. 

### Example
```yaml
task_id: "task_003"
template_id: "template_figure_question_answer"
title: "Linear Function Gradient Task"
description: "Determine the gradient of a linear function."
topic_id: 1
events:
  send: ["evaluationResult"]
  receive: ["evaluate", "refresh"]
external_scripts:
  - "figure.js"
...
```



## Communication
The framework uses an event system to facilitate communication between the parent application and the tasks/templates.

### Sending Events from the Parent Application
To send an event to a task or template, the parent application dispatches a custom event. The task or template listens for these events and handles them accordingly.

### Receiving Events from Tasks/Templates
Tasks and templates can send events to the parent application using the playerApi.sendEvent method. The parent application can subscribe to these events to handle them.

### Specifying Events
Tasks and templates specify the events they can send and receive in their YAML definitions under the events field.

## Integration
To integrate the player into a web application, follow these steps:
```html
<!-- Importing the YAML parser library -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-yaml/3.14.0/js-yaml.min.js"></script>
<!-- Importing the task player script -->
<script type="module">
  import TaskPlayer from './task_player.js';

  document.addEventListener('DOMContentLoaded', () => {
    const player = new TaskPlayer('task-container');
    player.openTask('task_multiple_choice');

    document.getElementById('check-btn').addEventListener('click', () => {
      const customEvent = new CustomEvent('parentEvent', {
        detail: { event: 'evaluate' }
      });
      document.dispatchEvent(customEvent);
    });

    document.addEventListener('input', (event) => {
      const typingIndicator = document.getElementById('typing-indicator');
      typingIndicator.innerText = 'typing...';
      setTimeout(() => {
        typingIndicator.innerText = '';
      }, 1000);
    });

    document.addEventListener('choice_selected', (event) => {
      const typingIndicator = document.getElementById('typing-indicator');
      typingIndicator.innerText = `Selected Choice: ID - ${event.detail.id}, Content - ${event.detail.content}`;
    });

    document.addEventListener('evaluationResult', (event) => {
      const evaluationResult = document.getElementById('evaluation-result');
      evaluationResult.innerText = `Evaluation Result: ${JSON.stringify(event.detail)}`;
    });
  });
</script>
```

## Django Example
The Django application is just an example to demonstrate how the task player can be integrated into any web application. The same principles can be applied to other frameworks or standalone applications.

Here, the tasks and templates are loaded in the backend (since they probably would be stored in a databse) and send to the frontend via a http request. External scripts, Styling and the Task-Player itself are included in the frontend as static files. 

### Start the app as local deployment:
1. Install Django
```bash
  pip install django
```
2. Navigate to the project root directory and execute:
```bash
  python manage.py runserver
```
