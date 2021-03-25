from ViginereAnalysis import *

with open("d:/Python/workspace/M1_Course01_Demos/ViginereBreaker-master/Ciphertext.txt", "r") as ciphertext:
    text = ciphertext.read()

    cleanText = re.sub(r"[^a-zA-Z]+", '', text).lower()
    print(text)
    
    patterns = findPatterns(cleanText, 2, 25)   # 查找重复出现的字母序列
    keyLengthPredictions = predictKeyLength(cleanText, patterns, 2, 25) # 由公式可知，秘钥长度只能是2~25

    for prediction in keyLengthPredictions:  # 依照key长度可能性从高到低，遍历猜解
        key = []

        for position in range(prediction[0]):   # 找出长度为prediction[0]的秘钥的每一位字母（并非最后结果，只是最大概率）
            # 形如 [('a', 3.4043673144945434), ('b', 3.25679954308027),..., ('z', 3.266028770954746)]
            # 取概率最大的字母，用于组成key
            key.append(predictKeySliceLetters(getKeySlice(cleanText, position, prediction[0]))[0][0])

        key = "".join(key)

        print("\n\n\n")
        print("KEY FIT: ", predictKeyFit(cleanText, key), "WITH KEY: ",key)

        print(decode(text, key))

        input("press any key to continue...")




                



            

        


            
