color = (163, 245, 43)  # RGB tuple
variable = "some text"

# Dynamically construct the color escape code
color_code = f"\033[38;2;{color[0]};{color[1]};{color[2]}m"

# Print the variable with the dynamically constructed color
print(f"{color_code}{variable}\033[0m")
