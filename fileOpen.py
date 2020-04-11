import cv2


def displayImage(filename):
    img = cv2.imread(filename)
    cv2.imshow('PNG Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def saveFileInHex(pngInHexFilename, filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    text_file = open(pngInHexFilename, 'w')
    n = text_file.write(fileInHex)
    text_file.close()
    print("Hex version of this file has been saved to given file")
    file.close()

def showFileInHex(filename):
    file = open(filename, 'rb')
    fileInHex = file.read().hex()
    print("Hex version of this file: ", fileInHex)
    file.close()


#displayImage('images/s03n3p01.png')
#saveFileInHex('hexFile3x3.txt', 'images/s03n3p01.png')
