var num1, num2, correctAnswer;

function create_exercise() {
    num1 = Math.floor(Math.random() * 9) + 1;
    num2 = Math.floor(Math.random() * 9) + 1;
    
    correctAnswer = num1 + num2;

    var questionText = '{{text_question}}';
    var formula = num1 + ' + ' + num2 + ' = /placeholder[result]{}';
    
    var answers = {
        'result': correctAnswer.toString()
    };
    
    var args = {
        question_text: questionText,
        formula: formula,
        answers: answers
    };
    playerApi.callTemplateScript('createLayout', args);
}

function get_task_details() {
    return `The current task requires adding the numbers ${num1} and ${num2}, with the correct answer being ${correctAnswer}.`;
}

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

create_exercise()