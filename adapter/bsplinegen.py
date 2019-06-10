import numpy as np
import scipy.interpolate as si
import matplotlib.pyplot as plt
import math
from scipy.interpolate import splprep, splev
from scipy import spatial
import config
import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from core import core

# cv: Input array of the body
# point_division: Number of new points required between given point indexes
# index1: First point index
# index2: Second point index

def angle(x1, y1, x2, y2, x3, y3):
    a = np.array([x1, y1])
    b = np.array([x2, y2])
    c = np.array([x3, y3])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

def distance(ax,ay,bx,by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def typeObtuseRightAcute(x1, y1, x2, y2, x3, y3):
    #no idea if this is a good value but works for example
    #and should be low enough to give right answers for all but crazy close triangles

    # Using Pythagoras theorem
    sideAB = distance(x1, y1, x2, y2)
    sideBC = distance(x2, y2, x3, y3)
    sideAC = distance(x3, y3, x1, y1)

    [var1, var2, largest] = sorted([sideAB, sideBC, sideAC])

    if largest == sideAC and (largest) ** 2 > ((var1 ** 2 + (var2) ** 2)):
        return 1
    else:
        return 0

def bsplineCall(cv, point_division, index1, index2):
    cv = np.concatenate((cv, [cv[0]]), axis = 0)
    # plt.plot(cv[:,0],cv[:,1], 'o-', label='Control Points')

    if(index1 > len(cv) or index2 > len(cv)):
        exit("ERROR: Index not in range")

    # tck : A tuple (t,c,k) containing the vector of knots, the B-spline coefficients, and the degree of the spline
    # u : The weighted sum of squared residuals of the spline approximation.
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)

    generated_points = [] 
    update = 2000
    while len(generated_points) < point_division and update < 100000:
        # print(update)
        generated_points.clear()
        u_new = np.linspace(u.min(), u.max(), (update + point_division)*(len(cv)))
        if update < 300:
            update = update + 1
        elif update < 2000:
            update = update + 100
        else:
            update = update + 1000
        new_points = splev(u_new, tck, der = 0)

        for i in range(len(new_points[0])):
            # The cv[x] represents point index (subtracted by one) in between which the new generated points are found 
            if (typeObtuseRightAcute(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1])== 1):
                if(angle(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1]) > 170 and 
                    angle(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1]) < 190):
                    generated_points.append([new_points[0][i], new_points[1][i]])
                    # print(new_points[0][i], new_points[1][i])
    else:
        None
        # print(update)

    # plt.plot(new_points[0], new_points[1], 'o-', label = 'direction point')

    # plt.minorticks_on()
    # plt.legend()
    # plt.xlabel('x')
    # plt.ylabel('y')
    # # plt.xlim(-0.1, 1.1)
    # # plt.ylim(-0.1, 0.1)
    # # plt.gca().set_aspect('equal', adjustable='box')
    # plt.show()
    return generated_points

def generateBSplinePoints(cv,update):
    cv = np.concatenate((cv, [cv[0]]), axis = 0)
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)
    u_new = np.linspace(u.min(), u.max(), update*len(cv))
    new_points = splev(u_new, tck, der = 0)
    return new_points

def generateBSplineBetween(cv,index1,index2, num_points = 20):
    cv = np.concatenate((cv, [cv[0]]), axis = 0)
    if index2 == 0:
        None
        index2 = len(cv) - 1
    if(index1 > len(cv) or index2 > len(cv)):
        exit("ERROR: Index not in range")
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)
    u_new = np.linspace(u[index1], u[index2], num_points)
    new_points = splev(u_new, tck, der = 0)
    new_points = convertPointsToNicePoints(new_points)
    new_points.pop(0)
    new_points.pop(-1)
    return new_points

def convertPointsToKdTree(points):
    return spatial.cKDTree(list(zip(points[0].ravel(), points[1].ravel())))

def convertPointsToNicePoints(bsplineData):
    return list(zip(bsplineData[0].ravel(), bsplineData[1].ravel()))

def getPointsBetween(kdTree,startx,stopx):
    startx = tuple(map(float,startx.split(",")))
    stopx = tuple(map(float,stopx.split(",")))
    startrg = kdTree.query(np.array(startx))[1]
    stoprg = kdTree.query(np.array(stopx))[1]
    result = kdTree.data[startrg:stoprg]
    return verifyPointsBetween(result.tolist(),startx,stopx)

def verifyPointsBetween(search_list,startpt,stoppt):
    generated_points = []
    for i in range(len(search_list)):
        if (typeObtuseRightAcute(startpt[0], startpt[1], search_list[i][0],search_list[i][1], stoppt[0], stoppt[1])== 1):
            if(angle(startpt[0], startpt[1], search_list[i][0],search_list[i][1], stoppt[0], stoppt[1]) > 170 and 
                angle(startpt[0], startpt[1], search_list[i][0],search_list[i][1], stoppt[0], stoppt[1]) < 190):
                generated_points.append([search_list[i][0], search_list[i][1]])
    return generated_points

def getPointsBetween2(bsplineData,startx,stopx):
    startx = tuple(map(float,startx.split(",")))
    stopx = tuple(map(float,stopx.split(",")))
    startrg = spatial.distance.cdist(np.array(bsplineData),np.array([startx]),"euclidean").argmin()
    stoprg = spatial.distance.cdist(np.array(bsplineData),np.array([stopx]),"euclidean").argmin()
    if startrg > stoprg:
        startrg,stoprg = stoprg,startrg
    result = bsplineData[startrg:stoprg]
    return verifyPointsBetween(result,startx,stopx)