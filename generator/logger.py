def writeLog(data):
    data = " ".join(str(x) for x in data)
    with open("log.txt", "a+") as text_file:
        text_file.writelines(str(data))
        text_file.writelines("\n")

def printL(data):
    print(data)
    with open("log.txt", "a+") as text_file:
        text_file.writelines(str(data))
        text_file.writelines("\n")  