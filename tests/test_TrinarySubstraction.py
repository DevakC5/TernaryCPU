# Substraction (Trinary)

class trit:
    allowed = [0, 1, 2]
    def __init__(self, value):
        if value in self.allowed:
            self.value = value
        else:
            raise ValueError("Value must be 0, 1, or 2")
        
def subtract_trits(trit1, trit2):
    #Reverse the order of strings
    trit1 = str(trit1)[::-1]
    trit2 = str(trit2)[::-1]
    result = ""
    borrow = 0
    for i in range(max(len(trit1), len(trit2))):
        digit1 = int(trit1[i]) if i < len(trit1) else 0
        digit2 = int(trit2[i]) if i < len(trit2) else 0
        total = digit1 - digit2 - borrow
        if total < 0:
            total += 3
            borrow = 1
        else:
            borrow = 0
        result += str(total)
    return result[::-1]

trit1 = int(input("Enter the first trit: "))
trit2 = int(input("Enter the second trit: "))
result = subtract_trits(trit1, trit2)
print("The difference of the two trits is: ", result)
