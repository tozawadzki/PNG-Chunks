import zlib
import cv2
import struct
import matplotlib.pyplot as plt
import numpy as np
import png
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from fileActions import executeNumpyFourierTransform, executeOpenCVFourierTransform, removeAncillaryChunks
from fileOpen import displayImage, showFileInHex

IHDR = '49484452'
IDAT = '49444154'
IEND = '49454e44'
PLTE = '504c5445'
CHRM = '6348524d'
TIME = '74494d45'

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

def getTIMEdata(filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    chunkTIME = fileInHex.find(TIME)

    print("\nTIME chunk data:\n")
    yearInHex = fileInHex[(chunkTIME + 8):(chunkTIME + 12)]
    yearInDec = int(yearInHex, 16)
    print("Year: ", yearInDec)

    monthInHex = fileInHex[(chunkTIME + 12):(chunkTIME + 14)]
    monthInDec = int(monthInHex, 16)
    print("Month: ", monthInDec)

    dayInHex = fileInHex[(chunkTIME + 14):(chunkTIME + 16)]
    dayInDec = int(dayInHex, 16)
    print("Day: ", dayInDec)

    hourInHex = fileInHex[(chunkTIME + 16):(chunkTIME + 18)]
    hourInDec = int(hourInHex, 16)

    minuteInHex = fileInHex[(chunkTIME + 18):(chunkTIME + 20)]
    minuteInDec = int(minuteInHex, 16)

    secondInHex = fileInHex[(chunkTIME + 20):(chunkTIME + 22)]
    secondInDec = int(secondInHex, 16)
    print("Time:", hourInDec, ":", minuteInDec, ":", secondInDec)


def getCHRMdata(filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    chunkCHRM = fileInHex.find(CHRM)

    print("\nCHRM chunk data\n")
    whitePointXInHex = fileInHex[(chunkCHRM + 8):(chunkCHRM + 16)]
    whitePointXInDec = int(whitePointXInHex, 16)
    print("White Point x: ", whitePointXInDec/100000)

    whitePointYInHex = fileInHex[(chunkCHRM + 16):(chunkCHRM + 24)]
    whitePointYInDec = int(whitePointYInHex, 16)
    print("White Point y: ", whitePointYInDec/100000)

    redXInHex = fileInHex[(chunkCHRM + 24):(chunkCHRM + 32)]
    redXInDec = int(redXInHex, 16)
    print("Red x: ", redXInDec/100000)

    redYInHex = fileInHex[(chunkCHRM + 32):(chunkCHRM + 40)]
    redYInDec = int(redYInHex, 16)
    print("Red y: ", redYInDec/100000)

    greenXInHex = fileInHex[(chunkCHRM + 40):(chunkCHRM + 48)]
    greenXInDec = int(greenXInHex, 16)
    print("Green x: ", greenXInDec/100000)

    greenYInHex = fileInHex[(chunkCHRM + 48):(chunkCHRM + 56)]
    greenYInDec = int(greenYInHex, 16)
    print("Green y:", greenYInDec/100000)

    blueXInHex = fileInHex[(chunkCHRM + 56):(chunkCHRM + 64)]
    blueXInDec = int(blueXInHex, 16)
    print("Green x: ", blueXInDec/100000)

    blueYInHex = fileInHex[(chunkCHRM + 64):(chunkCHRM + 72)]
    blueYInDec = int(blueYInHex, 16)
    print("Green y:", blueYInDec/100000)

def getPLTEColors(filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    chunkPLTE = fileInHex.find(PLTE)

    print("\nPLTE chunk - amount of colors\n")

    #4 bytes before chunk - its length
    chunkPLTEBytesInHex = fileInHex[(chunkPLTE-8)]
    chunkPLTEBytesInDec = int(chunkPLTEBytesInHex, 16)
    colors = chunkPLTEBytesInDec/3
    print(colors)
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
    # 8
    # 16
    # 24
    # 24-26 -> 1 byte po 8 b
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

def getChunks(filename):
    img = png.Reader(filename)
    print("b'<nazwa_chunka>' <długość (bytes)>")
    for chunk in img.chunks():
        print(chunk[0], len(chunk[1]))

def getHachoirExifData(filename):
    parser = createParser(filename)
    metadata = extractMetadata(parser)
    print("Hachoir exif data below")
    for line in metadata.exportPlaintext():
        print(line)

def read_chunk(file):
    # Returns (chunk_type, chunk_data)
    chunk_length, chunk_type = struct.unpack('>I4s', file.read(8))
    chunk_data = file.read(chunk_length)
    chunk_expected_crc, = struct.unpack('>I', file.read(4))
    chunk_actual_crc = zlib.crc32(chunk_data, zlib.crc32(struct.pack('>4s', chunk_type)))
    if chunk_expected_crc != chunk_actual_crc:
        raise Exception('chunk checksum failed')
    return chunk_type, chunk_data

def number_of_pixel(filename):
    option = getIHDRData(filename)
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
    bytesPerPixel = number_of_pixel(filename)
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
                Recon_x = Filt_x + paethPredictor(Recon_a(r, c), Recon_b(r, c), Recon_c(r, c))
            else:
                raise Exception('unknown filter type: ' + str(filter_type))
            Recon.append(Recon_x & 0xff)  # truncation to byte
    print(np.array(Recon).reshape((height, width,bytesPerPixel)))
    return Recon,height,width
    #plt.imshow(np.array(Recon).reshape((height, width,3)))
    #plt.show()

def paethPredictor(a, b, c):
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

def showImage(filename):
    Recon,height,width = getIDAT(filename)
    option = getIHDRData(filename)
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

def startMenu():
    print("Program PNGChunks")
    print("Daniel Jabłoński i Tomasz Zawadzki")
    print("Politechnika Wrocławska 2020")
    print("Prowadzący: dr Andrzej Gnatowski")
    filename = input("Wprowadź ścieżkę do pliku:")
    print("Ścieżka do pliku: ", filename)
    loop = 1
    while loop == 1:
        decision = input("""
            I - Wyświetl podstawowe informacje o pliku
            F - Transformata Fouriera
            H - Wyświetl informacje o pliku na podstawie IHDR
            Y - Usuń ancillary chunks z pliku
            D - Wyświetl interpretację IDAT
            A - Ancillary Chunks
            P - Ilość kolorów (PLTE)
            S - Wyświetl obrazek
            X - Przedstaw plik w surowym hex  
            C - Wyświetl wszystkie chunki oraz ich długości
            Q - Wyjdź     
        Wybór: """)
        choice = decision.upper()
        print("Wpisałeś: ", decision)
        if choice == "I":
            getFileData(filename)
        elif choice =="F":
            fourierType = input("""
                N - NumPy Fourier Transform
                C - OpenCV Fourier Transform
            Wybór: """)
            fourierType.upper()
            if fourierType == "N":
                executeNumpyFourierTransform(filename)
            elif fourierType == "C":
                executeOpenCVFourierTransform(filename)
        elif choice == "H":
            getIHDRData(filename)
        elif choice == "Y":
            removeAncillaryChunks(filename)
        elif choice == "D":
            showImage(filename)
        elif choice == "P":
            getPLTEColors(filename)
        elif choice == "A":
            exifInfoType = input("""
                E - EXIF
                C - CHRM
                T - TIME
            Wybór: """)
            exifInfoType.upper()
            if exifInfoType == "E":
                getHachoirExifData(filename)
            elif exifInfoType == "C":
                getCHRMdata(filename)
            elif exifInfoType == "T":
                getTIMEdata(filename)
        elif choice == "S":
            displayImage(filename)
        elif choice == "X":
            showFileInHex(filename)
        elif choice == "C":
            getChunks(filename)
        elif choice == "Q":
            loop = 0
    exit(0)

filename = 'images/test.png'
# exifFile = 'images/exifSquare.png'
# getFileData(testFile)
# getIHDRData(testFile)
# getIDAT(testFile)
# getPyPngExifData(exifFile)
# getPillowExifData(exifFile)
# getHachoirExifData(exifFile)
# showImage(filename)
startMenu()
# getChunks(filename)
# getTIMEdata(filename)
# getPLTEColors(filename)
# getCHRMdata(filename)
