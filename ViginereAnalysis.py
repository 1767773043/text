import re
import math

LETTERS = ["a","b","c","d","e","f","g","h","i","j","k","l","m",
            "n","o","p","q","r","s","t","u","v","w","x","y","z"]

FREQUENCIES = [8.12, 1.49, 2.71, 4.32, 12.02, 2.3, 2.03, 5.92, 7.31, 0.1,
               0.69, 3.98, 2.61, 6.95, 7.68, 1.82, 0.11, 6.02, 6.28, 9.1,
               2.88, 1.11, 2.09, 0.17, 2.11, 0.07]  # 通用文本中各字母的出现概率（%）

englishLetterFrequencies = dict(zip(LETTERS, FREQUENCIES))

# Find every sequence of letters with a length ranging from minSize to maxSize
# and encode the sequence and how many times it appears in a dict.
# PatternSize：字母序列长度 2~25
def findPatterns(ciphertext, minPatternSize, maxPatternSize, verbose = True):
    patterns = {}

    for i in range(minPatternSize, maxPatternSize + 1):
        for j in range(i, len(ciphertext)):
            
            pattern = ciphertext[j-i:j]     # 长度为j的某个字母序列

            if pattern not in patterns:
                matches = re.findall(rf'{pattern}', ciphertext)

                if matches and len(matches) > 1:    # 不止1次遇到相同的字母序列
                    patterns[pattern] = len(matches)

                    if verbose: print("Pattern: ", pattern, " , Hits: ", matches)   # 可视化
                    

    return patterns

# Calculate the probability of every key length given the number of patterns that
# repeat with a frequency that is a product of that length. (Yes I know this is a bad name
# for the function, fight me)
def predictKeyLength(ciphertext, patterns, minKeySize, maxKeySize, verbose = True):

    if len(patterns) == 0:
        raise Exception("No patterns found! Unable to predict key length.")

    distances = {pattern:[] for pattern in patterns.keys()}     # 用于存放某字母序列第一次出现和后续出现时，间隔的字母个数


    for pattern in distances.keys():
        locations = []

        for i in range(len(pattern), len(ciphertext)):
            if pattern == ciphertext[i - (len(pattern)):i]:
                locations.append(i)
        
        distances[pattern] = [locations[i] - locations[i - 1] for i in range(1, len(locations))]

    #for pattern, distanceList in distances.items():
        #if verbose: print("Pattern: ",pattern," , distances: ",distanceList)

    
    keyLengths = []

    # Kasiski测试
    for i in range(minKeySize, maxKeySize + 1):
        totalSuccesses = 0
        totalFailures = 0

        for distanceList in distances.values():
            
            for distance in distanceList:
                if distance % i == 0:       # 如果字母序列间隔距离可以被字母序列长度整除，则有可能该间隔距离的因子中某个数为秘钥长度
                    totalSuccesses += 1
                else:
                    totalFailures += 1

        total = totalSuccesses + totalFailures

        keyLengths.append((i, totalSuccesses / total, totalFailures / total))

    # 列举出秘钥长度为2~25这24种情况下，匹配成功和失败的可能性，第一位最有可能
    keyLengths.sort(key = lambda x: x[2])

    for keyLength in keyLengths:
        if verbose: print("Length: ",keyLength[0]," Successes: ",keyLength[1]," Failures: ",keyLength[2])

    return keyLengths

# Get every character in the ciphertext that was encoded using the position'th letter in the
# key given the key length
# 在给定密钥长度的情况下，获取在密文中使用位置中的第position个字母进行编码的每个字符
def getKeySlice(ciphertext, position, keyLength):
    return "".join([char for i,char in enumerate(ciphertext) if i % keyLength == position])

# Calculate the frequency of every letter in a given piece of text as a percentage of
# the total number of letters.
def calculateLetterFrequency(text):
    letterFrequencies = {letter:0 for letter in LETTERS} # {'a': 0, 'b': 0, ..., 'z': 0}
    
    for letter in text:
        letterFrequencies[letter] += 1

    return [freq / len(text) * 100 for freq in letterFrequencies.values()]

# Calculate the RMSE error between the letter frequencies in a given piece of text
# and the letter frequencies in the English language.
def calculateFrequencyFit(text):
    letterFrequencies = calculateLetterFrequency(text)

    errors = [letterFreq - FREQUENCIES[j] for j, letterFreq in enumerate(letterFrequencies)]
    totalError = math.sqrt(sum([error * error for error in errors]) / len(errors))

    return totalError

# Predict the key letter that was used to encode this slice using the frequency of
# the letters in the slice.
# 使用切片中字母的频率来预测用于对该切片的组成字母
def predictKeySliceLetters(keySlice):
    ciphertextLetterFrequencies = calculateLetterFrequency(keySlice)    # 26个字母各占总文本的百分之多少
    letterProbabilities = []    # 各个字母的均方误差，可反映该字母出现的概率，误差越小概率越大

    for i, letter in enumerate(LETTERS):
        # 通过计算每个字母的概率分布和通用文本概率分布比较，本文本和通用文本的均方误差
        errors = [ciphertextFreq - FREQUENCIES[j] for j, ciphertextFreq in enumerate(rotate(ciphertextLetterFrequencies, i))]
        totalError = math.sqrt(sum([error * error for error in errors]) / len(errors))  # 求均方误差

        letterProbabilities.append((letter, totalError))

    letterProbabilities.sort(key = lambda x: x[1])  # 26个字母按均方误差升序，即按可能性降序

    return letterProbabilities

# Decode a vigere cipher given the key.
def decode(ciphertext, key):
    decoded = ""

    keyChar = 0

    for char in ciphertext.lower():
        if char in LETTERS:

            if key[keyChar % len(key)] != "_":
                
                decoded += LETTERS[(LETTERS.index(char) - LETTERS.index(key[keyChar % len(key)])) % len(LETTERS)]   # 查表，单表置换解密
            else:
                decoded += "_"

            keyChar += 1

        else:
            decoded += char

    return decoded

# Encode the plaintext using the key.
def encode(plaintext, key):
    encoded = ""

    keyChar = 0

    for char in plaintext:
        if char in LETTERS:

            if key[keyChar % len(key)] != "_":
                
                encoded += LETTERS[(LETTERS.index(char) + LETTERS.index(key[keyChar % len(key)])) % len(LETTERS)]
            else:
                encoded += "_"

            keyChar += 1

        else:
            encoded += char

    return encoded

# Rotate a list. Takes the last n items in the list and puts them at the front, then shifts
# every other item right by n.
def rotate(seq, n):
    return seq[n:]+seq[:n]

# Predicts key fit by decoding the ciphertext using the key and comparing the resulting
# letter frequencies to those found in English.
def predictKeyFit(ciphertext, key):
    decoded = decode(ciphertext, key)       # 以此key解密
    return calculateFrequencyFit(decoded)   # 计算解密结果好坏

