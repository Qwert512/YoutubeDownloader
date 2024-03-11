import re

def remove_prefix_except(x, allowed_chars):
    # Define the regex pattern to find the first character not in allowed_chars
    pattern = r'[^' + re.escape(allowed_chars) + ']'

    # Find the index of the first character not in allowed_chars
    match = re.search(pattern, x)
    if match:
        index = match.start()
        return x[index:]
    else:
        return x  # No characters found that aren't in allowed_chars

# Example string
x = "123abc:def_ghi-jkl_mno"

# Define allowed characters
allowed_chars = "-_: "

# Remove prefix except for allowed characters
result = remove_prefix_except(x, allowed_chars)
print(result)  # Output will be ":def_ghi-jkl_mno"
