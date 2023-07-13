import textwrap

def format_numeric_question(question_num,stem,correct_answer,answer_precision,image=None):

    # Compute the amount we need to indent each image file by to ensure that 
    # it lines up with the first character of the text of the stem. This is a 
    # requirement of text2qti.
    indent_string = " "*(len(str(question_num))-1)

    if image:
        formatted_multiple_choice_string = textwrap.dedent(rf"""
                {question_num}.  {stem}
                    {indent_string}![caption]({image})
                =   {correct_answer} +- {answer_precision}
                """)
    else:
        formatted_multiple_choice_string = textwrap.dedent(rf"""
                {question_num}.  {stem}
                =   {correct_answer} +- {answer_precision}
                """)

    return formatted_multiple_choice_string

def format_multiple_answer(question_num,stem,correct_answers,distractors,image=None):

    # Compute the amount we need to indent each image file by to ensure that 
    # it lines up with the first character of the text of the stem. This is a 
    # requirement of text2qti.
    indent_string = " "*(len(question_num)-1)

    correct_string = ""
    for answer in correct_answers:
        correct_string+= "[*] "+str(answer)+"\n                "

    distractors_string = ""
    for distractor in distractors:
        distractors_string+= "[] "+str(distractor)+"\n                "

    if image:
        formatted_multiple_answer_string = textwrap.dedent(rf"""
                {question_num}.  {stem}
                    {indent_string}![caption]({image})
                {correct_string}{distractors_string}""")
        # formatted_multiple_answer_string.rstrip('\n\n')
    else:
        formatted_multiple_answer_string = textwrap.dedent(rf"""
                {question_num}.  {stem}
                {correct_string}{distractors_string}""")

    return formatted_multiple_answer_string

def format_multiple_choice(question_num,stem,correct_answer,distractors,image=None):

    # Compute the amount we need to indent each image file by to ensure that 
    # it lines up with the first character of the text of the stem. This is a 
    # requirement of text2qti.
    indent_string = " "*(len(question_num)-1)
    if image:
        # For now, use an rf string, inheriting the formatting from text2qti. May need to revise this.
        formatted_multiple_choice_string = textwrap.dedent(rf"""
                    {question_num}.  {stem}
                        {indent_string}![caption]({image})
                    *a) {correct_answer}
                    b) {distractors[0]}
                    c) {distractors[1]}
                    d) {distractors[2]}
                    e) {distractors[3]}
                    """)
    else:
        formatted_multiple_choice_string = textwrap.dedent(rf"""
                    {question_num}.  {stem}
                    *a) {correct_answer}
                    b) {distractors[0]}
                    c) {distractors[1]}
                    d) {distractors[2]}
                    e) {distractors[3]}
                    """)

    return formatted_multiple_choice_string