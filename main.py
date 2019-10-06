import sys
import math
import os
from os.path import isfile, join, isdir
# import timeit

class Node:
    def __init__(self, parent=None, value=None, index=None):
        self.parent = parent
        self.value = value
        self.index = index
        self.children = {}

    def setValue(self, value):
        self.value = value

    def setParent(self, parent):
        self.parent = parent

    def setIndex(self, index):
        self.index = index
    
    def getIndex(self):
        return self.index
    
    def addChild(self, value, index=None):
        node = Node(self, value, index)
        self.children[value] = node
        return node

    def findValue(self, value):
        if value in self.children:
            return self.children[value]
        else:
            return None
    

class LZ78:
    def __init__(self, directoryPath, outputDirPath=""):
        self.directoryPath = directoryPath
        self.root = Node(index=0)
        self.mapping = []
        self.next_index = 1
        self.outputDirPath = outputDirPath
    
    def clear(self):
        self.root = Node(index=0)
        self.mapping = []
        self.next_index = 1

    def findLastOne(self, node, inputs):
        for i in inputs:
            node = node.findValue(i)
        return self.mapping[node.getIndex()]

    def add_to_tree(self, node, inputs, index):
        if len(inputs) <= index:
            return 0
        childNode = node.findValue(inputs[index])
        if childNode is not None:
            return self.add_to_tree(childNode, inputs, index + 1)       
        else:
            if index != len(inputs) - 1:
                raise Exception("Could not find intermediate nodes values")
            node.addChild(inputs[index], self.next_index)
            self.mapping.append((node.getIndex(), inputs[index]))
            return 1

    def addToTree(self, inputs):
        ret = self.add_to_tree(self.root, inputs, 0)
        # print("ret = ", ret)
        if ret == 1:
            inputs.clear()
            self.next_index = self.next_index + 1

    def lz78_compress(self, inputPath, outputPath):
        self.clear()
        print("mapping: ", self.mapping)
        print("index", self.next_index)
        

        inputs = []
        with open(inputPath, 'rb') as f:
            while True:
                binary_input = f.read(1)
                if not binary_input:
                    break
                decimal_input = int.from_bytes(binary_input, 'big')
                # print(binary_input)
                inputs.append(decimal_input)
                self.addToTree(inputs)

        with open(outputPath, "wb") as f:
            for index, value in self.mapping:
                self.writeIndex(f, index)
                f.write(value.to_bytes(1, 'big'))
            if len(inputs) > 0:
                index, value = self.findLastOne(self.root, inputs)
                self.writeIndex(f, index)
                f.write(value.to_bytes(1, 'big'))
        
    def writeIndex(self, file, index):
        binary_string = bin(index)[2:]
        slen = len(binary_string)
        rbstr = ""
        if slen < 8:
            for _ in range(8 - slen - 1):
                binary_string = "0" + binary_string
            rbstr = "1" + binary_string
        else:
            nbs = ""
            cnt = 0
            q = 0
            used = False
            while q < slen:
                cnt += 1
                if cnt % 8 == 0:
                    if used:
                        nbs += '0'
                    else:
                        nbs += '1'
                else:
                    nbs += binary_string[q]
                    q += 1
            rbstr = nbs 
        blist = int(rbstr, 2).to_bytes(math.ceil(len(rbstr) / 8), 'big')
        file.write(blist)

    def compress(self):
        # self.clear()
        print(self.directoryPath)
        currentPath = os.getcwd()
        cp = join(currentPath, self.outputDirPath)
        os.mkdir(cp)
        folderNamesList = [f for f in os.listdir(self.directoryPath)]
        for i in folderNamesList:
            os.mkdir(join(cp, i))
        # print(folderNamesList)
        for d in os.listdir(self.directoryPath):
            directory = join(self.directoryPath, d)
            print(directory)
            for f in os.listdir(directory):
                fileLocation = join(cp, d)
                fileLocation = join(fileLocation, f)
                inputFileLocation = join(directory, f)
                # inputFileLocation = join(currentPath, inputFileLocation)
                print(inputFileLocation)    
                self.lz78_compress(inputFileLocation, fileLocation)
    def checkLast(self, byte):
        if(bin(int.from_bytes(byte, 'big'))[2] == '1'):
            return True
        else:
            return False

    def byteToInt(self, byte):
        return int.from_bytes(byte, 'big')
    
    def bytesToInt(self, bytes):
        if(len(bytes) == 0):
            print("Something went wrong")
        # print(bytes)
        stringForm = ""
        for i in bytes:
            stringForm += ((bin(int.from_bytes(i, "big"))[3:])).zfill(8)
        # print(stringForm)
        return int(stringForm, 2)

    def readOneItem(self, file):
        bytesList = []
        while True:
            nextByte = file.read(1)
            if not nextByte:
                return None, None
            bytesList.append(nextByte)
            if self.checkLast(nextByte):
                index = self.bytesToInt(bytesList)
                symbol = file.read(1)
                return index, symbol

    def lz78_decompress(self, input, output):
        self.clear()
        self.mapping.append(None)
        print(output)
        # print(len(self.mapping)
        self.mapping.append(None)
        mlen = 1
        outputFile = open(output, "wb")
        with open(input, "rb") as f:
            while True:
                index, symbol = self.readOneItem(f)
                if index is None:
                    break
                # print(index, symbol)
                if index >= mlen:
                    raise Exception("Wrong input file. Input file might not be compressed with LZ78")
                prefix = self.mapping[index]
                result = None
                if prefix is None:
                    result = symbol
                else:
                    result = prefix + symbol
                self.mapping.append(result)
                mlen += 1
                outputFile.write(result)
        outputFile.close()

    def decompress(self):
        self.clear()
        # currentPath = os.getcwd()
        # currentPath = join(currentPath, self.directoryPath)
        for d in os.listdir(self.directoryPath):
            directory = join(self.directoryPath, d)
            for f in os.listdir(directory):
                filePath = join(directory, f)
                name, extension = os.path.splitext(f)
                outputFileName = name + "Decompressed" + extension
                outputPath = join(directory, outputFileName)
                self.lz78_decompress(filePath, outputPath)

if __name__ == "__main__":    
    sys.setrecursionlimit(10000)
    lz78_c = LZ78("dataset_small", "output")
    lz78_d = LZ78("output")
    lz78_c.compress()
    lz78_d.decompress()

