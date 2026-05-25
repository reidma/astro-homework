# astro-homework

## Description

This package allows rapid algorithmic generation of large numbers of homework questions for2 QTI compliant learning management systems (LMS) such as Canvas. It contains several specialized question types suited to astronomy courses, but most of the question types are generalizable to any subject. It takes a JSON file (and optionally some images) to define the content of the questions. It produces a markdown file (and optionally more images) which must then be run through text2qti (https://github.com/gpoore/text2qti) to convert them into a QTI-compliant file for import into an LMS.

Text2qti already supports markdown input, including certain types of algorithmically generated questions. This package greatly extends the variety of question types that can be generated algorithmically, and adds astronomy-specific graphs (transit light curves in particular).

The generated questions generated are grouped into banks, of which each student sees only one per assignment attempt.


## Installation

Clone this repository. That's it!

## Usage

Refer to comprehensive_question_set.json to see many examples of questions that can be generated. 

Run main.py on comprehensive_question_set.json, which should produce a copy of the included file Comprehensive_Question_Set.md.

Install text2qti from its repo (linked above) and run 

```text2qti Comprehensive_Question_Set.md```

This will generate a .zip file in QTI format, suitable for upload to your LMS.