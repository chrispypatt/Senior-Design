import pose_learn as pl
import tensorflow as tf



win_size = 12
json_dir = '/media/storage/chris/json_output'
pl.normalize = False
output_file = 'training_results.txt'

X_train, Y_train, X_test, Y_test = pl.prepare_sets(json_dir, win_size)
model = pl.build_model2(win_size)
with tf.device('/gpu:2'), open(output_file, 'a') as f: 
    for i in range(0, 10): 
        print('Training for 10 epochs starting from epoch {}'.format(i*10))
        model.fit(X_train, Y_train, validation_data=(X_test, Y_test),\
                  batch_size=128, epochs=10, verbose=2)
        print('{} epochs completed'.format((i + 1) * 10))

        # Write the result of the training to the file
        loss, acc = model.evaluate(X_test, Y_test)
        f.write('{} epochs completed:\n'.format((i + 1) * 10)) 
        f.write('    Loss: {}\n'.format(loss))
        f.write('    Accuracy: {}\n'.format(acc))

        model.save('nonormal_model2.h5')
        
