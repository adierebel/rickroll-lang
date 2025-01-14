from time import time
from os.path import exists
from sys import argv, stdout

from PublicVariables import *
from Lexer import Lexer

# Help message
rick_help = """
Programming by writing code:   rickroll -s [File_Name]
Generate an audio: rickroll -r [File_Name] -audio [Audio_Name]
Sing code:  rickroll -sing [Audio_Name] [File_Name]

Other Options:
--time:      Show execution time of your code
--help/--h:  Help
"""

# Token types
TT_keyword             = 'KEYWORDS'
TT_identifier          = 'IDENTIFIER'
TT_arithmetic_operator = 'OPERATORS-ARITHMETIC'
TT_assignment_operator = 'OPERATORS-ASSIGNMENT'
TT_relational_operator = 'OPERATORS-RELATIONAL'
TT_logical_operator    = 'OPERATORS-LOGICAL'
TT_other_operator      = 'OPERATORS-OTHER'
TT_built_in_funcs      = 'OPERATORS-BUILT-IN-FUNCS'

TT_int                 = 'VALUE-INT'
TT_float               = 'VALUE-FLOAT'
TT_bool                = 'VALUE-Bool'
TT_char                = 'VALUE-Char'
TT_string              = 'VALUE-String'

start = time()

"""
Code level works as indentation in python
"""
# The current code level the interpreter is reading
current_code_level = 0
# The code level that the interpreter should execute or interpret
executing_code_level = 0

in_loop = False
in_loop_stmts = []

while_condition = False

current_line = 0
# For definining variables (Relevant: Interpreter, KW_let)
variables = {}



test_types = ['KEYWORDS', 'VALUE-String']
test_tokens = ['i_just_wanna_tell_u_how_im_feeling', '"Hello\\n"']


# Determine variable types
def v_types(string):
    string = str(string)
    # Boolean
    if string == 'True' or string == 'False':
        return 'bool'
    # String
    if string[0] == '"' and string[-1] == '"':
        return 'string'
    # List
    if string[0] == '[' and string[-1] == ']':
        return 'list'
    # Determine the string is int or float
    count = 0
    for char in string:
        if char in digits:
            count += 1
    if count == len(string) and string.count('.') < 2:
        return 'number'

class Token:
    def __init__(self, raw_tokens):
        self.__raw_tokens = raw_tokens
        self.tokens = []      # Tokens
        self.types = []       # Token types

        for t in self.__raw_tokens:
            if t:
                self.make_token(t)

    def make_token(self, t):

        def typeof(string):
            if string.count('"') == 2: return 'string'

            count = 0
            for i in string:
                if i in digits: count += 1
            if count == len(string):
                if string.count('.') == 1: return 'float'
                if string.count('.') == 0: return 'int'

        if t:
            self.tokens.append(t)
            if t in keywords:
                self.types.append(TT_keyword)
            elif t in OP_arithmetic:
                self.types.append(TT_arithmetic_operator)
            elif t in OP_assignment:
                self.types.append(TT_assignment_operator)
            elif t in OP_relational:
                self.types.append(TT_relational_operator)
            elif t in OP_other:
                self.types.append(TT_other_operator)
            elif t in OP_build_in_functions:
                self.types.append(TT_built_in_funcs)
            elif typeof(t) == 'int':
                self.types.append(TT_int)
            elif typeof(t) == 'float':
                self.types.append(TT_float)
            elif typeof(t) == 'string':
                self.types.append(TT_string)
            else:
                self.types.append(TT_identifier)


class Interpreter:
    def __init__(self, types, tokens):
        self.types = types
        self.tokens = tokens

        # If this line is executable or should be executed, then execute this line of code
        if self.types[0] == TT_keyword:
            self.run_code(kw=self.tokens[0])

    # Indentation, edits the two code levels
    def indent(self):
        global current_code_level, executing_code_level
        current_code_level += 1
        executing_code_level += 1


    # Get the value of an expression (EXPR)
    def evaluate(self, types=[], tokens=[]):
        for i in range(len(types)):
            if types[i] == TT_identifier:
                tokens[i] = variables[tokens[i]]

            if types[i] == TT_relational_operator:
                if tokens[i] == 'is_greater_than': tokens[i] = '>'
                if tokens[i] == 'is_less_than': tokens[i] = '<'
                if tokens[i] == 'is': tokens[i] = '=='
                if tokens[i] == 'is_not': tokens[i] = '!='

            if types[i] == TT_built_in_funcs:
                if tokens[i] == 'to_string': tokens[i] = 'str'


        try:
            return eval(join_list(tokens))

        except SyntaxError:
            return eval(f'"{join_list(tokens)}"')


    def run_code(self, kw):
        global current_code_level, executing_code_level
        global in_loop, in_loop_stmts, while_condition


        """
            End statement, which 
        """
        if kw == KW_end:
            
            run_loop = False

            if executing_code_level == current_code_level:
                executing_code_level -= 1

                # End a loop
                if in_loop:
                    in_loop = False
                    run_loop = True

            # the current code level go back 1
            current_code_level -= 1

            # Run the codes in loop
            if run_loop:
                while while_condition:
                    for stmt in in_loop_stmts:
                        Interpreter(stmt[0], stmt[1])


        # If the current code level should not execute, then return back (don't execute)
        if executing_code_level != current_code_level:
            return

        if in_loop:
            in_loop_stmts.append([self.types, self.tokens])
            return


        if kw == KW_main:
            self.indent()

        elif kw == KW_print:
            """
                PRINT EXPR
            """
            EXPR = self.evaluate(self.types[1:], self.tokens[1:])
            stdout.write(str(EXPR))

        elif kw == KW_if:
            """
                IF CONDI
            """
            CONDI = self.evaluate(self.types[1:], self.tokens[1:])
            if CONDI:
                executing_code_level += 1

            current_code_level += 1

        elif kw == KW_endless_loop:
            in_loop = True
            while_condition = True
            self.indent()

        elif kw == KW_while_loop:
            """
                WHILE CONDI
            """
            CONDI = self.evaluate(self.types[1:], self.tokens[1:])
            while_condition = CONDI
            if CONDI:
                in_loop = True
                executing_code_level += 1
            current_code_level += 1

            # self.indent()

        elif kw == KW_let:
            """
                LET ID = EXPR
            """
            ID = self.tokens[self.tokens.index(KW_let) + 1]

            EXPR = self.evaluate(
                types = self.types[self.types.index(TT_assignment_operator) + 1:],
                tokens = self.tokens[self.types.index(TT_assignment_operator) + 1:]
            )
            variables.update({ID: EXPR})


def run_in_interpreter(src_file_name):
    global current_line

    with open(src_file_name, mode='r', encoding='utf-8') as src:
        content = src.readlines()
        content[-1] += '\n'
        for i in range(len(content)):
            current_line += 1
            lexer = Lexer(stmt=content[i])    # "statement" is a line of code the in source code
            token = Token(raw_tokens=lexer.tokens)
            if token.tokens:
                try:
                    Interpreter(types=token.types, tokens=token.tokens)

                except Exception as e:
                    stdout.write(f'Exception in line {current_line}: {e}\n')
