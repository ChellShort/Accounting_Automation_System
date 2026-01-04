import re

def find_numbers_with_positions_regex(text):
    """
    Finds all numbers in a string and returns them with their start and end positions.
    """
    # The pattern r'\d+' matches one or more digits
    matches = re.finditer(r'\d+', text)
    results = []
    for match in matches:
        print(match)
        number = match.group(0) # The actual number string
        start_index = match.start() # The start index of the number
        end_index = match.end()   # The end index + 1 of the number
        results.append({
            'number': number,
            'start': start_index,
            'end': end_index
        })
    return results

# Example Usage:
my_string = "There are 12 eggs and 3.5 apples, with 4 dozen more items."
positions = find_numbers_with_positions_regex(my_string)
print(positions)

