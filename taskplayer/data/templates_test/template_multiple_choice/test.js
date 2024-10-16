let num1, num2, choices, answer;

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

    const texts = {
        question_text: {
            en: `What is the estimated result of adding {{num1}} and {{num2}}?`,
            de: `Was ist das geschätzte Ergebnis der Addition von {{num1}} und {{num2}}?`
        }
    };

    const question_text = texts.question_text.en.replace("{{num1}}", num1).replace("{{num2}}", num2);
    const choicesData = choices.map(choice => `<div>${choice}</div>`);
    const args = {
        question_text: question_text,
        choices: choicesData,
        correct: answer
    };

    playerApi.callTemplateScript('createLayout', args); 
}

function get_task_details() {
    return `The task is to estimate the result of adding ${num1} and ${num2}. The correct answer is ${choices[answer]}.`;
}
