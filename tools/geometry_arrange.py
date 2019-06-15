from math import acos
import argparse


def main():
	
	#need to input intpt and arr!

	parser = argparse.ArgumentParser()
	parser.add_argument("out", help="specify output file destination")
	args = parser.parser_args()

	x0 = intpt[0]
	y0 = intpt[1]
	
	new_arr = [arr[0]]
	arr.pop(0)

	for (x1, y1) in new_arr:

		if arr == []:
			break
		else:
			minimum = 6.1
			new_pt = None
			for (idx, (x2, y2)) in enumerate(arr):
				angle = angle_between(x1-x0, y1-y0, x2-x0, y2-y0)
				if angle < minimum and cross_product(x1-x0, y1-y0, x2-x0, y2-y0) > 0:
					minimum = angle
					new_pt = (x2, y2)
			new_arr.append((x2, y2))
			arr.pop(idx)
	
	choice = input("Please specify 'cw' or 'ccw': ")

	if choice == 'cw':
		temp = new_arr[0]
		new_arr.pop(0)
		new_arr.reverse()
		new_arr.insert(0, temp)

	file = open(args.out, "w+")

	for pt in new_arr:
		file.write(str(pt[0]) + "\t" + str(pt[1]) + "\n")

	def angle_between(x1, y1, x2, y2):
		return acos((x1*x2 + y1*y2) / ((x1**2 + y1**2) + (x2**2 + y2**2)) ** 0.5)

	def cross_product(x1, y1, x2, y2):
		return x1*y2 - x2*y1

if __name__ == "__main__":
	main()