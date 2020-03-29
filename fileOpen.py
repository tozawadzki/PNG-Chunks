import cv2


def displayImage(filename):
    img = cv2.imread(filename)
    cv2.imshow('PNG Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def saveFileInHex(filename, pngFile):
    file = open(pngFile, 'rb')
    fileInHex = file.read().hex()
    text_file = open(filename, 'w')
    n = text_file.write(fileInHex)
    text_file.close()
    print(fileInHex)
    file.close()


displayImage('images/testFile1.png')
saveFileInHex('hexFile.txt', 'images/testFile1.png')
