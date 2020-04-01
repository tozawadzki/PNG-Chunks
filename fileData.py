import cv2


def getFileData(filename):
    getFileSize(filename)
    getFileShape(filename)


def getFileSize(filename):
    img = cv2.imread(filename)
    size = img.size
    print("Size of this file (B): ", size)


# using cv2 library instead of IHDR interpretation
def getFileShape(filename):
    img = cv2.imread(filename)
    shape = img.shape
    print("Shape of this file (Height, Width, Number of channels): ", shape)


# https://www.w3.org/TR/PNG-Chunks.html
# Width: 4 bytes (expressed by getFileShape)
# Height: 4 bytes (expressed by getFileShape)
# Bit depth:          1 byte (1)
# Color type:         1 byte (2)
# Compression method: 1 byte (3)
# Filter method:      1 byte (4)
# Interlace method:   1 byte (5)
def getIHDRData(filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    chunkIHDR = fileInHex.find('49484452')

    # (1)
    colorDepthInHex = fileInHex[(chunkIHDR + 24):(chunkIHDR + 26)]
    colorDepthInDec = int(colorDepthInHex, 16)
    print("Color depth of this image equals: ", colorDepthInDec)

    # (2)
    colorTypeInHex = fileInHex[(chunkIHDR + 26):(chunkIHDR + 28)]
    colorTypeInDec = int(colorTypeInHex, 16)
    print("Color type of this file: ",
          {
              0: "A grayscale sample",
              2: "An RGB triple (truecolour)",
              3: "A palette index (indexed-colour)",
              4: "A grayscale sample, followed by an alpha sample",
              6: "An RGB triple, followed by an alpha sample"
          }.get(colorTypeInDec, colorTypeInDec))

    # (3) w3.org disclaimer -> "At present, only compression method 0 (deflate/inflate compression with a 32K sliding window) is defined."
    compressionMethodInHex = fileInHex[(chunkIHDR + 28):(chunkIHDR + 30)]
    compressionMethodInDec = int(compressionMethodInHex, 16)
    print("Compression method in this file: ",
          {
              0: "Deflate/inflate"
          }.get(compressionMethodInDec, compressionMethodInDec))

    # (4) https://www.w3.org/TR/PNG-Filters.html
    filterMethodInHex = fileInHex[(chunkIHDR + 30):(chunkIHDR + 32)]
    filterMethodInDec = int(filterMethodInHex, 16)
    print("Filter method in this file:",
          {
              0: "None",
              1: "Sub",
              2: "Up",
              3: "Average",
              4: "Paeth"
          }.get(filterMethodInDec, filterMethodInDec))

    # (5) https://www.w3.org/TR/PNG-DataRep.html#DR.Interlaced-data-order
    interlaceMethodInHex = fileInHex[(chunkIHDR + 32):(chunkIHDR + 34)]
    interlaceMethodInDec = int(interlaceMethodInHex, 16)
    print("Interlace method in this file:",
          {
              0: "No interlace",
              1: "Adam7 interlace"

          }.get(interlaceMethodInDec, interlaceMethodInDec))


testFile = 'images/testFile1.png'
getFileData(testFile)
getIHDRData(testFile)
