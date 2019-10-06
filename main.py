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
        if value in self.children.keys():
            return self.children[value]
        else:
            return None
    

class LZ78Compressor:
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
        return self.mapping[node.getIndex() - 1]

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
        if ret == 1:
            inputs.clear()
            self.next_index = self.next_index + 1

    def lz78_compress(self, inputPath, outputPath):
        self.clear()
        inputs = []
        with open(inputPath, 'rb') as f:
            while True:
                binary_input = f.read(1)
                if not binary_input:
                    break
                decimal_input = int.from_bytes(binary_input, 'big')
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
        last = True
        ans = ""
        if index == 0:
            file.write(int(128).to_bytes(1, 'big'))
            return
        while index > 0:
            offset = index % 128
            index = index // 128
            if last:
                last = False
                ans = (bin(offset + 128)[2:]) + ans
            else:
                ans = (bin(offset)[2:]).zfill(8) + ans
        
        number = int(ans, 2)
        bstring = number.to_bytes((len(ans) + 7) // 8, 'big')
        file.write(bstring)

    def compress(self):
        currentPath = os.getcwd()
        cp = join(currentPath, self.outputDirPath)
        os.mkdir(cp)
        folderNamesList = [f for f in os.listdir(self.directoryPath)]
        for i in folderNamesList:
            os.mkdir(join(cp, i))
        for d in os.listdir(self.directoryPath):
            directory = join(self.directoryPath, d)
            for f in os.listdir(directory):
                fileLocation = join(cp, d)
                fileLocation = join(fileLocation, f)
                inputFileLocation = join(directory, f)
                self.lz78_compress(inputFileLocation, fileLocation)
    
class LZ78Decompressor:
    def __init__(self, directoryPath):
        self.directoryPath = directoryPath
        self.root = Node(index=0)
        self.mapping = []
        self.next_index = 1
    
    def clear(self):
        self.root = Node(index=0)
        self.mapping = []
        self.next_index = 1

    def checkLast(self, byte):
        return (int.from_bytes(byte, 'big') > 127)

    def byteToInt(self, byte):
        return int.from_bytes(byte, 'big')
    
    def bytesToInt(self, bytes):
        if(len(bytes) == 0):
            print("Something went wrong")
        stringForm = ""
        for i in bytes:
            stringForm += (((bin(int.from_bytes(i, "big"))[2:]).zfill(8))[1:])
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
        mlen = 1
        outputFile = open(output, "wb")
        with open(input, "rb") as f:
            while True:
                index, symbol = self.readOneItem(f)
                if index is None:
                    break
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
    lz78_c = LZ78Compressor("dataset_small", "output")
    lz78_d = LZ78Decompressor("output")
    lz78_c.compress()
    lz78_d.decompress()
    