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
      let text = this.buildText(task.text, language);
      let template = Handlebars.compile(JSON.stringify(task));
      let task_str = template(text)
      task_str = he.decode(task_str)
      return JSON.parse(task_str)
    }

    buildText(text_obj, language) {
      let template = {};
      for (const [key, value] of Object.entries(text_obj)) {
          if (Array.isArray(value)) {
              template[key] = value.map(item => item[language]);
          } else {
              template[key] = value[language];
          }
      }
      return template;
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
  