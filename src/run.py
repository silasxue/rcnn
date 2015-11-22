from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from random import shuffle

import theano 
import theano.tensor as T

import os

from cnn import trainConvNet, represent
from rnn import trainRecNet, evaluate

def generate_data(file_prefixes, p_width = 10):
	def generate_patch(img, (i, j), p_width = 10): # patch area : (10*10)
		assert p_width%2 == 0
		p_width/=2
		patch = img.crop((i-p_width, j-p_width, i+p_width, j+p_width))
		return patch

	#load images
	patch_tuple = ()
	y_list = []
	data_size = 0
	ind = 0
	print 'Data generated: 0.00 %'
	for f in file_prefixes:
		img = Image.open(open('../data/left_scaled/'+f+'.jpg'))
		label = Image.open(open('../data/labeled_scaled/'+f+'.png'))
		label = np.array(label, dtype='int32')
		rows, cols = img.size
		for i in range(rows):
			for j in range(cols):
				# note img(i, j) -> label(j, i)
				l = label[j][i]
				if l==0:
					continue
				patch_10 = generate_patch(img, (i, j), p_width)
				patch_10_ = np.array(patch_10, dtype='float64').transpose(2, 0, 1)/256.
				patch_tuple += (patch_10_, )
				y_list.append(l-1)
				data_size += 1
				#print data_size
		ind += 1
		print '\033[FData generated: ', ind*100./len(file_prefixes), ' %\t'

	assert len(patch_tuple) == len(y_list) and len(y_list) == data_size
	print 'data size: ', data_size

	x = np.concatenate(patch_tuple).reshape((data_size, 3, p_width, p_width))
	y = y_list

	return x, y

def shared_dataset(data_xy):
	x, y = data_xy
	shared_x = theano.shared(np.asarray(x, dtype=theano.config.floatX), borrow=True)
	shared_y = theano.shared(np.asarray(y, dtype=theano.config.floatX), borrow=True)
	return shared_x, T.cast(shared_y, 'int32')

def shared_data_x(data_x):
	return theano.shared(np.asarray(data_x, dtype=theano.config.floatX), borrow=True)

def shared_data_y(data_y):
	return T.cast(theano.shared(np.asarray(data_y, dtype=theano.config.floatX), borrow=True), 'int32')

'''
	program starts here
'''

file_prefixes = []
for f in os.listdir('../data/labeled_scaled'):
	if f=='.DS_Store':
		continue
	file_prefixes.append(f[:-4])

shuffle(file_prefixes)

# repeat for p_width = 20, 30, 40 ...
p_width = 4

x, y = generate_data(file_prefixes[:1], p_width)
#x, y = x[:10], y[:10] # remove
train_x, train_y = shared_dataset((x[0:(3*len(x)/5)], y[0:(3*len(y)/5)]))
valid_x, valid_y = shared_dataset((x[(3*len(x)/5):(4*len(x)/5)], y[3*len(y)/5:4*len(y)]))
test_x, test_y = shared_dataset((x[(4*len(x)/5):len(x)], y[(4*len(y)/5):len(y)]))

net_x = shared_data_x(x)

#print type(test_x), type(test_y)
trainConvNet((train_x, train_y, test_x, test_y, valid_x, valid_y), p_width, 10, [5, 10])
rep4 = represent(net_x[:], net_x.shape.eval()[0], p_width)
# repeat block

# repeat for p_width = 20, 30, 40 ...
p_width = 10

x, y = generate_data(file_prefixes[:1], p_width)
#x, y = x[:10], y[:10] # remove
train_x, train_y = shared_dataset((x[0:(3*len(x)/5)], y[0:(3*len(y)/5)]))
valid_x, valid_y = shared_dataset((x[(3*len(x)/5):(4*len(x)/5)], y[3*len(y)/5:4*len(y)]))
test_x, test_y = shared_dataset((x[(4*len(x)/5):len(x)], y[(4*len(y)/5):len(y)]))
net_x = shared_data_x(x)

#print type(test_x), type(test_y)
trainConvNet((train_x, train_y, test_x, test_y, valid_x, valid_y), p_width, 10, [5, 10])
rep10 = represent(net_x[:], net_x.shape.eval()[0], p_width)
# repeat block

# repeat for p_width = 20, 30, 40 ...
p_width = 14

x, y = generate_data(file_prefixes[:1], p_width)
#x, y = x[:10], y[:10] # remove
train_x, train_y = shared_dataset((x[0:(3*len(x)/5)], y[0:(3*len(y)/5)]))
valid_x, valid_y = shared_dataset((x[(3*len(x)/5):(4*len(x)/5)], y[3*len(y)/5:4*len(y)]))
test_x, test_y = shared_dataset((x[(4*len(x)/5):len(x)], y[(4*len(y)/5):len(y)]))
net_x = shared_data_x(x)

print type(test_x), type(test_y)
trainConvNet((train_x, train_y, test_x, test_y, valid_x, valid_y), p_width, 10, [5, 10])
rep14 = represent(net_x[:], net_x.shape.eval()[0], p_width)
# repeat block

'''testing for RNN'''
#rep4 = represent(train_x[:], train_x[:].shape.eval()[0], 4)
#print type(rep4), rep4.shape
train_x4 = shared_data_x(rep4[:(3*rep4.shape[0]/4)])
test_x4 = shared_data_x(rep4[(3*rep4.shape[0]/4):])
#print 'HOla!', type(test_x4), test_x4.shape.eval()

train_x10 = shared_data_x(rep10[:(3*rep10.shape[0]/4)])
test_x10 = shared_data_x(rep10[(3*rep10.shape[0]/4):])

train_x14 = shared_data_x(rep14[:(3*rep14.shape[0]/4)])
test_x14 = shared_data_x(rep14[(3*rep14.shape[0]/4):])

train_x = (train_x4, train_x10, train_x14)
test_x = (test_x4, test_x10, test_x14)

train_y = shared_data_y(y[:(3*len(y)/4)])
test_y = shared_data_y(y[(3*len(y)/4):])

print 'RNN training data dimensions: '
print '4x4: ', train_x[0].shape.eval()
print 'label: ', train_y.shape.eval()

trainRecNet((train_x, train_y), 90, 1, n_recurrences=3)
pred = evaluate((test_x, test_y), 90, n_recurrences=3)

print np.array(pred).shape, test_y.shape.eval()

right_labels = 0
wrong_labels = 0

pred_shape = np.array(pred).shape
for i in range(pred_shape[0]):
	for j in range(pred_shape[1]):
		#print pred[i][j], test_y[i*pred_shape[1]+j]
		if (pred[i][j]==test_y.eval()[i*pred_shape[1]+j]):
			right_labels+=1
		else:
			wrong_labels+=1

print 'right: ', right_labels
print 'wrong: ', wrong_labels
print 'computed accuracy: ', (right_labels*100.)/(right_labels+wrong_labels), ' %'