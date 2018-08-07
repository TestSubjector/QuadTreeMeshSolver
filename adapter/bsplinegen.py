import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.interpolate import splprep, splev

# cv: Input array of the body
# point_division: Number of new points required between given point indexes
# index1: First point index
# index2: Second point index

def distance(ax,ay,bx,by):
    return math.sqrt((ax - bx)**2 + (ay - by)**2)

def distance2(ax,bx,ay,by):
    return distance(ax,ay,bx,by)

def typeObtuseRightAcute(x1, y1, x2, y2, x3, y3):
    #no idea if this is a good value but works for example
    #and should be low enough to give right answers for all but crazy close triangles

    epsilon = 1e-15

    # Using Pythagoras theorem
    sideAB = distance(x1, y1, x2, y2)
    sideBC = distance(x2, y2, x3, y3)
    sideAC = distance(x3, y3, x1, y1)

    [var1, var2, largest] = sorted([sideAB, sideBC, sideAC])

    if abs((largest) ** 2-((var1 ** 2 + (var2) ** 2))) < epsilon:
        return 1
    elif (largest) ** 2 > ((var1 ** 2 + (var2) ** 2)):
        return 0
    else:
        return 1

def bsplineCall(cv, point_division, index1, index2):
    plt.plot(cv[:,0],cv[:,1], 'o-', label='Control Points')

    if(index1 > len(cv) or index2 > len(cv)):
        exit("ERROR: Index not in range")

    # tck : A tuple (t,c,k) containing the vector of knots, the B-spline coefficients, and the degree of the spline
    # u : The weighted sum of squared residuals of the spline approximation.
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)

    generated_points = [] 
    update = 0
    while len(generated_points) < point_division and update < 10000:
        generated_points.clear()
        u_new = np.linspace(u.min(), u.max(), (update + point_division)*(len(cv))*(1/len(str(len(cv)))))
        if update < 1000:
            update = update + 1
        else:
            update = update + 100
        new_points = splev(u_new, tck, der = 0)

        for i in range(len(new_points[0])):
            # The cv[x] represents point index (subtracted by one) in between which the new generated points are found 
            if ((typeObtuseRightAcute(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1])== 1) and
                distance(cv[index1][0], cv[index1][1], new_points[0][i],new_points[1][i]) < distance(cv[index1][0], cv[index1][1], cv[index2][0], cv[index2][1]) and
                distance(new_points[0][i],new_points[1][i], cv[index2][0], cv[index2][1]) < distance(cv[index1][0], cv[index1][1], cv[index2][0], cv[index2][1])):

                generated_points.append([new_points[0][i], new_points[1][i]])
                # print(new_points[0][i], new_points[1][i])

    plt.plot(new_points[0], new_points[1], 'o-', label = 'direction point')

    plt.minorticks_on()
    plt.legend()
    plt.xlabel('x')
    plt.ylabel('y')
    # plt.xlim(-0.1, 1.1)
    # plt.ylim(-0.1, 0.1)
    # plt.gca().set_aspect('equal', adjustable='box')
    plt.show()
    return generated_points
    
    

if __name__ == "__main__":
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')

    cv = np.array([[0.10000000E+01, -0.38788960E-15],
    [0.92062677E+00, -0.10728153E-01],
    [0.70770751E+00, -0.34948589E-01],
    [0.42884258E+00, -0.56154724E-01],
    [0.17256963E+00, -0.55125874E-01],
    [0.20253513E-01, -0.23622473E-01],
    [0.20253513E-01, 0.23622473E-01],
    [0.17256963E+00, 0.55125874E-01],
    [0.42884258E+00, 0.56154724E-01],
    [0.70770751E+00, 0.34948589E-01]])

    cv = np.concatenate((cv, [cv[0]]), axis = 0)

    print(bsplineCall(cv, 4, 0, 1))
