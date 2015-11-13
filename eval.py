import os
import os.path as path
import numpy as np
import cv2
import sys
import scipy.stats as stats
from shapely.geometry import Polygon
from shapely.geometry import Point

import util

def _poly(res):
	tl = (res[0], res[1])
	size = (res[2], res[3])

	pts = [tl, (tl[0] + size[0], tl[1]), (tl[0] + size[0], tl[1] + size[1]), (tl[0], tl[1] + size[1])]

	return Polygon(pts)

def _iou(res1, res2):
	roi1 = _poly(res1)
	roi2 = _poly(res2) 

	inter = roi1.intersection(roi2)
	overlap = inter.area / (roi1.area + roi2.area - inter.area)

	return overlap

def _iou_circle(res1, res2):
	r1 = max(res1[2], res1[3])/2
	r2 = max(res2[2], res2[3])/2
	p1 = Point(res1[0] + r1, res1[1] + r1).buffer(r1)
	p2 = Point(res2[0] + r2, res2[1] + r2).buffer(r2)

	return p1.intersection(p2).area / p1.union(p2).area

def _iou_circle(res1, res2):
	r1 = max(res1[2], res1[3])/2
	r2 = max(res2[2], res2[3])/2
	p1 = Point(res1[0] + r1, res1[1] + r1).buffer(r1)
	p2 = Point(res2[0] + r2, res2[1] + r2).buffer(r2)

	return p1.intersection(p2).area / p1.union(p2).area

def _dist(blob1, blob2):
	print blob1, blob2
	return (blob1[0] - blob2[0]) ** 2 + (blob1[1] - blob2[1]) ** 2


def _load_results(results_path, factor=1.0):
	fin = open(results_path)
	results = []
	for line in fin:
		toks = line.split(' ')
		name = toks[0]
		print name

		if len(toks) == 1:
			num_rois = 0
		else:
			num_rois = int(toks[1])

		results.append([])

		for i in range(num_rois):
			results[-1].append([])
			for j in range(4):
				results[-1][-1].append(int(factor * int(toks[2 + i * 4 + j])))
		print num_rois, len(results[-1])

	return results

def _get_paths(results_path):
	fin = open(results_path)
	paths = []

	for line in fin:
		toks = line.split(' ')
		paths.append(toks[0])

	return paths

def _show_real_predicted(path, res1, res2):
	img = np.load(path, 0)
	resized_img = cv2.resize(img, (512, 512), interpolation=cv2.INTER_CUBIC)
	color_img = cv2.cvtColor(resized_img.copy(), cv2.COLOR_GRAY2BGR) 
	print color_img.shape
	for res in res1:
		color_img = util.label_blob(color_img, res, (255, 0, 0))
	for res in res2:
		color_img = util.label_blob(color_img, res, (0, 255, 255))
	#util.imshow('real vs predicted', color_img)


def evaluate(real_path, predicted_path):
	paths, real = util.load_list(real_path)
	_, predicted = util.load_list(predicted_path)

	assert len(real) == len(predicted)

	num_imgs = len(real)
	sensitivity = 0
	fppi = []
	iou = []
	iou_pos = []
	tp = 0
	p = 0
	MAX_DIST = 35.7142 # 25 mm

	for i in range(num_imgs):
		found = False
		overlap = -1e10
		p += len(real[i])
		for j in range(len(real[i])):
			for k in range(len(predicted[i])):
				#overlap = _iou_circle(real[i][j], predicted[i][k])
				dist = _dist(real[i][j], predicted[i][k])
				iou.append(dist)
				if dist < MAX_DIST * MAX_DIST:
					iou_pos.append(overlap)	
					found = True
					break
			if found:
				break

		fppi.append(len(predicted[i]))

		if found:
			tp += 1

		print "found: {}".format(found)
		print "overlap: {}".format(overlap)
		_show_real_predicted(paths[i], real[i], predicted[i])
		print "\n"

	fppi = np.array(fppi)
	iou = np.array(iou)
	iou_pos = np.array(iou_pos)

	sensitivity = tp * 1.0 / p

	#return sensitivity, np.mean(fppi), np.std(fppi), np.mean(iou), np.std(iou), np.mean(iou_pos), np.std(iou_pos)
	return sensitivity, np.mean(fppi), np.std(fppi), 0, 0, 0, 0


if __name__ == "__main__":
	real_path = sys.argv[1]
	predicted_path = sys.argv[2]

	mea = evaluate(real_path, predicted_path)
	print "sensitivity {:.2f}, \nfppi mean {:.2f}, fppi std {:.2f} \niou mean {:.2f} iou std {:.2f}, iou+ mean {:.2f}, iou+ std {:.2f}".format(mea[0], mea[1], mea[2], mea[3], mea[4], mea[5], mea[6])