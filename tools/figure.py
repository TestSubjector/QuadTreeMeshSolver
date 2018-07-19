from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

def main():
    someX, someY = 2, 3
    currentAxis = plt.gca()
    currentAxis.add_patch(Rectangle((someX - .5, someY - .5), 1, 1, facecolor="grey"))
    currentAxis.show()

if __name__ == "__main__":
    main()