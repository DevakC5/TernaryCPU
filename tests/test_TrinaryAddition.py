#Single Digit Addition (Trinary)

trit1 = int(input("Enter the first trit: "))
trit2 = int(input("Enter the second trit: "))

carry = 0

#Core Idea ; total = a + b + carry

def add_trits(trit1, trit2, carry):
    #Reverse the order of strings
    trit1 = str(trit1)[::-1]
    trit2 = str(trit2)[::-1]
    result = ""
    for i in range(max(len(trit1), len(trit2))):
        digit1 = int(trit1[i]) if i < len(trit1) else 0
        digit2 = int(trit2[i]) if i < len(trit2) else 0
        total = digit1 + digit2 + carry
        result_digit = total % 3
        carry = total // 3
        result += str(result_digit)
    if carry > 0:
        result += str(carry)
    return result[::-1]

result = add_trits(trit1, trit2, carry)
print("The sum of the two trits is: ", result)

