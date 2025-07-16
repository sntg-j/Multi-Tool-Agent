from langchain_core.tools import tool

@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@tool
def subtract(a: float, b: float) -> float:
    """Subtract two numbers."""
    return a - b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide two numbers."""
    return a / b

@tool
def exponent(a: float, b: float) -> float:
    """Raise a to the power of b."""
    return a ** b

@tool
def remainder(a: float, b: float) -> int:
    """Find remainder of division of a and b."""
    return a % b


if __name__ == '__main__':
    fun_list = [add, subtract, multiply, divide, exponent, remainder]
    for function in fun_list:
        print(function.name)
        print(function.description)
        print(function.args)