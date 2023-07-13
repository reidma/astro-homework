import random
import math

def add_blank_characters(input_string,num_chars):
    new_string =input_string + '&#8202'*num_chars
    return new_string

def correct_articles(text):
    """
    This function takes a string of text as input and returns the corrected string with
    all articles ('a' or 'an') corrected based on whether the following word starts with
    a vowel or consonant. It also corrects for single-letter instances of vowel-like consonants
    such as 'M' and 'N'. The capitalization of the articles is maintained.
    """
    words = text.split()
    corrected_words = []
    vowels = ['a', 'e', 'i', 'o', 'u']
    vowel_like_consonants = ['m', 'n']
    for i, word in enumerate(words):
        lower_word = word.lower()
        if lower_word == 'a' or lower_word == 'an':
            is_uppercase = word[0].isupper()
            corrected_word = ''
            if i+1 < len(words):
                next_word = words[i+1]
                # Check if the word is a single character and starts with 'm' or 'n'
                if len(next_word) == 1 and next_word.lower() in vowel_like_consonants:
                    corrected_word = 'an'
                elif next_word[0].lower() in vowels:
                    corrected_word = 'an'
                else:
                    corrected_word = 'a'
            corrected_word = corrected_word.capitalize() if is_uppercase else corrected_word
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
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
