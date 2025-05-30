import os

paths = [
    r"C:\Users\u8064927\Desktop\Rolls-Royce X Ali\Normstelle\Teile und Stoffe\Antrag_RRT129127.pdf",
    r"C:\Users\u8064927\Desktop\Rolls-Royce X Ali\Normstelle\Teile und Stoffe\Antrag_RRT1291d27.pdf",
]

# check if filepath is valid
for file in paths:
    if os.path.isfile(file) is True:
        print(f"file: {file} exists")
    else:
        print(f"file: {file} doesnt exists")