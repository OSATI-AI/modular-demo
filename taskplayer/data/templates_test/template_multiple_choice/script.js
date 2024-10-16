let selectedChoice = null;
let selectedIndex = null;
let correct_index = null;

function createLayout(question_text, choices, correct) {
  // Set Question Text
  const questionElement = document.getElementById('question');
  questionElement.innerText = question_text;

  // Setup choices container 
  const choicesContainer = document.getElementById('choices-container');
  choicesContainer.innerHTML = '';

  correct_index = correct;

  // Array to hold choice elements
  const choiceElements = [];

  // Loop through the choices and create div elements for each choice
  choices.forEach((choice, i) => {
    const choiceElement = document.createElement('div');
    choiceElement.classList.add('choice');
    
    // Add choice content to the choice element
    choiceElement.appendChild(choice);

    // Add event listener for selection
    choiceElement.addEventListener('click', () => selectChoice(choiceElement, i));

    // Append the choice element to the choices container
    choicesContainer.appendChild(choiceElement);
    choiceElements.push(choiceElement);
  });
}

function selectChoice(choiceElement, id) {
  // If there is already a selected choice, remove its 'selected' class
  if (selectedChoice) {
    selectedChoice.classList.remove('selected');
  }

  // Add the 'selected' class to the clicked choice element
  choiceElement.classList.add('selected');

  // Update the selectedChoice and selectedIndex variables
  selectedChoice = choiceElement;
  selectedIndex = id;
}

function check() {
  const result = {
    user_input: selectedIndex,
    correctAnswers: correct_index,
    result: selectedIndex === correct_index
  };
  return result;
}

playerApi.callTemplateScript = (method, details) => {
  if (method === 'createLayout') {
    return createLayout(details.question_text, details.choices, details.correct);
  }
};

playerApi.receiveEvent('evaluate', function() {
  eval_result = evaluate()
  playerApi.sendEvent('evaluationResult', eval_result);
});
