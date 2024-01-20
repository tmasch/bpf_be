from classes import *
from dbactions import *
import requests
import numpy as np 
import cv2
import random as rng



def findImages(id):
    print("finding images")
    print(id)
    r=getRessourceFromDb(id)
    print(r["images"][0])
    i=r["images"][0]
    frames=processImage(i)
    updateImageWithFrames(id,0,frames)
    print("finding images done")
    r={"val" : "finding images done"}
    return(r)
    
    

def processImage(image):
    print(image)
    url=image["baseurl"]+"/full/full/0/default.jpg"
    print(url)
    filename="14.jpg"
    print("fetching image from web")
    response = requests.get(url)
    jpg=response.content
    image = np.asarray(bytearray(jpg), dtype="uint8") 
    print("decoding")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR) 
    print("writing")
    cv2.imwrite("input.jpg", image)
    frames=strategy1(image)
#    print(response.content)
    return(frames)


def strategy1(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("gray.jpg",gray)

    ksize=21
    blurred = cv2.GaussianBlur(gray, (ksize, ksize), 0)
    threshAd = cv2.adaptiveThreshold(blurred, 255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY_INV, 151, 10)

    drawing=image
    imh, imw = image.shape[:2]    
    print(imh,imw)
    minsize=int(imw/10)


    contours, hierarchy = cv2.findContours(threshAd, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    contours_poly = [None]*len(contours)
    boundRect = [None]*len(contours)
#    centers = [None]*len(contours)
#    radius = [None]*len(contours)
    frames=[]

    for i, c in enumerate(contours):
        lw=2
        color = (rng.randint(0,256), rng.randint(0,256), rng.randint(0,256))
        contours_poly[i] = cv2.approxPolyDP(c, 3, True)
        boundRect[i] = cv2.boundingRect(contours_poly[i])
#        centers[i], radius[i] = cv2.minEnclosingCircle(contours_poly[i])
#        print(i,boundRect[i])
#        im=src_gray
        x,y,w,h = cv2.boundingRect(c)
        d=0
#        ROI = thresh[y-d:y+h+d, x-d:x+w+d]
        plot=0
        if (int(boundRect[i][2]) > minsize and int(boundRect[i][3] > minsize)) : 
            plot=1
#            print(i,boundRect[i],hierarchy[0][i])
#            print(imw-(x+w))
#            print(imh-(y+h))
        # remove borders
            if (int(boundRect[i][0]) == 0):
                plot=0
#                print("left border")
                color=(255,0,255)
                lw=10
            if (int(boundRect[i][1]) == 0):
                plot=0
#                print("top border")
                color=(255,255,0)
                color=(255,0,255)
                lw=10
            if ( imh-(y+h) <= 1):
                plot=0
#                print("bottom border")
                color=(255,0,255)
                lw=10
            if ( imw-(x+w) <= 1):
                plot=0
#                print("right border")
                color=(255,0,255)
                lw=10
#            plot=1
            if (hierarchy[0][i][3] > 0):
                plot=0
#                print("inside other")
                color=(0,255,0)
    #            print(hierarchy[0][i])
    #            print(boundRect[i])
        if (plot == 1):
            print("found image ",i)
            color=(255,255,0)
            lw=30
            print(i,boundRect[i],hierarchy[0][i])
            f=Frame()
            f.index=i
            f.x_abs=x
            f.y_abs=y
            f.w_abs=w
            f.h_abs=h
            f.x_rel=x/imw
            f.y_rel=y/imh
            f.w_rel=w/imw
            f.h_rel=h/imh
            frames.append(f)
#            cv2.imwrite(image+'/ROI_{}_{}.png'.format(image,i), ROI)
#            cv2.imwrite('./images/ROI_{}_{}.png'.format(image,i), ROI)
#            print("sum",np.sum(ROI)/np.size(ROI))
        if (int(boundRect[i][2]) > 3 and int(boundRect[i][3] > 3)) : 
             d=0
             if (plot==1): 
                 d=10
             cv2.rectangle(drawing, (x-d , y-d),(x+w+d, y+h+d), color, lw)
             cv2.drawContours(drawing, contours_poly, i, color)	
    cv2.imwrite("contours.jpg",drawing)
    return(frames)
 
    
