# How to Create new EXAM Questions
To use the EXAM method to evaluate retrieve-and-generate systems necessitates generating multiple choice
or true-false questions. This is a guide on how to create these questions in a format usable by the EXAM
system.

## What kind of Questions are good for EXAM?
There's several pieces or criteria that makes a good question for EXAM.
* Not open ended
* Only one answer
* Able to be answered by the retrieve-and-generated articles

### Not Open Ended
EXAM in its current form does not support free-text answers. It could be modified to support this, but
does not support it out-of-the-box. Therefore questions that cannot be constrained to multiple-choice
or true-false are not good choices.

### Only One Answer
EXAM in its current form does not support choosing any number of answers beyond one. Questions of the
format "select all that apply" should not be created. EXAM could be modified to support this, but does
not support it out-of-the-box.

### Able to be Answered by the Retrieve-and-Generated Articles
This is a little harder to define, but generally speaking, questions should not be included that the
generated articles have no way of answering. If the articles would not cover a particular topic, for example
the species of bird that Charles Darwin studied at the Galapagos Islands, no questions about finches should
be included. We have no exact way to determine what topics are or are not covered in retrieved-and-generated
articles. We leave it to the user to determine what is reasonable to include as a question topic and what
articles may or may not contain.

## What format do the questions need to be in?
EXAM originally used the [TQA dataset](https://allenai.org/data/tqa), so we require a similar format. We
lay out the format in [examples/example_question_file.json](examples/example_question_file.json)

### Example File
We have provided an example question file different from the [TQA dataset](https://allenai.org/data/tqa) 
to give a small example on how to set up a question file.

### Anatomy of a Question File
At the highest level of the JSON file is an array containing all the question set objects. Each question
set should contain at least one question though EXAM will be able to handle 0 questions in a question set.
Each question set needs an id, which is important to link articles to sets of questions. See
[Creating Articles](./createarticles.md) for more information. These question set ids should be unique.

Within the question set are individual questions. Rather than having them in an array, each question must
have its own unique id. Within the question there needs to be a list of possible answer choices, the
text of the question, and a singular correct answer. 

For additional information on any of these pieces, I recommend consulting the example in
[examples/example_question_file.json](examples/example_question_file.json)

## FAQ
### Do I need to use letters or numbers for the answer choices?
Either works, you can even mix and match if you so desire, we recommend picking one method and sticking 
to it. Our example file uses both to show you either is possible.

### How many answer choices can I give?
Technically minimum 1, but 2 or more would be highly, highly recommended (as one would be pretty useless).
While when we say things like true-false or multiple-choice, we think 2 or 4, EXAM supports 2, 3, 4, 5,
so on and so forth, as many answers as you want. If for no other reason than readability, maybe constrain
yourself to 10 or fewer answer choices, but that's up to you.

### Do the Question IDs need to be in a particular format?
No, again we recommend being consistent, but its fair game as long as they are unique. We highly recommend
that the question ids be unique across all question sets.

### Do the Question Set IDs need to be in a particular format?
No, but again we recommend being consistent. They must be unique so that each article links up to one
and only one question set.

### What labels of the JSON document are fixed?
* "globalID"
* "questions"
* "nonDiagramQuestions"
* "answerChoices"
* "beingAsked"
* "correctAnswer"
* "processedText"

### What labels of the JSON document are not fixed?
* Question Set IDs
* Question IDs
* Answer Choices

### Isn't there a better way to structure this document?
Probably, however this was intended to use the [TQA dataset](https://allenai.org/data/tqa) and as such
has its own specialized format we need to support. Feel free to ad in your own interpreter for questions
or generic approach and submit a pull request!