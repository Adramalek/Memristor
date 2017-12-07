from utils import waiter
from time import sleep
import cv2


@waiter('Start wasting time', 'Finish wasting time')
def waste_time(tm):
    sleep(tm)


def cam_test():
    cap = cv2.VideoCapture(0)
    while True:
        ret, img = cap.read()
        if ret:
            img = cv2.flip(img, -1)
            cv2.imshow('cap', img)
            k = cv2.waitKey(33)
            if k == ord('a'):
                cv2.imshow('img', img)
                cv2.imwrite('test.png', img)
            if k == ord('q'):
                break
    cap.release()
    cv2.destroyAllWindows()


def extract_digits(img_path):
    img = cv2.imread(img_path, 1)
    cv2.imshow('Original', img)
    while True:
        k = cv2.waitKey(33)
        if k == ord('g'):
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            ret, threshold = cv2.threshold(blur, 100, 255, cv2.THRESH_TRUNC)
            threshold = cv2.adaptiveThreshold(threshold, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 1)
            cv2.imshow('Threshold', threshold)
            k = cv2.waitKey(33)
        if k == ord('q'):
            cv2.destroyAllWindows()
            break
    pass


if __name__ == '__main__':
    cam_test()
    # extract_digits('test.png')
    pass
