# astro-homework

## Description

This package allows rapid algorithmic generation of large numbers of homework questions for the Canvas LMS. It was developed for use in astronomy courses, but the question types are mostly generalizable to any topic. It takes a JSON file (and optionally some images) to define the content of the questions. It produces a markdown file (and optionally more images) which must then be run through the text2qti package to bundle them up into a QTI-compliant file for import into a Canvas course shell.

Text2qti already supports markdown input, including embedded code to algorithmically generate questions. What this package offers is the ability to conveniently generate large numbers of questions according to a variety of different question logics, as well as the option to algorithmically generate astronomy-specific graphs.

The questions generated are grouped into banks, of which each student sees only one per assignment attempt.

The package is fully functional, but there are many more planned features.

## Authoring Questions

Here is a sample JSON file containing an assignment that consists of a single multiple choice question:

```
{
    "quiz_name": "sample assignment",
    "shuffle_answers": true,
    "questions": 
    [
        {
            "question_type": "static_multiple_choice",
            "stem": "Which of the following is a mammal??",
            "versions_requested": 3,
            "override_duplicate_stem": true,
            "static_multiple_choice":
            {
                "correct_answers": ["giraffe","monkey","buffalo","cow","tiger","dolphin"],
                "distractors": ["petunia","tuna","mushroom","potato","maple tree","sparrow","pelican","honey bee","grouse","iguana"]
            }
        }
    ]
}
```

And here are the meanings of the parameters: 

* quiz_name: The name you want the quiz to have on Canvas
* shuffle_answers: Sets the Canvas parameter that causes the order of the answers for each question to be randomized.
* questions: A JSON array, each of whose elements is a JSON object defining a single question.
* question_type: One of several possible question types defined in this package, each of which denotes question logic. "static_multiple_choice" indicates a multiple choice question whose stem and possible answers are "static", meaning that they are drawn from pre-written lists. For this question type, there is a single correct answer.
* stem: The stem for the current question. Colloquially referred to as "the question".
* versions_requested: The number of unique versions of this question you would like produced. You will receive an error message if it is not logically possible to generate the requested number of unique versions of the question, given the number of correct answers and distractors provided.
* override_duplicate_stem: The text2qti package deliberately flags questions that have the same stem, to prevent you from accidentally duplicating questions on your assignment. While this is a useful safety feature, we must bypass it to be able to generate banks of questions that all share the same stem, but different answers. So, this package checks that each instance of a generated question is different from all of the others, but allows for identical stems. To allow for identical stems, it inserts non-printing characters unique to each instance of the question.
* static_multiple_choice: A JSON object containing the actual content of the question, including correct answers and distractors.
* correct_answers: A list of strings giving all of the correct answers to the question. There can be as many as you like.
* distractors: A list of strings giving all of the distractors ("incorrect answers"). There can be as many as you like.

The above example would result in the following output, in a file called sample_assignment.md:

```
Quiz title: sample assignment
shuffle answers: true
GROUP
pick: 1
points per question: 1

1.  Which of the following is a mammal??
*a) monkey
b) petunia
c) maple tree
d) pelican
e) grouse

2.  Which of the following is a mammal??&#8202
*a) cow
b) maple tree
c) petunia
d) sparrow
e) grouse

3.  Which of the following is a mammal??&#8202&#8202
*a) cow
b) grouse
c) tuna
d) pelican
e) iguana

END_GROUP
```

This is the necessary input for the text QTI package.