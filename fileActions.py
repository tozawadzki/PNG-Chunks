from matplotlib import pyplot as plt
import cv2
import numpy as np


#####################
# FOURIER TRANSFORM #
#####################
# inspired by https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_imgproc/py_transforms/py_fourier_transform/py_fourier_transform.html
# https://docs.scipy.org/doc/numpy/reference/routines.fft.html
def executeNumpyFourierTransform(filename):
    img = cv2.imread(filename, 0)
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift))
    phase_spectrum = np.angle(fshift);
    plt.subplot(131), plt.imshow(img, cmap='gray')
    plt.title('Input Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(132), plt.imshow(magnitude_spectrum, cmap='gray')
    plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
    plt.subplot(133), plt.imshow(phase_spectrum, cmap='gray')
    plt.title('Phase'), plt.xticks([]), plt.yticks([])
    plt.show()


def executeOpenCVFourierTransform(filename):
    img = cv2.imread(filename, 0)

    dft = cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)

    magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))

    # cv2.cartToPolar()

    plt.subplot(121), plt.imshow(img, cmap='gray')
    plt.title('Input Image'), plt.xticks([]), plt.yticks([])
    plt.subplot(122), plt.imshow(magnitude_spectrum, cmap='gray')
    plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
    plt.show()


############################
# END OF FOURIER TRANSFORM #
############################

#############################
# REMOVING ANCILLARY CHUNKS #
#############################
def removeAncillaryChunks(filename):
    # ancillaryChunks = [bKGD, cHRM, gAMA, ..., zTXt ] -> chronology the same as in link below
    # https://www.rapidtables.com/convert/number/ascii-to-hex.html?fbclid=IwAR1bm7FkVGOjOrqGsBfq2vITBMSVRtWd7aKZeqmNcyDQeoCLoB2dOnCmZJs
    ancillaryChunks = ["624b4744", "6348524d", "64534947", "65584966", "67414d41",
                       "68495354", "69434350", "69545874", "70485973", "73424954",
                       "73504c54", "73524742", "73544552", "74455874", "74494d45",
                       "74524e53", "7a545874"]

    file = open(filename, 'rb')
    fileInHex = file.read().hex()

    chunkLength = 24

    for chunk in ancillaryChunks:
        position = fileInHex.find(chunk)
        if position != -1:
            chunkSizeInBytesInHex = fileInHex[(position - 8): position]
            chunkSizeInBytesInDec = int(chunkSizeInBytesInHex, 16)
            chunkSizeInDec = 2 * chunkSizeInBytesInDec
            begin = fileInHex[0:(position - 8)]
            end = fileInHex[(position - 8) + chunkSizeInDec + chunkLength:]
            fileInHex = begin + end
    file.close()
    print("Successfully removed ancillary chunks")
    return fileInHex
####################################
# END OF REMOVING ANCILLARY CHUNKS #
####################################

#executeNumpyFourierTransform('images/testFile2.png')
#executeOpenCVFourierTransform('images/testFile1.png')
#removeAncillaryChunks('images/testFile1.png')
####################################
# END OF REMOVING ANCILLARY CHUNKS #
####################################
