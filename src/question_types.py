import random
import math
import re
import os
import hashlib
from formatting import format_multiple_choice, format_numeric_question, format_multiple_answer
from utilities import add_blank_characters, correct_articles, round_sigfigs, select_random_items_from_list
from make_graphs import generate_transit_graph

def multiple_answer(stem,num_questions_desired,override_duplicate_stem,correct_options,incorrect_options,number_correct_options_desired,image=None):
    '''This is a traditional multiple-answer question. It takes a static stem and more than one correct answer.
    '''

    # Check to ensure that the user has requested that at least two options be correct.
    # Otherwise, students will be confused because the question will be marked as multiple-answer
    # but there will be only one correct answer.
    if (number_correct_options_desired < 2) or (number_correct_options_desired > 4):
        raise Exception('For a multiple answer question, number_correct_options_desired must be more than 1 and less than 5')

    # A list to keep track of sets of answers previously used so we don't duplicate them
    previous_answer_sets = []

    # A list that keeps track of all of the unique questions generated. The length of this list
    # Is used to decide when we are done generating questions.
    unique_questions_generated = []

    # Calculate the number of possible versions of this question
    unique_answer_sets = math.comb(len(correct_options),number_correct_options_desired)*math.comb(len(incorrect_options),(5-number_correct_options_desired))
    if unique_answer_sets < num_questions_desired:
        raise Exception('number of desired questions not possible given number of distractors and solutions')

    # Generate the requested number of versions of this question 
    while len(unique_questions_generated) < num_questions_desired:
        # Select the correct answer randomly from among the correct options
        correct_answers = random.sample(correct_options,number_correct_options_desired)

        # Select the distractors randomly from among the incorrect answers
        distractors = random.sample(incorrect_options,(5-number_correct_options_desired))
        
        # Produce a list of all of the answers used for this version of the question and 
        # sort them so that they can be compared to previously generated sets
        new_set = correct_answers + distractors
        new_set.sort()

        # If this version of the question isn't a duplicate, use it
        if new_set not in previous_answer_sets:
        
            # Override stem deduplication if specified in JSON file
            if override_duplicate_stem:
                stem_with_blanks = add_blank_characters(stem,len(unique_questions_generated))
            else:
                stem_with_blanks = stem
            
            previous_answer_sets.append(new_set)
            unique_questions_generated.append(format_multiple_answer(\
                str(len(unique_questions_generated)+1),stem_with_blanks,correct_answers,distractors,image))
            #print(unique_questions_generated)
    return unique_questions_generated

def static_multiple_choice(stem,num_questions_desired,override_duplicate_stem,correct_options,incorrect_options,image=None):

    # This question type is a traditional multiple choice: a static stem with one correct answer and four distractors.
    # Answers are randomly chosen from user-provided lists of strings. If there is only one possible correct answer, 
    #there need to be a large number of distractors to be able to generate a sufficient number of random variations of the question.

    # A list to keep track of sets of answers previously used so we don't duplicate them
    previous_answer_sets = []

    # A list that keeps track of all of the unique questions generated. The length of this list
    # Is used to decide when we are done generating questions.
    unique_questions_generated = []

    # Calculate the number of possible versions of this question
    unique_answer_sets = len(correct_options)*math.comb(len(incorrect_options),4)
    if unique_answer_sets < num_questions_desired:
        raise Exception('number of desired questions not possible given number of distractors and solutions')

    # Generate the requested number of versions of this question 
    while len(unique_questions_generated) < num_questions_desired:
        # Select the distractors randomly from among the incorrect answers
        distractors = random.sample(incorrect_options,4)
        # Select the correct answer randomly from among the correct options
        correct_answer = [random.choice(correct_options)]

        # Produce a list of all of the answers used for this version of the question and 
        # sort them so that they can be compared to previously generated sets
        new_set = correct_answer + distractors
        new_set.sort()

        # If this version of the question isn't a duplicate, use it
        if new_set not in previous_answer_sets:

            # Override stem deduplication if specified in JSON file
            if override_duplicate_stem:
                stem_with_blanks = add_blank_characters(stem,len(unique_questions_generated))
            else:
                stem_with_blanks = stem

            previous_answer_sets.append(new_set)
            unique_questions_generated.append(format_multiple_choice(\
                str(len(unique_questions_generated)+1),stem_with_blanks,correct_answer[0],distractors,image))
            #print(unique_questions_generated)
    return unique_questions_generated

def ordered_multiple_choice(stem,num_questions_desired,override_duplicate_stem,parameters,correct_options,incorrect_options,image=None):
    '''A multiple choice question in which there are variables in either or both of the stem and 
    the answers. Technically, this is a superset of static multiple choice questions, and could be 
    used as such, but I am keeping them separate to ensure that authoring static questions is as 
    straightforward as possible. In this case, the parameter list provided is assumed to be
    sequential. The variable names early_parameter and late_parameter will be automatically substituted
    in both the stem and the answers with a correctly sequenced pair of the parameters'''
    
    # A list to keep track of sets of answers previously used so we don't duplicate them
    previous_answer_sets = []

    # A list that keeps track of all of the unique questions generated. The length of this list
    # Is used to decide when we are done generating questions.
    unique_questions_generated = []

    # Calculate the number of possible versions of this question
    '''This is a bit tricky to do, because it depends on how many instances of the parameters appear 
    throughout the possible answers, and therefore how many versions of them could be produced. 
    For now, set it to the number that could be produced with a stem containing two variables 
    and answers containing none. '''
    unique_answer_sets = len(correct_options)*math.comb(len(incorrect_options),4)*math.comb(len(parameters),2)

    # print(num_questions_desired,unique_answer_sets)
    # print(len(correct_options))
    # print(math.comb(len(incorrect_options),4))
    # print(math.comb(len(parameters),2))

    if unique_answer_sets < num_questions_desired:
        raise Exception('number of desired questions not possible given number of distractors and solutions')

    # Generate the requested number of versions of this question 
    while len(unique_questions_generated) < num_questions_desired:

        # Select the parameters we will use
        parameter_indices = [i for i in range(0,len(parameters))]
        chosen_parameters = sorted(random.sample(parameter_indices,2))
        # print(chosen_parameters)
        early_parameter = parameters[chosen_parameters[0]]
        # print(early_parameter)
        late_parameter = parameters[chosen_parameters[1]]
        # print(late_parameter)
        
        # Select the distractors randomly from among the incorrect answers
        distractors = random.sample(incorrect_options,4)
        # Select the correct answer randomly from among the correct options
        correct_answer = [random.choice(correct_options)]

        # Go through and replace any instances of early_parameter and late_parameter 
        # in the stem and all of the answers. Correct article mismatches as you go.
        
        subbed_stem = correct_articles(stem,"early_parameter",early_parameter)
        subbed_stem = correct_articles(subbed_stem,"late_parameter",late_parameter)
        
        subbed_correct_answer = [correct_articles(answer,"early_parameter",early_parameter) for answer in correct_answer]
        subbed_correct_answer = [correct_articles(answer,"late_parameter",late_parameter) for answer in subbed_correct_answer]

        subbed_distractors = [correct_articles(distractor,"early_parameter",early_parameter) for distractor in distractors]
        subbed_distractors = [correct_articles(distractor,"late_parameter",late_parameter) for distractor in subbed_distractors]


        # Produce a list of all of the answers used for this version of the question and 
        # sort them so that they can be compared to previously generated sets
        new_set = subbed_correct_answer + subbed_distractors
        new_set.sort()

        # If this version of the question isn't a duplicate, use it
        if new_set not in previous_answer_sets:

            # Override stem deduplication if specified in JSON file
            if override_duplicate_stem:
                stem_with_blanks = add_blank_characters(subbed_stem,len(unique_questions_generated))
            else:
                stem_with_blanks = stem

            previous_answer_sets.append(new_set)
            unique_questions_generated.append(format_multiple_choice(\
                str(len(unique_questions_generated)+1),stem_with_blanks,subbed_correct_answer[0],subbed_distractors,image))
            #print(unique_questions_generated)
    return unique_questions_generated

def ranked_list_multiple_choice(stem,num_questions_desired,override_duplicate_stem,ranked_list,list_length,num_correct,force_multiple_choice,image=None):
    '''A multiple choice question in which the goal is to determine which answer(s) correctly rank(s)
    a set of options. The author supplies a list of correctly ranked items
    and from those we generate lists of incorrectly ranked items.'''
    
    # A list to keep track of sets of answers previously used so we don't duplicate them
    previous_answer_sets = []

    # A list that keeps track of all of the unique questions generated. The length of this list
    # Is used to decide when we are done generating questions.
    unique_questions_generated = []

    # Calculate the number of possible versions of this question
    unique_correct_answers = math.comb(len(ranked_list),list_length)
    unique_incorrect_answers = math.perm(len(ranked_list),list_length) - unique_correct_answers
    unique_answer_sets = unique_correct_answers*math.comb(unique_incorrect_answers,4)

    # print(num_questions_desired,unique_answer_sets)
    # print(len(correct_options))
    # print(math.comb(len(incorrect_options),4))
    # print(math.comb(len(parameters),2))

    if unique_answer_sets < num_questions_desired:
        raise Exception('number of desired questions not possible given list length for this ranked list question')

    # Generate the requested number of versions of this question 
    while len(unique_questions_generated) < num_questions_desired:

        # Initialize the list we will use to ensure that there are no duplicate options
        # in this instance of a multiple choice question.
        used_answers = []
        distractors = []
        correct_answers = []

        while len(correct_answers) < num_correct:
            # Construct the list that will be the correct answer
            correct_list_indices = random.sample(range(len(ranked_list)),list_length)
            correct_list_indices.sort()
            # print(ranked_list[0])
            # print(correct_list_indices)
            correct_answer = [ranked_list[correct_list_index] for correct_list_index in correct_list_indices]
            correct_answer_string = ', '.join(str(answer) for answer in correct_answer)
            # Add this answer to the list of options being used for this question. 
            # This allows us to make sure that none of the distractors accidentally duplicates 
            # a correct answer.
            if correct_answer_string not in used_answers:
                correct_answers.append(correct_answer_string)
                used_answers.append(correct_answer_string)
        
        # Generate the distractors, ensuring that each is unique
        while len(distractors) < (5 - num_correct):
            distractor_indices = random.sample(range(len(ranked_list)),list_length)
            # Ensure that the distractor_indices are not in the correct order by putting them in the
            # correct order, then shuffling them and comparing to the original order:
            distractor_indices.sort()
            shuffled_indices = distractor_indices[:]
            #print('shuffled_indices ',shuffled_indices)
            while (shuffled_indices == distractor_indices):
                random.shuffle(shuffled_indices)
            distractor_indices = shuffled_indices[:]
            #print('distractor_indices ',distractor_indices)

            distractor_candidate = [ranked_list[distractor_list_index] for distractor_list_index in distractor_indices]
            #print('distractor candidate ',distractor_candidate)
            distractor_candidate_string = ', '.join(str(answer) for answer in distractor_candidate)
            #print('distractor candidate string ',distractor_candidate_string)
            #print('used answers ',used_answers)
            if distractor_candidate_string not in used_answers:
                distractors.append(distractor_candidate_string)
                used_answers.append(distractor_candidate_string)
       
        used_answers.sort()
        
        # If this version of the question isn't a duplicate, use it
        if used_answers not in previous_answer_sets:

            # Override stem deduplication if specified in JSON file
            if override_duplicate_stem:
                stem_with_blanks = add_blank_characters(stem,len(unique_questions_generated))
            else:
                stem_with_blanks = stem

            previous_answer_sets.append(used_answers)

            # Give the user the option to force multiple choice formatting, in the case where there is only one correct answer

            if force_multiple_choice and (num_correct != 1):
                raise Exception('You may not force multiple choice formatting when there is more than one correct answer')

            if force_multiple_choice and (num_correct == 1):
                unique_questions_generated.append(format_multiple_choice(str(len(unique_questions_generated)+1),\
                    stem_with_blanks,correct_answers[0],distractors,image))
            else: 
                unique_questions_generated.append(format_multiple_answer(str(len(unique_questions_generated)+1),stem_with_blanks,correct_answers,distractors,image))
            
    return unique_questions_generated  

def multiple_choice_matching(stem,num_questions_desired,override_duplicate_stem,pairs,num_correct,answer_match_or_mismatch,force_multiple_choice,image=None):

    # Given a list of pairs of items, choose the ones that either do or do not match.
    # For example, each pair could consist of a geologic eon and an event 
    # supposed to have occurred during that eon. Students pick the one that is an incorrect 
    # pairing. Whether the correct answer is a match or a mismatch must be specified.

    # A list to keep track of sets of answers previously used so we don't duplicate them
    previous_answer_sets = []

    # A list that keeps track of all of the unique questions generated. The length of this list
    # Is used to decide when we are done generating questions.
    unique_questions_generated = []

    # Calculate the number of possible versions of this question
    unique_matches = 0
    unique_mismatches = 0
    for key in pairs:
        '''In the case that we allow for multiple correct answers, the number of unique questions
        that can be generated is the number of possible correct pairings choose the number of desired correct pairings,
        times the number of possible incorrect pairings choose the number of desired incorrect pairings.'''

        # The number of possible matches is simply equal to the total number of entries in the pairs dict, 
        # because that dict contains only correct pairings
        unique_matches += len(pairs[key])
        
        # For each key, calculate all of the possible incorrect pairings by summing up all the ways this key
        # can be paired with entries from other keys, which are not correct matches.
        pairs_without_this_key = pairs.copy()
        pairs_without_this_key.pop(key)
        for non_matching_key in pairs_without_this_key:
            unique_mismatches += len(pairs_without_this_key[non_matching_key])
        
    # The total possible number of unique sets of answers is equal to the number of matches
    # times the total number of possible mismatches.
    if answer_match_or_mismatch == "match":
        total_possible_answer_combinations = math.comb(unique_matches,num_correct)*math.comb(unique_mismatches,(5 - num_correct))
    elif answer_match_or_mismatch == "mismatch":
        total_possible_answer_combinations = math.comb(unique_mismatches,num_correct)*math.comb(unique_matches,(5 - num_correct))
        
    if total_possible_answer_combinations < num_questions_desired:
        raise Exception('number of desired questions not possible given number of possible combinations of distractors and solutions')

    # Generate the requested number of versions of this question
    while len(unique_questions_generated) < num_questions_desired:
        
        correct_answers = [] # Compile the correct answers
        distractors = [] # Compile the distractors for this instance of the question
        used_answers = [] # Compile all sets of answers used, including both distractors and the correct answer
        matches = [] # Compile the matches for this instance of the question
        mismatches = [] # Compile the mismatches for this instance of the question

        # Determine the number of matches and mismatches needed
        if answer_match_or_mismatch == "match":
            matches_needed = num_correct
            mismatches_needed = 5 - num_correct
        elif answer_match_or_mismatch == "mismatch":
            matches_needed = 5 - num_correct
            mismatches_needed = num_correct
        else:
            raise Exception('Could not calculate necessary number of matches and mismatches for multiple choice matching question. Check JSON file.')
        
        print("Matches,mismatches ",matches_needed,mismatches_needed)
        # Choose the key that will form the basis for the mismatched pair, which will be the correct answer:
        # random_mismatch_key = random.choice(list(pairs.keys()))

        # Choose the pairs of keys and values that will form the basis for the mismatched pairs
        while len(mismatches) < mismatches_needed:
            # Choose the key that will form the basis for the mismatched pair
            random_mismatch_key_part1 = random.choice(list(pairs.keys()))
            # Now choose a new key that doesn't match the previous one, thereby guaranteeing that we get a mismatched pair
            pairs_only_mismatches = pairs.copy()
            pairs_only_mismatches.pop(random_mismatch_key_part1)
            random_mismatch_key_part2 = random.choice(list(pairs_only_mismatches.keys()))

            candidate_mismatch = [random_mismatch_key_part1,random.choice(pairs_only_mismatches[random_mismatch_key_part2])]
            if candidate_mismatch not in used_answers:
                mismatches.append(candidate_mismatch)
                used_answers.append(candidate_mismatch)

        # Now generate the necessary number of matches. The pairings are chosen randomly, so for each pairing, check that 
        # it hasn't been used before in this question.
        while len(matches) < (matches_needed):
            random_key = random.choice(list(pairs.keys()))
            match_candidate = [random_key,random.choice(pairs[random_key])]
            if match_candidate not in used_answers:
                matches.append(match_candidate)
                used_answers.append(match_candidate)

        used_answers.sort()
    
        # If set of answers aren't a duplicate of a previous version of the question, then use them.
        if used_answers not in previous_answer_sets:

            if answer_match_or_mismatch == "match":
                correct_answers = matches
                distractors = mismatches
            elif answer_match_or_mismatch == "mismatch":
                correct_answers = mismatches
                distractors = matches

            # Override stem deduplication if specified in JSON file
            if override_duplicate_stem:
                stem_with_blanks = add_blank_characters(stem,len(unique_questions_generated))
                #print(stem,len(unique_questions_generated))
            else:
                stem_with_blanks = stem
            
            correct_answer_strings = []
            for k in range(0,num_correct):
                correct_answer_strings.append(str(correct_answers[k][0])+', '+str(correct_answers[k][1]))

            distractor_strings = []
            for j in range(0,(5-num_correct)):
                distractor_strings.append(str(distractors[j][0])+', '+str(distractors[j][1]))
            
            # Give the user the option to force multiple choice formatting, in the case where there is only one correct answer

            if force_multiple_choice and (num_correct != 1):
                raise Exception('You may not force multiple choice formatting when there is more than one correct answer')

            if force_multiple_choice and (num_correct == 1):
                unique_questions_generated.append(format_multiple_choice(str(len(unique_questions_generated)+1),\
                    stem_with_blanks,correct_answer_strings[0],distractor_strings,image))
            else: 
                unique_questions_generated.append(format_multiple_answer(str(len(unique_questions_generated)+1),\
                    stem_with_blanks,correct_answer_strings,distractor_strings,image))              

            # Having chosen all the options for this instance of the question,
            # keep a copy of the ones that were used so we can compare the answers 
            # chosen for subsequent instances and ensure no duplication.
            previous_answer_sets.append(sorted(used_answers))

    return unique_questions_generated

def numeric_question(stem,num_questions_desired,override_duplicate_stem,formula,input_parameters,percent_precision,image=None):
    """Note that there is a limitation of Canvas in that the answer to a numerical question 
    must be larger than 1E-4. All values lower than that will be interpreted as zero. So, 
    ensure that appropriate units are chosen such that the answer is larger than 1E-4 and 
    that students are given necessary instructions about how to express their answers."""
    # print(stem,correct_answer,parameters,num_questions_desired)
    unique_questions_generated = []

    # Generate the requested number of versions of this question
    while len(unique_questions_generated) < num_questions_desired:    
        # correct_answer = 
        #print(input_parameters)
        # par = []

        # Generate the random parameters for this instance of the question
        par = [round(random.randint(input_parameters[0][i], input_parameters[1][i])) 
       if isinstance(input_parameters[0][i], int) and isinstance(input_parameters[1][i], int)
       else round_sigfigs(random.uniform(input_parameters[0][i], input_parameters[1][i]), 3)
       for i in range(len(input_parameters[0]))]
        #par = [round_sigfigs(random.uniform(input_parameters[0][i],input_parameters[1][i]),3) for i in range(0,len(input_parameters[0]))]
        #par = [round(random.uniform(input_parameters[0][i],input_parameters[1][i])) for i in range(0,len(input_parameters[0]))]
        # print(par)
        # print(random.uniform(input_parameters[0][0],input_parameters[1][0]))

        # Now generate the stem that matches these parameters:
        revised_stem = stem
        for j in range(0,len(par)):
            parameter_name = "par"+str(j)
            revised_stem  = re.sub(parameter_name,str(par[j]),revised_stem)
            # print(revised_stem)
        # Calculate the correct answer based on the formula supplied in the JSON file
        # correct_answer = par[0]+par[1]
        # print(par,formula)
        correct_answer = round_sigfigs(eval(formula),3)
        answer_precision = correct_answer*percent_precision/100.0
        #print(correct_answer,answer_precision)
        unique_questions_generated.append(format_numeric_question((len(unique_questions_generated)+1),\
            revised_stem,correct_answer,answer_precision,image))

    return unique_questions_generated

def single_transit_graph(stem,num_questions_desired,override_duplicate_stem,planet_parameters,graph_parameters,zoom_level,output_image_path,focus_parameter=None,distractor_multipliers=None):

    # Define standard answers:
    standard_answers = ["A","B","C","D","E"]

    # A list to keep track of sets of answers previously used so we don't duplicate them
    previous_answer_sets = []

    # Similarly, to support cases where both the stem and the answers are identical from question to question,
    # check that no two sets of planet parameters are the same. This is exceptionally unlikely, but we can check.
    previous_planet_parameters = []

    # A list that keeps track of all of the unique questions generated. The length of this list
    # Is used to decide when we are done generating questions.
    unique_questions_generated = []

    # Calculate the number of possible versions of this question
    #    unique_answer_sets = len(correct_options)*math.comb(len(incorrect_options),4)
    #    if unique_answer_sets < num_questions_desired:
    #        raise Exception('number of desired questions not possible given number of distractors and solutions')

    # Generate the requested number of versions of this question 
    while len(unique_questions_generated) < num_questions_desired:

        # Shuffle the order of the planets provided so that the correct one is no longer first.
        # Record the new position of the correct planet.

        original_planet_parameters = planet_parameters
        original_planet_indices = list(range(len(planet_parameters)))
        random.shuffle(original_planet_indices)
        planet_parameters = [planet_parameters[i] for i in original_planet_indices]
        

        '''The user supplies a set of planet parameter ranges which define the bounds within which 
        individual questions will be generated. As we generate each question, we have to choose consistent 
        fixed parameters defining a specific planet. So we go through the list of planet parameters provided
        and, if a range is provided, than we choose a specific value for this instance of the question.'''
        fixed_planet_parameters = [dict() for x in range(len(planet_parameters))]
        # print("Fixed planet parameters:\n", fixed_planet_parameters)
        for i in range(len(planet_parameters)):
            # print(planet_parameters[i])
            for planet_parameter_key in planet_parameters[i]:
                if type(planet_parameters[i][planet_parameter_key]) is list:
                    fixed_planet_parameters[i][planet_parameter_key] = random.uniform(planet_parameters[i][planet_parameter_key][0],planet_parameters[i][planet_parameter_key][1])
                else:
                    fixed_planet_parameters[i][planet_parameter_key] = planet_parameters[i][planet_parameter_key]
        #print("\n\n Fixed planet parameters:\n", fixed_planet_parameters)
        # print('----- NEW QUESTION ----')
        # print('Fixed planet parameters:')
        # print(fixed_planet_parameters)
        fixed_graph_parameters = {}
        for graph_parameter_key in graph_parameters:
            if type(graph_parameters[graph_parameter_key]) is list:
                fixed_graph_parameters[graph_parameter_key] = random.uniform(graph_parameters[graph_parameter_key][0],graph_parameters[graph_parameter_key][1])
            else:
                fixed_graph_parameters[graph_parameter_key] = graph_parameters[graph_parameter_key]

        # Generate the image file name based on hashing the stem for the question.
        # This should ensure that each question gets its own string and that no two questions get the same string.
        image_string = hashlib.md5(stem.encode()).hexdigest()
        
        correct_answer = []
        distractors = []
        # Choose the correct option depending on the focus parameter
        if focus_parameter == "num_planets":
            number_of_planets = random.randint(1,len(planet_parameters))
            correct_answer = [number_of_planets]
            distractors = [k for k in range(0,6) if k != correct_answer[0]]
            fixed_planet_parameters = select_random_items_from_list(fixed_planet_parameters,number_of_planets)
        elif focus_parameter == "tagged_correct":
            # Identify the planet which contains the correctness tag
            tagged_correct_index = [k for k, dict in enumerate(fixed_planet_parameters) if "correct" in dict]
            correct_answer = [standard_answers[tagged_correct_index[0]]]
            distractors = [answer for answer in standard_answers if answer != correct_answer[0]]
            random.shuffle(distractors)
        elif distractor_multipliers:
            # If any other focus parameter, choose the correct answer and distractors randomly
            # within the range specified for the focused parameter

            #correct_answer = [random.uniform(planet_parameters[focus_parameter][0],planet_parameters[focus_parameter][1])]
            #correct_answer = [random.uniform(planet_parameters[focus_parameter][0],planet_parameters[focus_parameter][1])]
            #print(fixed_planet_parameters)
            print('focus parameter is:',fixed_planet_parameters[0][focus_parameter])
            correct_answer = [round_sigfigs(fixed_planet_parameters[0][focus_parameter],3)]
            # print(planet_parameters[focus_parameter][0],planet_parameters[focus_parameter][1])
            # print(correct_answer)
            # Generate the distractors from the provided parameter and multipliers
            distractors = [round_sigfigs(correct_answer[0]*multiplier,3) for multiplier in distractor_multipliers]

        if correct_answer == []:
            raise Exception('Failed to determine the correct answer for a single planet transit graph. Check specified parameters')
        if distractors == []:
            raise Exception('Failed to set distractors for a single planet transit graph. Check specified parameters')
        

        # Produce a list of all of the answers used for this version of the question and 
        # sort them so that they can be compared to previously generated sets
        new_set = correct_answer + distractors
        new_set.sort()

        # If this version of the question isn't a duplicate, use it. We check for this in two ways:
        # Check whether the set of answers are identical to a set previously used. This is effectively impossible 
        # the way the subroutine is currently written, because the answers are always the same set of letters.
        # But it is theoretically possible, so check for it. Even if all of the answers are identical, 
        # we might still pass the question as long as the planets used are different from those used in previous questions.
        # This would be the case if the question were like "Which of these planets has the largest radius? Choose A, B, C, D, or E."
        if (new_set not in previous_answer_sets) or (fixed_planet_parameters not in previous_planet_parameters):

            # Only add labels if there is more than one planet and the goal of the question isn't 
            # for the student to figure out how many there are.
            if (focus_parameter == "num_planets") or len(planet_parameters) == 1:
                labels = False
            else:
                labels = True

            # Plot the graph for this question
            if not os.path.exists(output_image_path):
                os.makedirs(output_image_path)
            image_file = output_image_path+image_string+'_'+str(len(unique_questions_generated))+'.png'
            print("Creating image file: ",image_file)
            generate_transit_graph(fixed_planet_parameters,fixed_graph_parameters,zoom_level,labels,image_file)
            
            # Override stem deduplication if specified in JSON file
            if override_duplicate_stem:
                stem_with_blanks = add_blank_characters(stem,len(unique_questions_generated))
            else:
                stem_with_blanks = stem

            previous_answer_sets.append(new_set)
            unique_questions_generated.append(format_multiple_choice(\
                str(len(unique_questions_generated)+1),stem_with_blanks,correct_answer[0],distractors,image_file))
            # print(unique_questions_generated)
    return unique_questions_generated
