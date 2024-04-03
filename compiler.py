import re

WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
SYMBOLS = [';', ':', ',', '[', ']', '{', '}', '+', '-', '*', '=', '<']
LETTERS = [chr(i) for i in range(ord('A'),ord('Z')+1)] + [chr(i) for i in range(ord('a'), ord('z')+1)]
DIGITS = [chr(i) for i in range(ord('0'),ord('9')+1)]
KEYWORDS = ['if', 'else', 'void', 'int', 'for', 'break', 'return', 'endif']
VALID_CHARS = WHITESPACES + SYMBOLS + LETTERS + DIGITS + KEYWORDS

def is_id_keyword(curr_string, look_ahead, prev_result):
    if prev_result < 0:
        return None, -1
    
    if prev_result == 0:
        if curr_string.startswith(tuple(LETTERS)):
            return None, 1
        else:
            return None, -1
    else:
        if curr_string.startswith(tuple(LETTERS)) and look_ahead not in (VALID_CHARS):
            return None, -2
        elif curr_string.startswith(tuple(LETTERS)) and look_ahead not in (LETTERS + DIGITS):
            if curr_string in KEYWORDS:
                return ('KEYWORD', curr_string), 1
            else:
                return ('ID', curr_string), 1            
        elif curr_string.startswith(tuple(LETTERS)):
            return None, 1

def is_num(curr_string, look_ahead, prev_result):
    if prev_result < 0:
        return None, -1
    
    if prev_result == 0:
        if curr_string.startswith(tuple(DIGITS)):
            return None, 1
        else:
            return None, -1
    else:
        if curr_string.startswith(tuple(DIGITS)) and look_ahead in (DIGITS):
            return None, 1
        elif curr_string.startswith(tuple(DIGITS)) and look_ahead in (LETTERS):
            return None, -2
        elif curr_string.startswith(tuple(DIGITS)) and look_ahead 
            #todo: error handling
            return 'error'


def is_symbol(curr_string, look_ahead, prev_result):
    if prev_result < 0:
        return None, -1
    
    if prev_result == 0:
        if curr_string in SYMBOLS and curr_string != '=':
            return ('SYMBOLS', curr_string), 1
        elif curr_string in SYMBOLS and curr_string == '=' and look_ahead == '=':
            return ('SYMBOLS', '=='), 2
        elif curr_string in SYMBOLS and curr_string == '=' and look_ahead != '=':
            return ('SYMBOLS', '='), 1
        else:
            return None, -1

def is_comment(curr_string, prev_result):
    if prev_result < 0:
        return None, -1
    
    if prev_result == 0:
        if curr_string.startswith('/'):
            return None, 1
        else:
            return None, -1
    else:
        if curr_string.startswith('/*') and curr_string.endswith('*/'):
            return ('COMMENT', curr_string), 1
        elif curr_string.startswith('/*'):
            return None, 1
        else:
            # to do: strings start with /{~*}
            return 'error'

def is_whitespace(curr_string, prev_result):
    if prev_result < 0:
        return None, -1
    
    if prev_result == 0:
        if curr_string == ' ':
            return ('WHITESPACE', curr_string), 1
        elif curr_string.startswith('\\'):
            return None, 1
        else:
            return None, -1
    else:
        if curr_string in WHITESPACES:
            return ('WHITESPACE', curr_string), 1
        else:
            # to do: strings start with \ but are not whitespace
            return 'error'

def get_next_token(text):
    line_number = 1
    buffer = ''
    whitespace_result = 0
    symbols_result = 0
    comment_result = 0

    while len(text) != 0:
        for i, char in enumerate(text):
            buffer += char

            # check symbols
            token, symbols_result = is_symbol(buffer, text[i+1], symbols_result)
            if token is not None:
                if symbols_result == 2:
                    text = text[len(buffer)+1:]
                else:
                    text = text[len(buffer):]
                
                yield token, line_number
                break

            # check comment
            token, comment_result = is_comment(buffer, comment_result)
            if token is not None:
                text = text[len(buffer):]
                yield token, line_number
                break

            # check whitespace
            token, whitespace_result = is_whitespace(buffer, whitespace_result)
            if token is not None:
                text = text[len(buffer):]
                yield token, line_number
                if token[1] == '\n':
                    line_number += 1
                break



if __name__ == '__main__':
    # to do: check get_next_token() function
    pass