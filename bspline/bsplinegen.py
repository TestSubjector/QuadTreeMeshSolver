import numpy as np
import scipy.interpolate as si
import matplotlib.pyplot as plt
from scipy.interpolate import splprep, splev

# cv: Input array of the body
# point_division: Number of new points required between given point indexes
# index1: First point index
# index2: Second point index

def bsplineCall(cv, point_division, index1, index2):
    # plt.plot(cv[:,0],cv[:,1], 'o-', label='Control Points')

    # tck : A tuple (t,c,k) containing the vector of knots, the B-spline coefficients, and the degree of the spline
    # u : The weighted sum of squared residuals of the spline approximation.
    tck, u = splprep([cv[:,0], cv[:,1]], s=0)
    
    generated_points = [] 
    update = 0
    while len(generated_points) < point_division:
        generated_points.clear()
        update = update + 1
        u_new = np.linspace(u.min(), u.max(), len(cv)*(update + point_division))

        new_points = splev(u_new, tck, der = 0)
        for i in range(len(new_points[0])):
            # The cv[x] represents point index (subtracted by one) in between which the new generated points are found 
            if (cv[index1][0] <= new_points[0][i]) and (new_points[0][i] <= cv[index2][0]):
                generated_points.append([new_points[0][i], new_points[1][i]])
                # print(new_points[0][i], new_points[1][i])
    else:
        None
        # for i in generated_points:
        #     print(i)
        # print(update)

    # plt.plot(new_points[0], new_points[1], 'o-', label = 'direction point')

    # plt.minorticks_on()
    # plt.legend()
    # plt.xlabel('x')
    # plt.ylabel('y')
    # plt.xlim(-0.1, 1.1)
    # plt.ylim(-0.1, 0.1)
    # plt.gca().set_aspect('equal', adjustable='box')
    # plt.show()
    return generated_points