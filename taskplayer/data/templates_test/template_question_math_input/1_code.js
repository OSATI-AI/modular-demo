// Global variables to store task-specific details
var num1, num2, correctAnswer;

function create_exercise() {
    // Generate two random numbers between 1 and 9
    num1 = Math.floor(Math.random() * 9) + 1;
    num2 = Math.floor(Math.random() * 9) + 1;
    
    // Calculate the correct answer
    correctAnswer = num1 + num2;
    
    // Define the question text and formula
    var questionText = '{{text_question}}';
    var formula = num1 + ' + ' + num2 + ' = \\\\placeholder[result]{}';
    
    // Define the answers object
    var answers = {
        'result': correctAnswer.toString()
    };
    
    // Call the createLayout function with the generated parameters
    var args = {
        question_text: questionText,
        formula: formula,
        answers: answers
    };
    playerApi.callTemplateScript('createLayout', args);
}

function get_task_details() {
    // Return a single string describing the current task
    return `The current task requires adding the numbers ${num1} and ${num2}, with the correct answer being ${correctAnswer}.`;
}

playerApi.receiveEvent('refresh', function() {
    generateExercise();
  });

playerApi.receiveEvent('get_task_details', function() {
const taskDetails = playerApi.getTaskDetails();
const dynamicDetails = get_task_details(); 

playerApi.sendEvent('task_details', {
    staticInfo: taskDetails.description,
    dynamicDetails: dynamicDetails
    });
});

create_exercise()