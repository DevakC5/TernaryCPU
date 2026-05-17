#Making a basic Binary to Trinary Converter

class trit:
    allowed = [0, 1, 2]
    def __init__(self, value):
        if value in self.allowed:
            self.value = value
        else:
            raise ValueError("Value must be 0, 1, or 2")
        

def binary_to_trinary(binary):
    # Convert binary string to decimal
    decimal = int(binary, 2)
    
    # Convert decimal to trinary
    trinary = ""
    while decimal > 0:
        remainder = decimal % 3
        trinary = str(remainder) + trinary
        decimal //= 3
    
    return trinary if trinary else "0"

# Example usage
binary_input = input("Enter a binary number: ")  # This is 13 in decimal
trinary_output = binary_to_trinary(binary_input)
print(f"Binary: {binary_input} -> Trinary: {trinary_output}")