WHITESPACES = [' ', '\n', '\r', '\t', '\v', '\f']
SYMBOLS = [';', ':', ',', '[', ']','(', ')', '{', '}', '+', '-', '*', '=', '<']
LETTERS = [chr(i) for i in range(ord('A'), ord('Z')+1)] + [chr(i) for i in range(ord('a'), ord('z')+1)]
DIGITS = [chr(i) for i in range(ord('0'), ord('9')+1)]
KEYWORDS = ['if', 'else', 'void', 'int', 'for', 'break', 'return', 'endif']
VALID_CHARS = WHITESPACES + SYMBOLS + LETTERS + DIGITS + KEYWORDS


class Scanner():
    def __init__(self, addr):
        self.text = self._read_file(addr)
        self.line_number = 1

    def _read_file(self, addr):
        text = ''
        with open(addr, 'r') as f:
            text = f.read()
        return text

    def is_id_keyword(self, curr_string, look_ahead, prev_result):
        if prev_result < 0:
            return None, -1

        if curr_string.startswith(tuple(LETTERS)) and look_ahead not in (VALID_CHARS):
            return None, -2
        elif curr_string.startswith(tuple(LETTERS)) and look_ahead not in (LETTERS + DIGITS):
            if curr_string in KEYWORDS:
                return ('KEYWORD', curr_string), 1
            else:
                return ('ID', curr_string), 1
        elif curr_string.startswith(tuple(LETTERS)):
            return None, 1
        else:
            return None, -1

    def is_num(self, curr_string, look_ahead, prev_result):
        if prev_result < 0:
            return None, -1

        if not curr_string.startswith(tuple(DIGITS)):
            return None, -1
        elif curr_string.startswith(tuple(DIGITS)) and look_ahead in (LETTERS):
            return None, -2
        elif curr_string.startswith(tuple(DIGITS)) and look_ahead in (DIGITS):
            return None, 1
        else:
            return ('NUM', curr_string), 1

    def is_symbol(self, curr_string, look_ahead, prev_result):
        if prev_result < 0:
            return None, -1

        if curr_string == '*' and look_ahead == '/':
            return None, -2             # panic (umnatched comment)
        elif curr_string in SYMBOLS and curr_string != '=':
            return ('SYMBOL', curr_string), 1
        elif curr_string == '=' and look_ahead == '=':
            return ('SYMBOL', '=='), 1
        elif curr_string == '=' and look_ahead != '=':
            return ('SYMBOL', '='), 1
        else:
            return None, -1

    def is_comment(self, curr_string, look_ahead, prev_resutl):
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

    def is_whitespace(self, curr_string, look_ahead, prev_result):
        if prev_result < 0:
            return None, -1

        if curr_string in WHITESPACES:
            return ('WHITESPACE', curr_string), 1
        else:
            return None, -1

    def get_next_token(self):
        # check end of file
        if self.text == '':
            return ('EOF', '$'), self.line_number
        
        buffer = ''
        look_ahead = ''
        is_panic, panic_type = False, ''
        whitespace_result, symbols_result, comment_result, num_result, id_result = 0, 0, 0, 0, 0
        token = None

        for i, char in enumerate(self.text):
            buffer += char
            look_ahead = '' if i+1 == len(self.text) else self.text[i+1]

            # check number
            token, num_result = self.is_num(buffer, look_ahead, num_result)
            if num_result == -2:
                is_panic = True
                panic_type = 'Invalid number'
                buffer = buffer + look_ahead
                break
            if token is not None:
                break

            # check id, keyword
            token, id_result = self.is_id_keyword(buffer, look_ahead, id_result)
            if id_result == -2:
                is_panic = True
                panic_type = 'Invalid input'
                buffer = buffer + look_ahead
                break
            if token is not None:
                break

            # check symbols
            token, symbols_result = self.is_symbol(buffer, look_ahead, symbols_result)
            if symbols_result == -2:
                is_panic = True
                panic_type = 'Unmatched comment'
                buffer = buffer + look_ahead
                break
            if token is not None:
                break

            # check comment
            token, comment_result = self.is_comment(buffer, look_ahead, comment_result)
            if comment_result == -2:
                is_panic = True
                panic_type = 'Invalid input'
                break
            if token is not None:
                break

            # check whitespace
            token, whitespace_result = self.is_whitespace(buffer, look_ahead, whitespace_result)
            if token is not None:
                break

            # check invalid input
            if -1 == num_result == id_result == symbols_result == comment_result == whitespace_result:
                is_panic = True
                panic_type = 'Invalid input'
                break

        # check new line
        if token is not None:
            result = (token, self.line_number)
            if token[1] == '\n':
                self.line_number += 1
            move_len = len(token[1])
        # check panic
        elif is_panic:
            result = ((panic_type, buffer), self.line_number)
            move_len = len(buffer)
        # check unclosed comment
        elif token is None and comment_result == 1:
            result = (('Unclosed comment', f'{buffer[:7]}...'), self.line_number)
            move_len = len(buffer)

        # remove token from text
        self.text = self.text[move_len:]

        return result
