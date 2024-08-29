let correct_answers = null 

function createLayout(question_text, formula, answers) {

  console.log("CREATE LAYOUT")
  console.log("Question Text: ", question_text)
  console.log("Formula: ", formula)
  console.log("Answers: ", answers)

    // Question
    const questionElement = document.getElementById('question');
    questionElement.innerText = question_text

    // Formula
    const mf = document.getElementById('formula');
    formula = formula.replace("/", "\\")
    console.log("Formula Replaced: ", formula)
    mf.value = formula

    // save correct answer
    correct_answers = answers
  }

  function evaluate() {
    const mf = document.getElementById('formula');
    const ce = MathfieldElement.computeEngine;
    // Initialize arrays to keep track of answers, correct answers, and results
    const answers = [];
    const correctAnswers = [];
    let allMatch = true;

    // Iterate over each key-value pair in the global correct_answers object
    for (const [key, value] of Object.entries(correct_answers)) {
        // Get the user's answer for the current key
        const answer = ce.parse(mf.getPromptValue(key));
        answers.push(answer);

        // Get the correct answer for the current key
        const correctAnswer = ce.parse(value);
        correctAnswers.push(correctAnswer);
        // Check if the user's answer matches the correct answer
        if (!answer.isSame(correctAnswer)) {
            allMatch = false;
        }
    }

    console.log({
      user_input: answers,
      correct_answer: correctAnswers,
      result: allMatch
  })


    // Return the result as an object
    return {
        user_input: answers,
        correct_answer: correctAnswers,
        result: allMatch
    };
}
  
  // Override the callTemplateScript method of playerApi
  playerApi.callTemplateScript = (method, params) => {
    // Check if the method called is 'createLayout'
    if (method === 'createLayout') {
      // Call the createLayout function with the provided details
      return createLayout(params.question_text, params.formula, params.answers);
    }
    };

  playerApi.receiveEvent('evaluate', function() {
    eval_result = evaluate()
    playerApi.sendEvent('evaluationResult', eval_result);
  });
  