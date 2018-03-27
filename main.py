#!/usr/bin/env python
# encoding: utf-8
from optparse import OptionParser
import cv2
import sys  
import numpy as np
import os
import fnmatch
import re
import threading
import Queue
import time



reload(sys)  
sys.setdefaultencoding('utf8')

parser = OptionParser()

parser.add_option("-v", "--version", action="store_true", dest="version", default=True)
parser.add_option("-i", "--input", dest="input", default="/tmp/data/*.png",
                        help="Wildcard pattern to all samples", metavar="INPUT")
parser.add_option("-t", "--thread_count", dest="threadCount", default=4,
                        type="int", help="Number of threads that will be used to calculate result image", metavar="THREADS")
parser.add_option("-s", "--start", dest="startImage", default=800,
                        type="int", help="Start image number in sequence", metavar="START_IMG")
parser.add_option("-e", "--end", dest="endImage", default=1900,
                        type="int", help="Start image number in sequence", metavar="END_IMG")
parser.add_option("-d", "--threshold", dest="threshold", default=120,
                        type="int", help="Threshold value", metavar="THRESHOLD")
parser.add_option("-m", "--median_kernel", dest="medianKernel", default=3,
                        type="int", help="Size of median kernel", metavar="KERNEL")


(options, args) = parser.parse_args()


def showImage(img):
    cv2.imshow("result", img)
    retval = (cv2.waitKey(0))
    cv2.destroyAllWindows()
    return retval


def getPathsByWildcard(path):
    dirPath = path[0:path.rfind('/')+1]
    pattern = path[path.rfind('/')+1:]
    retval = []
    for fileName in os.listdir(dirPath):
        if (fnmatch.fnmatch(fileName, pattern)):
            number = int(re.search('\\d+', fileName).group(0))
            if number > options.startImage and number < options.endImage:
                retval.append(dirPath + fileName)
    return retval


def loadImage(path):
    retval  = cv2.imread(path)
    return retval


def imageToGrayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


def thresholdImage(img):
    ret, thresh = cv2.threshold(img, options.threshold, 255, cv2.THRESH_BINARY)
    return thresh


def initResultImage(img):
    return img


class AddImagesThread(threading.Thread):
    args = ()
    def __init__(self, threadID, name, counter, args):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.args = args


    def run(self):#imgPaths, results):
        resultImg = None
        for path in self.args[0]:
            img = loadImage(path)
            img = imageToGrayscale(img)
            img = thresholdImage(img)
            if resultImg == None:
                resultImg = initResultImage(img)

            resultImg = cv2.add(img, resultImg)
            #if 113 == showImage(resultImg):
            #    break
            #break
        self.args[1].put(resultImg)


if __name__ == '__main__':
    time1 = time.time()
    imgPaths = getPathsByWildcard(options.input)
    resultImg = None

    results = Queue.Queue()

    threads = []

    # count number of started threads
    #for i in range(options.threadCount):
    #    threads.append(thread.start_new_thread(addImages, (imgPaths[i*len(imgPaths)/options.threadCount:(i+1)*len(imgPaths)/options.threadCount], results)))
    for i in range(options.threadCount):
        thrArgs = (imgPaths[i*len(imgPaths)/options.threadCount:(i+1)*len(imgPaths)/options.threadCount], results)
        thr = AddImagesThread(i, "thread-" + str(i), i, thrArgs)
        threads.append(thr)
        thr.start()

    # count stopped threads

    # if started threads count == stopped threads
    for t in threads:
        t.join()

    #showImage(results.get())

    resultImg = results.get()
    #showImage(resultImg)

    while not results.empty():
        img = results.get()
        #showImage(img)
        resultImg = cv2.add(resultImg, img)


    resultImg = cv2.medianBlur(resultImg, options.medianKernel)
    ret, resultImg = cv2.threshold(resultImg, 127, 255, cv2.THRESH_BINARY)
    showImage(resultImg)
    cv2.imwrite('result.png', resultImg)
    time2 = time.time()
    print time2 - time1



