from langchain_core.tools import Tool

# Taking inspiration of the shunting yard algorithm to implement the calculator tool 
add= lambda a,b: a + b,
subtract= lambda a,b: a - b,
multiply= lambda a,b: a * b,
divide= lambda a,b: a / b,
exponent= lambda a,b: a ** b

ops = {
    '+': (1, add),
    '-': (1, subtract),
    '*': (2, multiply),
    '/': (2, divide),
    '**': (3, exponent)
}

def tokenize(expression:str):
    expression=str(expression)
    key_symbols='+-*/()' # considering all the possible symbols in any regular expression
    tokens=[]
    num=''
    index = 0
    while index < len(expression):
        char=expression[index]
        if char.isdigit() or char == '.':
            num += char
        else:
            if num:
                tokens.append(float(num))
                num=""
            if char in key_symbols:
                if char == '*' and index+1 < len(expression) and expression[index+1] == '*':
                    tokens.append('**')
                    index += 1
                else:
                    tokens.append(char)
        index += 1
    if num: # flushing any remaining number in the expression
        tokens.append(float(num))
    return tokens

def infix_to_postfix(tokens):
    output = []
    stack = []
    for token in tokens:
        if isinstance(token, float): # checking for numbers in the tokens to append to the output list immediately 
            output.append(token) 
        elif token in ops: # in the event there is an operator at this index
            while stack and stack[-1] != '(' and ops.get(stack[-1], (0,))[0] >= ops[token][0]: 
                # priority checks the current symbol with any symbols in stack,
                # pops for '(' in the top of stack, priority of current token is less than top operator in stack or
                #       does nothing for non-operator symbols at the top like parentheses
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop() # popping '('
    while stack:
        output.append(stack.pop())
    return output


def evaluate_postfix(postfix_tokens):
    stack = []
    for token in postfix_tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            b = stack.pop()
            a = stack.pop()
            result = ops[token][1](a, b)
            stack.append(result)
    return stack[0]

def expression_check(tokens, supported_symbols):
    for token in tokens:
        if isinstance(token, float):
            continue
        if token not in supported_symbols:
            return True, token
    return False, None

def calculator(expression):
    supported_symbols= ['+','-','*','/','(',')','**']
    tokens = tokenize(expression.replace(' ', ''))
    
    try:
        expression_check(tokens, supported_symbols)
    except Exception as e:
        return f"Error: Invalid Expression. Details: {str(e)}"
    
    postfix = infix_to_postfix(tokens)
    result = str(evaluate_postfix(postfix))
    return result

Calculator = Tool(name="calculator",
    func=lambda expression: str(calculator(expression)),
    description="Useful for simple mathematical operations"
)