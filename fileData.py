import zlib
import cv2
import struct
import matplotlib.pyplot as plt
import numpy as np

IHDR = '49484452'
IDAT = '49444154'
IEND = '49454e44'

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
    chunkIHDR = fileInHex.find(IHDR)

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
    return colorTypeInDec

def read_chunk(file):
    # Returns (chunk_type, chunk_data)
    chunk_length, chunk_type = struct.unpack('>I4s', file.read(8))
    chunk_data = file.read(chunk_length)
    chunk_expected_crc, = struct.unpack('>I', file.read(4))
    chunk_actual_crc = zlib.crc32(chunk_data, zlib.crc32(struct.pack('>4s', chunk_type)))
    if chunk_expected_crc != chunk_actual_crc:
        raise Exception('chunk checksum failed')
    return chunk_type, chunk_data

def number_of_pixel():
    option = getIHDRData(testFile)
    if option==0:
        return 1
    elif option==2:
        return 3
    elif option==3:
        return 1
    elif option==4:
        return 2
    elif option==6:
        return 4

def getIDAT(filename):
    file = open(filename, 'rb')
    PngSignature = b'\x89PNG\r\n\x1a\n'
    file.read(len(PngSignature))
    chunks = []
    ##############################
    #Reading chunks
    while True:
        chunk_type, chunk_data = read_chunk(file)
        chunks.append((chunk_type, chunk_data))
        if chunk_type == b'IEND':
            break
    #Merging IDAT chunks
    IDAT_data = b''.join(chunk_data for chunk_type, chunk_data in chunks if chunk_type == b'IDAT')
    IDAT_data = zlib.decompress(IDAT_data)
    ###########################################################
    #Reconstructing IDAT chunks
    _, IHDR_data = chunks[0]  # IHDR is always first chunk
    width, height, bitd, colort, compm, filterm, interlacem = struct.unpack('>IIBBBBB', IHDR_data)
    Recon = []
    bytesPerPixel = number_of_pixel()
    stride = width * bytesPerPixel
    def Recon_a(r, c):
        return Recon[r * stride + c - bytesPerPixel] if c >= bytesPerPixel else 0
    def Recon_b(r, c):
        return Recon[(r - 1) * stride + c] if r > 0 else 0
    def Recon_c(r, c):
        return Recon[(r - 1) * stride + c - bytesPerPixel] if r > 0 and c >= bytesPerPixel else 0

    i = 0
    for r in range(height):  # for each scanline
        filter_type = IDAT_data[i]  # first byte of scanline is filter type
        i += 1
        for c in range(stride):  # for each byte in scanline
            Filt_x = IDAT_data[i]
            i += 1
            if filter_type == 0:  # None
                Recon_x = Filt_x
            elif filter_type == 1:  # Sub
                Recon_x = Filt_x + Recon_a(r, c)
            elif filter_type == 2:  # Up
                Recon_x = Filt_x + Recon_b(r, c)
            elif filter_type == 3:  # Average
                Recon_x = Filt_x + (Recon_a(r, c) + Recon_b(r, c)) // 2
            elif filter_type == 4:  # Paeth
                Recon_x = Filt_x + PaethPredictor(Recon_a(r, c), Recon_b(r, c), Recon_c(r, c))
            else:
                raise Exception('unknown filter type: ' + str(filter_type))
            Recon.append(Recon_x & 0xff)  # truncation to byte
    print(np.array(Recon).reshape((height, width,bytesPerPixel)))
    return Recon,height,width
    #plt.imshow(np.array(Recon).reshape((height, width,3)))
    #plt.show()

def PaethPredictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        Pr = a
    elif pb <= pc:
        Pr = b
    else:
        Pr = c
    return Pr

def ShowImage():
    Recon,height,width = getIDAT(testFile)
    option = getIHDRData(testFile)
    if option==0 or option==3:
        plt.imshow(np.array(Recon).reshape((height, width)))
        plt.show()
    elif option==2:
        plt.imshow(np.array(Recon).reshape((height, width, 3)))
        plt.show()
    elif option==6:
        plt.imshow(np.array(Recon).reshape((height, width, 4)))
        plt.show()
    else:
        print("Not yet implemented")


testFile = 'images/testFile2.png'
getFileData(testFile)
getIHDRData(testFile)
getIDAT(testFile)
ShowImage()
