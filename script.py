import pandas as pd

try:
    # Open and read the contents of the file using "r"
    with open("Les_Brown.txt", "r", encoding="utf-8") as file:
        text = file.read()

    # Split text into words
    words = text.lower().split()

    # Count word frequency using dictionary
    word_count = {}
    for word in words:
        word = word.strip(",.!?\"'()")
        word_count[word] = word_count.get(word, 0) + 1


    df = pd.DataFrame(list(word_count.items()), columns=["Word", "Count"])    # Convert to pandas DataFrame.
    df = df.sort_values(by="Count", ascending=False)

    # Print results to a new file
    df.to_csv("word_count.txt", index=False, sep=":")

    print("Word count successfully written to word_count.txt!")

except FileNotFoundError:
    print("Error: The file 'Les_Brown.txt' was not found.")
