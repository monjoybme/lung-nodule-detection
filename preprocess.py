import cv2
import numpy as np
import util
import time
EPS = 1e-9

def downsample(img):
	# check a better low-pass anti-aliasing filter, boxfilter is better
	ksize = (11, 11)
	dsize = (512, 512)
	sigma = 0.5

	smt = cv2.GaussianBlur(img, ksize, sigma)
	resized = cv2.resize(smt, dsize, interpolation=cv2.INTER_CUBIC)
	
	return resized

def lce(img):
	hsize = (33, 33)
	hsigma = 16

	mu = cv2.GaussianBlur(img, hsize, hsigma)
	ro2 = cv2.GaussianBlur(pow(img, 2), hsize, hsigma) - pow(mu, 2) + EPS
	assert np.min(ro2) >= 0
	res = (img - mu) / pow(ro2, 0.5)
	return res

def normalize(img, lung_mask):
	count = np.count_nonzero(lung_mask)
	mean = np.sum(img * lung_mask) * 1.0 / count
	std = (np.sum(lung_mask * ((img - mean) ** 2)) * 1.0 / (count-1)) ** 0.5
	normalized = (img - mean) / std

	return normalized

def preprocess(img, lung_mask):
	resized = downsample(img)
	enhanced = lce(resized)
	normalized = normalize(resized, lung_mask)

	return resized, enhanced, normalized



