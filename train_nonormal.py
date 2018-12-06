import pose_learn as pl
import tensorflow as tf



win_size = 12
json_dir = '/media/storage/chris/json_output'
pl.normalize = False

X_train, Y_train, X_test, Y_test = pl.prepare_sets(json_dir, win_size)
model = pl.build_model(win_size)
with tf.device('/gpu:2'): 
    for i in range(0, 10): 
	print('Training for 10 epochs starting from epoch {}'.format(i*10))
        model.fit(X_train, Y_train, validation_data=(X_test, Y_test),\
                  batch_size=128, epochs=10, verbose=2)
	print('{} epochs completed'.format((i + 1) * 10))
	model.save('nonormal_model.h5')

