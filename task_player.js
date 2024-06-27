  export default class TaskPlayer {
    constructor(containerId, config = {}) {
      this.container = document.getElementById(containerId);
      this.config = config;
      this.events = {};
      this.templateApi = {};
      this.playerApi = {
        sendEvent: this.sendEvent.bind(this),
        receiveEvent: this.receiveEvent.bind(this),
        callTemplateScript: this.callTemplateScript.bind(this)
      };
  
      // Route events from the parent application to tasks/templates
      document.addEventListener('parentEvent', (e) => {
        this.routeEvent(e.detail.event, e.detail.data);
      });
    }
  
    async fetchYaml(fileName) {
      try {
        const response = await fetch(`${fileName}.yaml`);
        if (!response.ok) {
          throw new Error(`Failed to load file: ${fileName}.yaml`);
        }
        const yamlText = await response.text();
        return jsyaml.load(yamlText);
      } catch (error) {
        console.error(`Error fetching YAML file ${fileName}:`, error);
        return null;
      }
    }
  
    async openTask(taskName) {
      try {
        this.task = await this.fetchYaml(taskName);
        if (!this.task) throw new Error('Invalid task YAML content.');
  
        this.template = await this.fetchYaml(this.task.template_id);
        if (!this.template) throw new Error('Invalid template YAML content.');
  
        this.renderTemplate();
        this.executeTaskScript();
      } catch (error) {
        console.error('Error opening task:', error);
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
    }
  
    receiveEvent(event, callback) {
      this.events[event] = callback;
    }
  
    routeEvent(event, data) {
      if (this.events[event]) {
        this.events[event](data);
      }
    }
  }
  