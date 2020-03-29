import cv2

def displayImage(filename):
    img = cv2.imread(filename)
    cv2.imshow('PNG Image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def printFileInHex(filename):
    handler = open(filename, 'rb')
    hexFile = handler.read().hex()
    print(hexFile)
    handler.close()

displayImage('images/testFile1.png')
printFileInHex('images/testFile1.png')
