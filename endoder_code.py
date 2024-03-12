
def encode_message(message):
    words = message.split()
    for index, word in enumerate(words):
        if len(word) > 3:
            words[index] = word[::-1]
    return ' '.join(words)

def main():
    message = input("Enter the message: ")
    print(encode_message(message))

if __name__ == "__main__":
    main()