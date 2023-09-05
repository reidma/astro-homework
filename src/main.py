from io import TextIOWrapper
import json
import sys
from question_types import static_multiple_choice, ordered_multiple_choice, ranked_list_multiple_choice, identify_incorrect_pairing, numeric_question, multiple_answer, single_transit_graph
from utilities import write_questions_to_file

def generate_questions():

    if len(sys.argv) != 3:
        print("Usage: python3 main.py <input json file> <output path>")
        sys.exit(1)


    # Read in the JSON file that contains the description of the quiz.
    quiz_description_file = open(sys.argv[1])
    quiz_data_from_file = json.load(quiz_description_file)
    quiz_description_file.close()
    # print(quiz_data_from_file)

    output_path= sys.argv[2]
    output_image_path = output_path + 'images/'

    markdown_output_file: TextIOWrapper = open(str(quiz_data_from_file['quiz_name']).replace(' ', '_') + ".md", "w")
    quiz_title = 'Quiz title: '+ str(quiz_data_from_file['quiz_name']+ '\n')
    markdown_output_file.write(quiz_title)
    if quiz_data_from_file['shuffle_answers']:
        markdown_output_file.write('shuffle answers: true')

    # Parse the JSON tree, generating questions as it specifies:
    question_list = quiz_data_from_file['questions']
    for question in question_list:
        if question['question_type'] == 'static_multiple_choice':
            new_questions = static_multiple_choice(question['stem'],question['versions_requested'],question['override_duplicate_stem'],\
                question['static_multiple_choice']['correct_answers'],question['static_multiple_choice']['distractors'],question.get('image'))
        elif question['question_type'] == 'ordered_multiple_choice':
            new_questions = ordered_multiple_choice(question['stem'],question['versions_requested'],question['override_duplicate_stem'],\
                question['ordered_multiple_choice']['parameters'],question['ordered_multiple_choice']['correct_answers'],question['ordered_multiple_choice']['distractors'],question.get('image'))
        elif question['question_type'] == 'ranked_list_multiple_choice':
            new_questions = ranked_list_multiple_choice(question['stem'],question['versions_requested'],question['override_duplicate_stem'],question['ranked_list_multiple_choice']['ranked_list'],question['ranked_list_multiple_choice']['answer_list_length'],question['ranked_list_multiple_choice']['num_correct'],question['ranked_list_multiple_choice']['force_multiple_choice'],question.get('image'))
        elif question['question_type'] == 'identify_incorrect_pairing':
            new_questions = identify_incorrect_pairing(question['stem'],question['versions_requested'],question['override_duplicate_stem'],\
                question['identify_incorrect_pairing']['pairs'],question['identify_incorrect_pairing']['num_incorrect'],question['identify_incorrect_pairing']['force_multiple_choice'],question.get('image'))
        elif question['question_type'] == 'numeric_question':
            new_questions = numeric_question(question['stem'],question['versions_requested'],question['override_duplicate_stem'],\
                question['numeric_question']['formula'],question['numeric_question']['parameters'],question['numeric_question']['percent_precision'],question.get('image'))
        elif question['question_type'] == 'multiple_answer':
            new_questions = multiple_answer(question['stem'],question['versions_requested'],question['override_duplicate_stem'],\
                question['multiple_answer']['correct_answers'],question['multiple_answer']['distractors'],question['multiple_answer']['number_correct_options_desired'],\
                question.get('image'))
        elif question['question_type'] == 'single_transit_graph':        
            new_questions = single_transit_graph(question['stem'],question['versions_requested'],question['override_duplicate_stem'],\
                question['single_transit_graph']['planet_parameters'],question['single_transit_graph']['graph_parameters'],question['single_transit_graph']['zoom_level'],output_image_path,\
                question['single_transit_graph'].get('focus_parameter'),question['single_transit_graph'].get('distractor_multipliers'))
        else:
            raise Exception('Unrecognized question type')
        
        # Determine whether more than one version of a given question has been
        # requested and therefore whether we need to make a question group
        
        if question['versions_requested'] > 1:
            markdown_output_file.write("\nGROUP\npick: 1\npoints per question: 1\n")
            
        # Write out the last generated questions
        write_questions_to_file(markdown_output_file,new_questions)

        if question['versions_requested'] > 1:
            markdown_output_file.write("\nEND_GROUP\n")
    markdown_output_file.close()

    








generate_questions() 