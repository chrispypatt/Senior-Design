import pose_learn as pl



win_size = 12
json_dir = '/media/storage/chris/json_output'
pl.normalize = False

X_train, Y_train, X_test, Y_test = pl.prepare_sets(json_dir, win_size)
model = pl.build_model(win_size)
model.fit(X_train, Y_train, validation_data=(X_test, Y_test),\
          batch_size=128, epochs=100, verbose=2)

model.save('nonormal_model.h5')

