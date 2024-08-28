function createLayout(details) {
    // Get the question element by its ID
    const questionElement = document.getElementById('question');
  
    // Get the image placeholder element by its ID (optional)
    const imagePlaceholder = document.getElementById('image_placeholder');
  
    // Get the answer element by its ID
    const answerElement = document.getElementById('answer');
  
    // Return an object containing references to the three elements
    return { questionElement, imagePlaceholder, answerElement };
  }
  
  // Override the callTemplateScript method of playerApi
  playerApi.callTemplateScript = (method, details) => {
    // Check if the method called is 'createLayout'
    if (method === 'createLayout') {
      // Call the createLayout function with the provided details
      return createLayout(details);
    }
  };
  