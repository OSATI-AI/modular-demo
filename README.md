# Task Player Framework

## Overview

The Task Player Framework allows you to create and render arbitrary learning tasks within a web application. It consists of three main components:

1. **Templates**: Define the overall layout and behavior of different types of tasks.
2. **Tasks**: Use templates and fill them with specific content and logic.
3. **Player**: Renders tasks using templates and handles communication between the tasks and the parent application.



## Usage: 
Use Python to start a simple HTTP server.

```bash
python -m http.server 8000
```

Navigate to http://localhost:8000 in your web browser. You should see the task player in action.


## Integration
```html
<script type="module">
  import TaskPlayer from './task_player.js';

  document.addEventListener('DOMContentLoaded', () => {
    const player = new TaskPlayer('task-container');
    player.openTask('task_001');

    document.getElementById('check-btn').addEventListener('click', () => {
      player.sendEvent('evaluate');
    });

    document.addEventListener('input', (event) => {
      const typingIndicator = document.getElementById('typing-indicator');
      typingIndicator.innerText = 'typing...';
      setTimeout(() => {
        typingIndicator.innerText = '';
      }, 1000);
    });

    document.addEventListener('evaluate', (event) => {
      const evaluationResult = document.getElementById('evaluation-result');
      evaluationResult.innerText = `Evaluation Result: ${JSON.stringify(event.detail)}`;
    });
  });
</script>
```