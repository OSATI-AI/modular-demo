  export default class TaskPlayer {
    constructor(containerId, config = {}) {
      this.container = document.getElementById(containerId);
      this.config = config;
      this.events = {};
      this.templateApi = {};
      this.playerApi = {
        sendEvent: this.sendEvent.bind(this),
        receiveEvent: this.receiveEvent.bind(this),
        callTemplateScript: this.callTemplateScript.bind(this),
        getTaskDetails: () => this.taskDetails // Added method to get task details
      };
  
      // Route events from the parent application to tasks/templates
      document.addEventListener('parentEvent', (e) => {
        this.routeEvent(e.detail.event, e.detail.data);
      });
    }


    fillText(task, language) {
      let text = task.text
      task = JSON.stringify(task)
      task = this.buildText(task, language)
      let template = Handlebars.compile(task);
      let task_str = template(text)
      task_str = he.decode(task_str)
      return JSON.parse(task_str)
    }

    buildText(text, language) {
      // Regular expression to find {{anything}} patterns
      const regex = /{{(.*?)}}/g;
    
      // Replace the patterns in the text
      return text.replace(regex, (match, p1) => {
        // Check if the content inside curly brackets already contains a dot
        if (p1.includes('.')) {
          return match; // If it contains a dot, return the match unchanged
        } else {
          return `{{${p1}.${language}}}`; // Otherwise, add the language
        }
      });
    }

    
    openTask(task, template, language ="english") {
        this.events = []
        
        console.log(task)


        try {
            // Fill text based on the selected language
            this.task = task
            this.template = template
            this.task = this.fillText(this.task, language);
    
            this.applyStyles(this.template.styles);
            this.applyStyles(this.task.styles);

            this.renderTemplate();
            this.executeTaskScript();
        } catch (error) {
            console.error('Error opening task:', error);
        }
    }
    
  
    applyStyles(styles) {
      if (styles) {
        const styleSheet = document.createElement('style');
        styleSheet.type = 'text/css';
        styleSheet.innerText = styles;
        document.head.appendChild(styleSheet);
      }
    }
  

    renderTemplate() {
      try {
        this.container.innerHTML = this.template.html;
        const playerApi = this.playerApi;
        const templateScript = new Function('playerApi', this.template.scripts);
        this.templateApi = templateScript(playerApi);
      } catch (error) {
        console.error('Error rendering template:', error);
      }
    }
  
    executeTaskScript() {
      try {
        const playerApi = this.playerApi;
        this.taskDetails = {
          description: this.task.description,
          title: this.task.title
        };
        const taskScript = new Function('playerApi', this.task.script);
        taskScript(playerApi);
      } catch (error) {
        console.error('Error executing task script:', error);
      }
    }
  
    callTemplateScript(method, details) {
      if (this.templateApi[method]) {
        return this.templateApi[method](details);
      } else {
        console.error(`Method ${method} not found in template API.`);
      }
    }
  
    sendEvent(event, data) {
      const customEvent = new CustomEvent(event, { detail: data });
      document.dispatchEvent(customEvent);
      this.routeEvent(event,data)
    }
  
    receiveEvent(event, callback) {
      if (!this.events[event]) {
        this.events[event] = [];
      }
      this.events[event].push(callback);
    }
    
    routeEvent(event, data) {
      if (this.events[event]) {
        this.events[event].forEach(callback => callback(data));
      }
    }
  }
  