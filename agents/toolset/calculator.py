from typing import Tuple, List, Union
from langchain_core.tools import Tool

# Taking inspiration of the shunting yard algorithm to implement the calculator tool 
add = lambda a, b: a + b
subtract = lambda a, b: a - b
multiply = lambda a, b: a * b
divide = lambda a, b: a / b
exponent = lambda a, b: a ** b

ops = {
    '+': (1, add),
    '-': (1, subtract),
    '*': (2, multiply),
    '/': (2, divide),
    '**': (3, exponent)
}

# separated preemptive exponent reading from general symbol reading for readability  
def tokenize(expression:str) -> List[Union[float, str]]:
    expression=str(expression).replace(' ','')
    key_symbols='+-*/()' # considering all the possible symbols in any regular expression
    tokens=[]
    num=''
    index = 0
    while index < len(expression):
        char = expression[index]
        if char.isdigit() or char == '.':
            num += char
        else:
            if num:
                tokens.append(float(num))
                num = ""

            # preemptive reading
            if char == '*' and index+1 < len(expression) and expression[index+1] == '*':
                tokens.append('**')
                index += 1
            elif char in key_symbols:
                tokens.append(char)
            else:
                raise ValueError(f"invalid character: {char}")
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
        elif token == '(': # finds the location of opening parentheses first
            stack.append(token)
        elif token == ')': # finds the location of the closing parentheses
            while stack and stack[-1] != '(': # calls only if there is already atleast one opening parentheses present
                output.append(stack.pop())
            if not stack:
                raise ValueError("Mismatched parentheses")
            stack.pop() # popping '('
        elif token in ops: # in the event there is an operator at this index
            while stack and stack[-1] != '(' and ops.get(stack[-1], (0,))[0] >= ops[token][0]: 
                # priority checks the current symbol with any symbols in stack,
                # pops for '(' in the top of stack, priority of current token is less than top operator in stack or
                #       does nothing for non-operator symbols at the top like parentheses
                output.append(stack.pop())
            stack.append(token)

    while stack:
        if stack[-1] == '(':
            raise ValueError("Mismatched parentheses")
        output.append(stack.pop())

    return output

def evaluate_postfix(postfix_tokens: List[Union[float, str]]) -> float:
    stack = []
    for token in postfix_tokens:
        if isinstance(token, float):
            stack.append(token)
        else:
            if len(stack) < 2:
                raise ValueError("Incomplete Expression")
            b = stack.pop()
            a = stack.pop()
            try:
                result = ops[token][1](a,b)
                stack.append(result)
            except ZeroDivisionError:
                raise ValueError("Division by zero")
            except Exception as e:
                raise ValueError(f"Calculation error: {str(e)}")
    
    if len(stack) != 1:
        raise ValueError("Invalid expression")
    
    return stack[0]

def expression_check(tokens: List[Union[float, str]]) -> Tuple[bool, str]:
    supported_symbols= {'+','-','*','/','(',')','**'}
    paren_stack = []
    for i, token in enumerate(tokens):
        if isinstance(token, float):
            continue
        if token not in supported_symbols:
            return False, f"Unsupported operator: {token}"

        if token == '(':
            paren_stack.append(i)
        elif token == ')':
            if not paren_stack:
                return False, "Unbalanced parentheses"
            paren_stack.pop()

    # where paren stack is empty to show that all open and close parentheses cancel out
    if paren_stack:
        return False, "Unbalanced parentheses"

    # valid expression tokens should be like so: ['(', 3.0, '/', 2.0, ')', '*', 4.0, '-', 6.0]
    for i in range(len(tokens)-1):
        ptr = tokens[i]
        ptr2 = tokens[i+1]
        if (ptr in ops and ptr2 in ops) or \
           (isinstance(ptr, float) and isinstance(ptr2, float)):
            return False, "Invalid operator/number sequence"
    
    return True, ""

def calculator(expression: str) -> str:
    try:
        # checking for empty strings
        expr = expression.strip()
        if not expr:
            return "Error: Empty expression"
        
        # Tokenize and validate for proper syntax
        tokens = tokenize(expr)
        is_valid, error_msg = expression_check(tokens)
        if not is_valid:
            return f"Error: {error_msg}"
        
        # Convert to RPN and evaluating expression
        postfix = infix_to_postfix(tokens)
        result = evaluate_postfix(postfix)
        
        # Format result (avoid .0 for whole numbers)
        if result.is_integer():
            return str(int(result))
        return str(round(result, 4))  # Limiting decimal places
    except Exception as e:
        return f"Error: {str(e)}"


def testing():
# if __name__ == "__main__":
    print(calculator("(3*2)/4+ 6"))
    print(calculator("(3*2)-4+6"))
    print(calculator("(3/2)*4- 6"))
    print(calculator("(3/2)*4-=6"))
    print(calculator("(3/0)*4-6"))

Calculator = Tool( name="calculator",
    func=calculator,
    description="A tool used for PEMDAS specific calculations.")