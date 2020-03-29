import cv2


def getFileSize(filename):
    img = cv2.imread(filename)
    size = img.size
    print("Size of this file (B): ", size)


def getFileShape(filename):
    img = cv2.imread(filename)
    shape = img.shape
    print("Shape of this file (Height, Width, Number of channels): ", shape)


def getIHDRInterpretation(filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    chunkIHDR = fileInHex.find('49484452')

    colorDepthInHex=fileInHex[(chunkIHDR+24):(chunkIHDR+26)]
    colorDepthInDec=int(colorDepthInHex, 16)
    print("Color depth of this file is: ", colorDepthInDec)


testFile='images/testFile1.png'
getFileSize(testFile)
getFileShape(testFile)
getIHDRInterpretation(testFile)
