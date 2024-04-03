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
        if curr_string.startswith(tuple(DIGITS)) and look_ahead not in (VALID_CHARS):
            return None, -2
        elif curr_string.startswith(tuple(DIGITS)) and look_ahead in (LETTERS):
            return None, -2
        elif curr_string.startswith(tuple(DIGITS)) and look_ahead in (DIGITS):
            return None, 1
        else:
            return ('NUM', curr_string), 1


def is_symbol(curr_string, look_ahead, prev_result):
    if prev_result < 0:
        return None, -1

    if curr_string == '*' and look_ahead == '/':
        return None, -2             # panic (umnatched comment)
    elif curr_string in SYMBOLS and curr_string != '=':
        return ('SYMBOLS', curr_string), 1
    elif curr_string == '=' and look_ahead == '=':
        return ('SYMBOLS', '=='), 1
    elif curr_string == '=' and look_ahead != '=':
        return ('SYMBOLS', '='), 1
    else:
        return None, -1


def is_comment(curr_string, look_ahead, prev_resutl):
    if prev_resutl < 0:
        return None, -1

    if prev_resutl == 0:
        if curr_string == '/':
            if (curr_string+look_ahead) != '/*':
                return None, -2     # panic (invalid input)
            else:
                return None, 1      # possible token
        else:
            return None, -1         # not comment
    # it is a possible token
    else:
        if curr_string.startswith('/*') and curr_string.endswith('*/'):
            return ('COMMENT', curr_string), 1
        else:
            return None, 1          # still possible


def is_whitespace(curr_string, look_ahead, prev_result):
    if prev_result < 0:
        return None, -1

    if curr_string == ' ':
        return ('WHITESPACE', curr_string), 1
    elif curr_string == '\\':
        if (curr_string+look_ahead) in WHITESPACES:
            return ('WHITESPACE', curr_string+look_ahead), 1
        else:
            return None, -2         # panic (invalid input)
    else:
        return None, -1             # not whitespace


def get_next_token(text):
    line_number = 1

    while True:
        buffer = ''
        look_ahead = ''
        is_panic, panic_type = False, ''
        whitespace_result, symbols_result, comment_result, num_result, id_result = 0, 0, 0, 0, 0
        token = None

        for i, char in enumerate(text):
            buffer += char
            look_ahead = '' if i+1 == len(text) else text[i+1]

            # check number
            token, num_result = is_num(buffer, look_ahead, num_result)
            if num_result == -2:
                is_panic = True
                panic_type = 'Invalid number'
                buffer = buffer + look_ahead
                break
            if token is not None:
                yield token, line_number
                break

            # check id, keyword
            token, id_result = is_id_keyword(buffer, look_ahead, id_result)
            if id_result == -2:
                is_panic = True
                panic_type = 'Invalid input'
                buffer = buffer + look_ahead
                break
            if token is not None:
                yield token, line_number
                break

            # check symbols
            token, symbols_result = is_symbol(buffer, look_ahead, symbols_result)
            if symbols_result == -2:
                is_panic = True
                panic_type = 'Unmatched comment'
                buffer = buffer + look_ahead
                break
            if token is not None:
                yield token, line_number
                break

            # check comment
            token, comment_result = is_comment(buffer, look_ahead, comment_result)
            if comment_result == -2:
                is_panic = True
                panic_type = 'Invalid input'
                break
            if token is not None:
                yield token, line_number
                break

            # check whitespace
            token, whitespace_result = is_whitespace(buffer, look_ahead, whitespace_result)
            if whitespace_result == -2:
                is_panic = True
                panic_type = 'Invalid input'
                break
            if token is not None:
                yield token, line_number
                break

            # check invalid input
            if -1 == num_result == id_result == symbols_result == comment_result == whitespace_result:
                is_panic = True
                panic_type = 'Invalid input'
                break

        # check panic
        if is_panic:
            panic = (panic_type, buffer)
            yield panic, line_number
            move_len = len(buffer)
        # check unclosed comment
        elif token is None and comment_result == 1:
            panic = ('Unclosed comment', buffer)
            yield panic, line_number
            move_len = len(buffer)
        # check new line
        elif token is not None:
            if token[1] == '\n':
                line_number += 1
            move_len = len(token[1])
        
        # remove token from text
        text = text[move_len:]

        # check end of file
        if text == '':
            break


if __name__ == '__main__':
    token_tags = ['NUM', 'ID', 'KEYWORD', 'SYMBOL']
    symboltable_tags = ['ID', 'KEYWROD']
    panic_tags = ['Invalid input', 'Unclosed comment', 'Unmatched comment', 'Invalid number']

    # read input
    addr = './testcases/T01/input.txt'
    with open(addr, 'r') as f:
        text = f.read()
    
    # generate tokens
    tokens = ''
    symbols = set()
    errors = ''
    prev_linenumber = 0
    for t, line_number in get_next_token(text):
        if t[0] in token_tags:
            if line_number != prev_linenumber:
                tokens += f'\n{line_number}.\t'
                prev_linenumber = line_number
            tokens += f'{(t[0], t[1])} '
        
        elif t[0] in panic_tags:
            if line_number != prev_linenumber:
                errors += f'\n{line_number}.\t'
                prev_linenumber = line_number
            errors += f'{(t[1], t[0])} '

        elif t[0] in symboltable_tags:
            symbols.add(t[1])

    # save results in file
    with open('./tokens.txt', 'w') as f:
        f.write(tokens[2:])
    with open('./lexical_errors.txt', 'w') as f:
        f.write(errors[2:])
    with open('./symbol_table.txt', 'w') as f:
        f.write('\n'.join([f'{i+1}.\t{x}' for i, x in enumerate(symbols)]))
