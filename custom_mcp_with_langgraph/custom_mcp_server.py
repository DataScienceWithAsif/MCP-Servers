from mcp.server.fastmcp import FastMCP
import math

server = FastMCP("math")

@server.tool()
def add(a:int, b:int) -> int:
    """Add Two nubmers"""
    return a + b

@server.tool()
def subtract(a:int, b:int) -> int:
    """Subtract Two numbers"""
    return a - b

@server.tool()
def multiply(a:int, b:int) -> int:
    """Multiply two numbers"""
    return a * b

@server.tool()
def divide(a:float, b:float) -> float:
    """Divide Two numbers a and b. raise error if b is zero"""
    if b == 0:
        raise ValueError("Division by zero is not allowed!")
    else:
        return a / b

@server.tool()
def square_root(x:float) -> float:
    """Return the square root of value x"""  
    if x < 0:
        raise ValueError("cannot take square root of a negative number")
    else:
        return math.sqrt(x)
 
@server.tool()
def factorial(n:int) -> int:
    """Return factorial of n"""
    if n < 0:
        raise ValueError("Factorial is not defined of a negative number")
    else:
        return math.factorial(n)
    

if __name__ == "__main__":
    # server.run(transport="stdio")
    server.run(transport="streamable-http")