let numbers, correctAnswers;
const NUM_CHOICES = 8;
const { questionElement, choiceElements } = playerApi.callTemplateScript('createLayout', { choices: NUM_CHOICES, choicesData: [] });

function generateExercise() {
  playerApi.selectedChoices = [];
  numbers = generateRandomNumbers(NUM_CHOICES);
  correctAnswers = numbers.filter(isPrime);
  questionElement.innerText = `{{text_question}}`;
  numbers.forEach((number, index) => {
    choiceElements[index].querySelector('label').innerText = number;
    choiceElements[index].querySelector('input').onclick = () => selectChoice(index, number);
  });

  playerApi.sendEvent('task_loaded', {});
}

function generateRandomNumbers(count) {
  const numbers = new Set();
  while (numbers.size < count) {
    numbers.add(Math.floor(Math.random() * 100) + 1);
  }
  return Array.from(numbers);
}

function isPrime(num) {
  if (num <= 1) return false;
  for (let i = 2; i < num; i++) {
    if (num % i === 0) return false;
  }
  return true;
}

function selectChoice(index, number) {
  const checkbox = choiceElements[index].querySelector('input');
  if (checkbox.checked) {
    playerApi.selectedChoices.push(number);
  } else {
    playerApi.selectedChoices = playerApi.selectedChoices.filter(choice => choice !== number);
  }
}

function init() {
  playerApi.receiveEvent('get_task_details', function() {
    const taskDetails = playerApi.getTaskDetails();
    const dynamicDetails = `The numbers to choose from are: ${numbers}. The correct answers are: ${correctAnswers}.`;
    playerApi.sendEvent('task_details', {
      staticInfo: taskDetails.description,
      dynamicDetails: dynamicDetails
    });
  });

  playerApi.receiveEvent('evaluate', function() {
    const selectedChoices = playerApi.selectedChoices || [];
 	console.log(selectedChoices) 
   	const isCorrect = selectedChoices.every(choice => correctAnswers.includes(choice)) && selectedChoices.length === correctAnswers.length;
    playerApi.sendEvent('evaluationResult', {
      selectedChoices,
      isCorrect
    });
  });

  playerApi.receiveEvent('refresh', function() {
    choiceElements.forEach(choice => choice.querySelector('input').checked = false);
    generateExercise();
  });
}

init();
generateExercise();