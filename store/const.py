



# function that make number a fload and it id have more than 2 after the point it will be rounded to 2 decimal places
# fonvert it to float if it is not a float
def convert_to_float(number):
    if isinstance(number, float):
        return number
    else:
        return float(number)


def round_number(number):
    number = convert_to_float(number)
    return round(number, 2)