import cv2
import math
import recognize_digits


def segment(seg):
    length = len(seg)
    result = False
    if length == 4 or length == 5:
        result = True
        for i in range(-1, length-1):
            point0 = seg[i-1]
            point1 = seg[i]
            point2 = seg[i+1]
            k1 = (point0[1]-point1[1])/(point0[0]-point1[0])
            k2 = (point1[1]-point2[1])/(point1[0]-point2[0])
            result &= True if k1*k2 == -1 else math.tan(abs((k2-k1)/(1+k2*k1))) == math.tan(math.pi/4)
    return result


if __name__ == '__main__':
    image = cv2.imread('C:\\Users\\User\\Downloads\\test.jpg')

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 200, 200)

    cv2.imshow('preproc', edged)
    cv2.waitKey(0)

    im, cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    digits = []

    for cnt in cnts:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4:
            if segment(approx):
                digits.append(cnt)

    cv2.drawContours(image, digits, -1, (0, 255, 0), 3)
    cv2.imshow('counters', image)
    cv2.waitKey(0)
