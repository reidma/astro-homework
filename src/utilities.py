import random
import math
import hashlib
import warnings
from datetime import datetime

def add_blank_characters(input_string,num_chars):
    new_string =input_string + '&#8202'*num_chars
    return new_string

def correct_articles(text,search_string,substitution_string):
    # This function takes a string of text as input, searches for search_string, and replaces it
    # with substitution_string. It takes the corrected string and looks at the            
    # character immediately prior to the substitution_string. 
    # All articles ('a' or 'an') immediately prior to the substitution_string are corrected based 
    # on whether the following word starts with
    # a vowel or consonant. It also corrects for single-letter instances of vowel-like consonants
    # such as 'M' and 'N'. The capitalization of the articles is maintained. 

    words = text.split()
    corrected_words = []
    vowels = ['a', 'e', 'i', 'o', 'u']
    vowel_like_consonants = ['m', 'n', 'f', 'h', 'l', 'r', 's', 'x']
    for i, word in enumerate(words):
        if word == search_string: 
            corrected_words.append(substitution_string)
            # If the search string is the first word, just replace it with the substitution_string
            if words[i-1] == 'a' or words[i-1] == 'an':
                if len(substitution_string) == 1 and substitution_string.lower() in vowel_like_consonants:
                    corrected_words[i-1] = 'an'
                elif substitution_string.lower() in vowels:
                    corrected_words[i-1] = 'an'
        else:
            corrected_words.append(word)
    finalized_string = ' '.join(corrected_words)
    return ' '.join(corrected_words)




def select_random_items_from_list(list,num_items):
    if num_items > len(list):
        raise ValueError('You are trying to choose a number of items greater than the number available in the dictionary')
    selected_items = random.sample(list,num_items)
    return selected_items

def round_sigfigs(number, sig_figs):
    """
    Rounds a floating point number to a specified number of significant figures,
    rounding half-integers up to the nearest whole number.
    """
    if number == 0:
        return 0
    
    magnitude = int(math.floor(math.log10(abs(number))))
    digits = sig_figs - 1 - magnitude
    
    factor = 10 ** digits
    rounded_number = round(number * factor)
    return rounded_number / factor

def write_questions_to_file(markdown_output_file,formatted_questions):
    for question in formatted_questions:
        markdown_output_file.write(str(question))

def get_image_filename(stem):
    # Generate the image file name based on hashing the stem for the question.
    # This should ensure that each question gets its own string and that no two questions get the same string.
    # Add a string including the current date and time. So, on subsequent runs, the filename will encode the stem and the time of creation.
    date_string = datetime.now().strftime("%Y%m%d%H%M%S")
    image_string = hashlib.md5(stem.encode()).hexdigest()+'_'+date_string
    return image_string

def check_all_that_apply(stem):
    # Ensure that the stem doesn't end with the phrase "all that apply.":
    if stem.endswith("all that apply."):
        warnings.warn('You really should not force multiple choice formatting when the stem ends with "all that apply." This would imply to students that they must be able to select more than one answer, but you have disabled this functionality, which will be very confusing. Please remove the phrase "all that apply." from the stem or set force_multiple_choice to false.')
