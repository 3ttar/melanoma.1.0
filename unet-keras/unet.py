import os 
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import numpy as np
from keras.models import *
from keras.layers import Input, merge, Conv2D, MaxPooling2D, UpSampling2D, Dropout, Cropping2D
from keras.optimizers import *
from keras.callbacks import ModelCheckpoint, LearningRateScheduler
from keras import backend as keras
from data import *

class myUnet(object):

	def __init__(self, img_rows = 256, img_cols = 256):

		self.img_rows = img_rows
		self.img_cols = img_cols

	# def test(self, y_true, y_pred, smooth=1):
	# 	y_true_f = K.flatten(y_true)
	# 	y_pred_f = K.flatten(y_pred)
	# 	# y_pred_f[y_pred_f >= 0.5] = 1
	# 	# y_pred_f[y_pred_f < 0.5] = 0
	# 	intersection = K.sum(y_true_f * y_pred_f)
	# 	# print(np.unique(y_pred))
	# 	# print(np.unique(y_true))
	# 	return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

	# def test_loss(self, y_true, y_pred):
	# 	return - self.test(y_true, y_pred)

	def load_data(self):

		mydata = dataProcess(self.img_rows, self.img_cols)
		# these two lines by A Hassaan
		mydata.create_train_data()
		mydata.create_test_data()

		###
		imgs_train, imgs_mask_train = mydata.load_train_data()
		imgs_test = mydata.load_test_data()
		return imgs_train, imgs_mask_train, imgs_test

	def get_unet(self):

		inputs = Input((self.img_rows, self.img_cols,1))
		
		'''
		unet with crop(because padding = valid) 

		conv1 = Conv2D(64, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(inputs)
		print "conv1 shape:",conv1.shape
		conv1 = Conv2D(64, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv1)
		print "conv1 shape:",conv1.shape
		crop1 = Cropping2D(cropping=((90,90),(90,90)))(conv1)
		print "crop1 shape:",crop1.shape
		pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
		print "pool1 shape:",pool1.shape

		conv2 = Conv2D(128, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(pool1)
		print "conv2 shape:",conv2.shape
		conv2 = Conv2D(128, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv2)
		print "conv2 shape:",conv2.shape
		crop2 = Cropping2D(cropping=((41,41),(41,41)))(conv2)
		print "crop2 shape:",crop2.shape
		pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
		print "pool2 shape:",pool2.shape

		conv3 = Conv2D(256, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(pool2)
		print "conv3 shape:",conv3.shape
		conv3 = Conv2D(256, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv3)
		print "conv3 shape:",conv3.shape
		crop3 = Cropping2D(cropping=((16,17),(16,17)))(conv3)
		print "crop3 shape:",crop3.shape
		pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
		print "pool3 shape:",pool3.shape

		conv4 = Conv2D(512, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(pool3)
		conv4 = Conv2D(512, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv4)
		drop4 = Dropout(0.5)(conv4)
		crop4 = Cropping2D(cropping=((4,4),(4,4)))(drop4)
		pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

		conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(pool4)
		conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv5)
		drop5 = Dropout(0.5)(conv5)

		up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
		merge6 = merge([crop4,up6], mode = 'concat', concat_axis = 3)
		conv6 = Conv2D(512, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(merge6)
		conv6 = Conv2D(512, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv6)

		up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
		merge7 = merge([crop3,up7], mode = 'concat', concat_axis = 3)
		conv7 = Conv2D(256, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(merge7)
		conv7 = Conv2D(256, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv7)

		up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
		merge8 = merge([crop2,up8], mode = 'concat', concat_axis = 3)
		conv8 = Conv2D(128, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(merge8)
		conv8 = Conv2D(128, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv8)

		up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
		merge9 = merge([crop1,up9], mode = 'concat', concat_axis = 3)
		conv9 = Conv2D(64, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(merge9)
		conv9 = Conv2D(64, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv9)
		conv9 = Conv2D(2, 3, activation = 'relu', padding = 'valid', kernel_initializer = 'he_normal')(conv9)
		'''

		conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(inputs)
		print("conv1 shape:",conv1.shape)
		conv1 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv1)
		print("conv1 shape:",conv1.shape)
		pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
		print("pool1 shape:",pool1.shape)

		conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool1)
		print("conv2 shape:",conv2.shape)
		conv2 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv2)
		print("conv2 shape:",conv2.shape)
		pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
		print("pool2 shape:",pool2.shape)

		conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool2)
		print("conv3 shape:",conv3.shape)
		conv3 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv3)
		print("conv3 shape:",conv3.shape)
		pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
		print("pool3 shape:",pool3.shape)

		conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool3)
		conv4 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv4)
		drop4 = Dropout(0.5)(conv4)
		pool4 = MaxPooling2D(pool_size=(2, 2))(drop4)

		conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(pool4)
		conv5 = Conv2D(1024, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv5)
		drop5 = Dropout(0.5)(conv5)

		up6 = Conv2D(512, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(drop5))
		merge6 = merge([drop4,up6], mode = 'concat', concat_axis = 3)
		conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge6)
		conv6 = Conv2D(512, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv6)

		up7 = Conv2D(256, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv6))
		merge7 = merge([conv3,up7], mode = 'concat', concat_axis = 3)
		conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge7)
		conv7 = Conv2D(256, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv7)

		up8 = Conv2D(128, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv7))
		merge8 = merge([conv2,up8], mode = 'concat', concat_axis = 3)
		conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge8)
		conv8 = Conv2D(128, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv8)

		up9 = Conv2D(64, 2, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(UpSampling2D(size = (2,2))(conv8))
		merge9 = merge([conv1,up9], mode = 'concat', concat_axis = 3)
		conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(merge9)
		conv9 = Conv2D(64, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
		conv9 = Conv2D(2, 3, activation = 'relu', padding = 'same', kernel_initializer = 'he_normal')(conv9)
		conv10 = Conv2D(1, 1, activation = 'sigmoid')(conv9)

		model = Model(input = inputs, output = conv10)

		def dice_coef(y_true, y_pred, smooth=1):
			y_true_f = K.flatten(y_true)
			y_pred_f = K.flatten(y_pred)
			intersection = K.sum(y_true_f * y_pred_f)
			return (2. * intersection + smooth) / (K.sum(y_true_f) + K.sum(y_pred_f) + smooth)

		def dice_coef_loss(y_true, y_pred):
			return 1-dice_coef(y_true, y_pred)

		def Jac(y_true, y_pred):
			y_pred_f = K.flatten(K.round(y_pred))
			y_true_f = K.flatten(y_true)
			num = K.sum(y_true_f * y_pred_f)
			den = K.sum(y_true_f) + K.sum(y_pred_f) - num
			return num / den

		model.compile(optimizer = Adam(lr = 1e-4), loss = ['binary_crossentropy'], metrics = ['accuracy'])
		# model.compile(optimizer = Adam(lr = 1e-2), loss = dice_coef_loss, metrics = ['acc'])

		return model


	def train(self):

		print("loading data")
		imgs_train, imgs_mask_train, imgs_test = self.load_data()
		print("loading data done")
		model = self.get_unet()
		print("got unet")

		model_checkpoint = ModelCheckpoint('unet.hdf5', monitor='loss',verbose=1, save_best_only=True)
		print('Fitting model...')
		model.fit(imgs_train, imgs_mask_train, batch_size=16, nb_epoch=200, verbose=1,validation_split=0.2, shuffle=True, callbacks=[model_checkpoint])

		print('predict test data')
		imgs_mask_test = model.predict(imgs_test, batch_size=1, verbose=1)
		np.save('/content/unet-keras/results/imgs_mask_test.npy', imgs_mask_test)

	def save_img(self):

		print("array to image")
		imgs = np.load('/content/unet-keras/results/imgs_mask_test.npy')
		names = np.load("/content/unet-keras/names.npy")
		for i in range(imgs.shape[0]):
			img = imgs[i]
			img = array_to_img(img)
			n = names[i]
			img.save("/content/unet-keras/results/{0}.jpg".format(n))




if __name__ == '__main__':
	myunet = myUnet()
	myunet.train()
	myunet.save_img()








