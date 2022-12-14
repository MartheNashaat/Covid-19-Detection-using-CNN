#**X-Ray Classification(Covid-Pnemonia-Normal)**
---
"""

from google.colab import drive
drive.mount('/content/drive')

"""#Imports"""

import zipfile
import numpy as np
import pandas as pd
import imageio
from PIL import Image,ImageOps
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split
import keras
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50 #####
from keras.models import Model,Sequential
from keras.layers import Flatten, Dense, Activation
from keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt
#added imports for grid search
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV

from keras.layers import Dropout
from tensorflow.keras.layers import BatchNormalization
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers.schedules import ExponentialDecay
from keras.utils.vis_utils import plot_model
import seaborn as sn
import sklearn

"""#Open dataset and store in matrices

**Run the following two cells once only. Use the saved binary files after that.**
"""

#append samples to an empty array
Covid_data = []
Normal_data=[]
Pneumonia_data=[]

#open zip file in google drive
zip_read = zipfile.ZipFile('/content/drive/MyDrive/Colab Notebooks/COVID-19_Radiography_Database.zip')

#search the three categorical class , take it's image(png) sample , changed it to Greyscale and append it to it's class
for file in zip_read.namelist():
   if file.startswith('COVID-19_Radiography_Dataset/COVID/') & file.endswith('.png') :
     x=zip_read.open(file)  
     img =Image.open(x)
     img=(img.resize((100,100))).convert('L') #######
     gray_img =np.array(img)
     Covid_data.append(gray_img)
   elif  file.startswith('COVID-19_Radiography_Dataset/Normal/') & file.endswith('.png'):
     x=zip_read.open(file)  
     img =Image.open(x)
     img=(img.resize((100,100))).convert('L') #######
     ray_img =np.array(img)
     Normal_data.append(gray_img)
   elif  file.startswith('COVID-19_Radiography_Dataset/Viral Pneumonia/') & file.endswith('.png'):
     x=zip_read.open(file)  
     img =Image.open(x)
     img=(img.resize((100,100))).convert('L') #######
     gray_img =np.array(img)
     Pneumonia_data.append(gray_img)

Covid_data=np.array(Covid_data)
Normal_data=np.array(Normal_data)
Normal_data=Normal_data[:3000] ######
Pneumonia_data=np.array(Pneumonia_data)

print('Covid data shape-> ',Covid_data.shape)
print('Normal data shape-> ',Normal_data.shape)
print('Pneumonia data shape->',Pneumonia_data.shape)

"""Save data in binary files """

## save in binary file 
np.save('/content/drive/MyDrive/Colab Notebooks/Covid_data_Array.npy', Covid_data)
np.save('/content/drive/MyDrive/Colab Notebooks/Normal_Array.npy', Normal_data)
np.save('/content/drive/MyDrive/Colab Notebooks/Pneumonia_Array.npy', Pneumonia_data)

### read data from binary file 
Covid_data = np.load('/content/drive/MyDrive/Colab Notebooks/Covid_data_Array_og.npy')
print(np.array(Covid_data).shape)
Covid_data=np.stack((Covid_data,)*3,axis=-1)
print(np.array(Covid_data).shape)

Normal_data = np.load('/content/drive/MyDrive/Colab Notebooks/Normal_Array_og.npy')
print(np.array(Normal_data).shape)
Normal_data=np.stack((Normal_data,)*3,axis=-1)
print(np.array(Normal_data).shape)

Pneumonia_data = np.load('/content/drive/MyDrive/Colab Notebooks/Pneumonia_Array_og.npy')
print(np.array(Pneumonia_data).shape)
Pneumonia_data=np.stack((Pneumonia_data,)*3,axis=-1)
print(np.array(Pneumonia_data).shape)

"""#Normalize the dataset 




"""

#Normalize the dataset by subtracting it my max value(255)  
Covid_data=Covid_data/255.0
Normal_data=Normal_data/255.0
Pneumonia_data=Pneumonia_data/255.0

"""#Create Labels for Covid, Pnemonia,Normal X-Rays


"""

CovidSize=Covid_data.shape[0]
Covid_Labels=np.repeat(0,CovidSize) #0 represents covid labels

PneumoniaSize=Pneumonia_data.shape[0]
Pneumonia_Labels=np.repeat(1,PneumoniaSize) #1 represents pnemonia labels

NormalSize=Normal_data.shape[0]
Normal_Labels=np.repeat(2,NormalSize) #2 represents normal labels

print(type(Covid_Labels[0]))
print(Pneumonia_Labels.shape)
print(Normal_Labels.shape)

"""#Split data into Train, Validation, Test
> 
15% is used for the Testing phase
>
15% is used for the validation phase
>
70% is used for the Training phase
"""

#split into train and test into 85 and 15 (done in covid data train1 and covid data test),
#then split train again into 70(train)-->covid data train and 15(validation)-->covid data validation
#this is done for the data and the labels 
##repeated in pnemonia and normal 
Covid_data_Train1,Covid_data_Test,Covid_Labels_Train1,Covid_Labels_Test=train_test_split(Covid_data,Covid_Labels,test_size=0.15,random_state=42)
Covid_data_Train,Covid_data_Validation,Covid_Labels_Train,Covid_Labels_Validation=train_test_split(Covid_data_Train1,Covid_Labels_Train1,test_size=0.1767,random_state=42)
print(Covid_data_Validation.shape)
print(Covid_data_Train.shape)
print(Covid_data_Test.shape)

print('Labels\n',Covid_Labels_Train.shape)
print(Covid_Labels_Test.shape)
print(Covid_Labels_Validation.shape)

Pneumonia_data_Train1,Pneumonia_data_Test,Pneumonia_Labels_Train1,Pneumonia_Labels_Test=train_test_split(Pneumonia_data,Pneumonia_Labels,test_size=0.15,random_state=42)
Pneumonia_data_Train,Pneumonia_data_Validation,Pneumonia_Labels_Train,Pneumonia_Labels_Validation=train_test_split(Pneumonia_data_Train1,Pneumonia_Labels_Train1,test_size=0.1767,random_state=42)
print(Pneumonia_data_Validation.shape)
print(Pneumonia_data_Train.shape)
print(Pneumonia_data_Test.shape)

print('Labels\n',Pneumonia_Labels_Train.shape)
print(Pneumonia_Labels_Test.shape)
print(Pneumonia_Labels_Validation.shape)

Normal_data_Train1,Normal_data_Test,Normal_Labels_Train1,Normal_Labels_Test=train_test_split(Normal_data,Normal_Labels,test_size=0.15,random_state=42)
Normal_data_Train,Normal_data_Validation,Normal_Labels_Train,Normal_Labels_Validation=train_test_split(Normal_data_Train1,Normal_Labels_Train1,test_size=0.1762,random_state=42)
print(Normal_data_Validation.shape)
print(Normal_data_Train.shape)
print(Normal_data_Test.shape)

print('Labels\n',Normal_Labels_Train.shape)
print(Normal_Labels_Test.shape)
print(Normal_Labels_Validation.shape)

from numpy.lib import twodim_base
#Combine all train datasets 
All_Train_Data=np.asarray(np.vstack((Covid_data_Train,Pneumonia_data_Train,Normal_data_Train))).astype(np.float32)
All_Train_Labels=np.hstack((Covid_Labels_Train,Pneumonia_Labels_Train,Normal_Labels_Train)).ravel()
print(All_Train_Data.shape)
print(All_Train_Labels.shape)
#Combine all validation datasets
All_Validation_Data=np.asarray(np.vstack((Covid_data_Validation,Pneumonia_data_Validation,Normal_data_Validation))).astype(np.float32)
All_Validation_Labels=np.hstack((Covid_Labels_Validation,Pneumonia_Labels_Validation,Normal_Labels_Validation)).ravel()
print(All_Validation_Data.shape)
print(All_Validation_Labels.shape)
#Combine all Test datasets
All_Test_Data=np.asarray(np.vstack((Covid_data_Test,Pneumonia_data_Test,Normal_data_Test))).astype(np.float32)
All_Test_Labels=np.hstack((Covid_Labels_Test,Pneumonia_Labels_Test,Normal_Labels_Test)).ravel()
print(All_Test_Labels.shape)
print(All_Test_Data.shape)


#combine all dataset together
All_Data=np.asarray(np.vstack((All_Train_Data,All_Validation_Data,All_Test_Data))).astype(np.float32)
All_Labels=np.hstack((All_Train_Labels,All_Validation_Labels,All_Test_Labels)).ravel()

All_Test_Labels = to_categorical(All_Test_Labels, 3)
All_Validation_Labels = to_categorical(All_Validation_Labels, 3)
All_Train_Labels = to_categorical(All_Train_Labels, 3)
All_Labels=to_categorical(All_Labels, 3)

"""## ResNet50 Model"""

from keras import regularizers
def create_model():
  Resnet_Model=Sequential()
  model=tf.keras.applications.ResNet50(include_top=False, input_shape=(100,100,3), weights='imagenet', classes=3,pooling='max')
  #(include_top=False-->(use my input and output), weights='imagenet' -->model already trained as has its saved weights)
  for layer in model.layers:
    layer.trainable=False #don't change in the weights saved (from imagenet)
  Resnet_Model.add(model)
  Resnet_Model.add(Flatten())
  Resnet_Model.add(Dense(64,activation='relu', kernel_regularizer=regularizers.l2(0.001)) )
  Resnet_Model.add(BatchNormalization(epsilon=1e-06,momentum=0.8))
  Resnet_Model.add(Dense(128,activation='relu', kernel_regularizer=regularizers.l2(0.001)) )
  Resnet_Model.add(BatchNormalization(epsilon=1e-06,momentum=0.8))
  Resnet_Model.add(Dense(512,activation='relu', kernel_regularizer=regularizers.l2(0.001)) )
  Resnet_Model.add(Dense(3,activation='softmax'))
  Resnet_Model.summary()

  # initial_learning_rate = 0.1
  lr_schedule =ExponentialDecay(initial_learning_rate=0.01,
                                decay_steps=1000, # was 1000
                                decay_rate=0.8, #was 0.3 - 0.96
                                staircase=True
                                )


  Resnet_Model.compile(optimizer=tf.keras.optimizers.Adadelta(learning_rate=lr_schedule),loss='categorical_crossentropy',metrics=['accuracy']) ##check learning rate, categorical_crossentropy= multi class output label
  return Resnet_Model
ResnetModel=create_model()
model = KerasClassifier(build_fn=ResnetModel, verbose=0)

"""Random and grid search - don't run unless needed"""

# # Random search
# ResnetModel=create_model()
# model = KerasClassifier(build_fn=ResnetModel, verbose=0)
# space= dict()
# space["batch_size"] = [32,64]
# space["epochs"] = [6,7]
# search = RandomizedSearchCV(model, space, n_iter=100, scoring='accuracy', n_jobs=-1, cv=3, random_state=1)
# result = search.fit(All_Train_Data, All_Train_Labels)
# # summarize result
# print('Best Score: %s' % result.best_score_)
# print('Best Hyperparameters: %s' % result.best_params_)

# Grid search 
# seed= 7 
# np.random.seed(seed)
# model = KerasClassifier(build_fn=create_model, verbose=0)
# batch_size = [32, 64, 128]
# epochs = [7,10,30]
# param_grid = dict(batch_size=batch_size, epochs=epochs)
# grid = GridSearchCV(estimator=model, param_grid=param_grid, n_jobs=-1, cv=3)
# grid_result = grid.fit(All_Train_Data, All_Train_Labels)
# # summarize results
# print("Best: %f using %s" % (grid_result.best_score_, grid_result.best_params_))
# means = grid_result.cv_results_['mean_test_score']
# stds = grid_result.cv_results_['std_test_score']
# params = grid_result.cv_results_['params']
# for mean, stdev, param in zip(means, stds, params):
#     print("%f (%f) with: %r" % (mean, stdev, param))

No_epochs=30
# callback = EarlyStopping(monitor='loss', patience=5)
fit_model=ResnetModel.fit(All_Train_Data,
                          All_Train_Labels,
                          batch_size=32,
                          epochs=No_epochs,
                          validation_data=(All_Validation_Data,All_Validation_Labels)#,callbacks=[callback]
                          )

print("number of epochs used :",len(fit_model.history['loss']))
pred=ResnetModel.evaluate(All_Test_Data,All_Test_Labels,batch_size=10)
print("Test loss, Test acc:", pred)
predictions=ResnetModel.predict(All_Test_Data[:3])
print("predictions shape:", predictions.shape)

print(predictions)

acc = fit_model.history['accuracy']
val_acc = fit_model.history['val_accuracy']

loss = fit_model.history['loss']
val_loss = fit_model.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Cross Entropy')
plt.title('Training and Validation Loss')
plt.xlabel('epoch')
plt.show()

"""## Xception model

"""

Xception_model = Sequential()
model_2=tf.keras.applications.Xception(
    include_top= False,
    weights="imagenet",
    input_shape=(100,100,3),
    classes=3,
    classifier_activation="softmax",
)
for layer in model_2.layers:
  layer.trainable= False
Xception_model.add(keras.Input(shape=(100, 100, 3)))
Xception_model.add(tf.keras.layers.Rescaling(scale=1./255))
Xception_model.add(tf.keras.layers.RandomCrop(100, 100, seed=42))
Xception_model.add(model_2)
Xception_model.add(Flatten())
Xception_model.add(Dense(64,activation='relu'))
Xception_model.add(BatchNormalization(epsilon=1e-06,momentum=0.8))
Xception_model.add(Dense(512,activation='relu'))
Xception_model.add(Dense(3,activation='softmax'))
Xception_model.summary()

plot_model(Xception_model, to_file='model_plot.png', show_shapes=True, show_layer_names=True,show_layer_activations=True)

initial_learning_rate = 0.01
lr_schedule = ExponentialDecay(initial_learning_rate,
                                  decay_steps=10000, #more
                                  decay_rate=0.8, #less
                                  staircase=True
                                  )


Xception_model.compile(optimizer=tf.keras.optimizers.Adadelta(learning_rate=lr_schedule),loss='categorical_crossentropy',metrics=['accuracy']) ##check learning rate, categorical_crossentropy= multi class output label
No_epochs=30
# callback = EarlyStopping(monitor='loss', patience=5)
fit_model=Xception_model.fit(All_Train_Data,
                           All_Train_Labels,
                           batch_size=32,
                           epochs=No_epochs,
                           validation_data=(All_Validation_Data,All_Validation_Labels)#,callbacks=[callback]
                           )

print("number of epochs used :",len(fit_model.history['loss']))
pred=Xception_model.evaluate(All_Test_Data,All_Test_Labels,batch_size=10)
print("Test loss, Test acc:", pred)
predictions=Xception_model.predict(All_Test_Data)
print("predictions shape:", predictions.shape)

object1 = pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/AdadeltaFitModel')


plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(object1['accuracy'], label='Training Accuracy of Xception')
plt.plot(object1['val_accuracy'], label='Validation Accuracy of Xception')
# plt.plot(object2['accuracy'], label='Training Accuracy of Resnet50' )
# plt.plot(object2['val_accuracy'], label='Validation Accuracy of Resnet50')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(object1['loss'], label='Training Loss of Xception')
plt.plot(object1['val_loss'], label='Validation Loss of Xception')
# plt.plot(object2['loss'], label='Training Loss  of Resnet50')
# plt.plot(object2['val_loss'], label='Validation Loss  of Resnet50')
plt.legend(loc='upper right')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.show()

import pickle
with open('/content/drive/MyDrive/Colab Notebooks/AdadeltaFitModel', 'wb') as file_pi:
    pickle.dump(fit_model.history, file_pi)
object1 = pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/AdadeltaFitModel')

Xception_model.save('/content/drive/MyDrive/Colab Notebooks/Adadelta_Model')
Xception_model= keras.models.load_model('/content/drive/MyDrive/Colab Notebooks/Adadelta_Model')

object1 = pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/AdadeltaFitModel')
object2=pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/ResnetAdadelta')

# acc = fit_model.history['accuracy']
# val_acc = fit_model.history['val_accuracy']

# loss = fit_model.history['loss']
# val_loss = fit_model.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(object1['accuracy'], label='Training Accuracy of Xception')
plt.plot(object1['val_accuracy'], label='Validation Accuracy of Xception')
plt.plot(object2['accuracy'], label='Training Accuracy of Resnet50' )
plt.plot(object2['val_accuracy'], label='Validation Accuracy of Resnet50')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(object1['loss'], label='Training Loss of Xception')
plt.plot(object1['val_loss'], label='Validation Loss of Xception')
plt.plot(object2['loss'], label='Training Loss  of Resnet50')
plt.plot(object2['val_loss'], label='Validation Loss  of Resnet50')
plt.legend(loc='upper right')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.show()

matrix = sklearn.metrics.confusion_matrix(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1))
print(matrix)

from sklearn.metrics import classification_report
target_names = ['Covid', 'Normal', 'Pneumonia']
print(classification_report(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1), target_names=target_names))
matrix = sklearn.metrics.confusion_matrix(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1))
# pp_matrix_from_data(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1))

# sn.set(font_scale=1) # for label size
# sn.heatmap(matrix, annot=True, annot_kws={"size": 13}) # font size
# plt.show()
ax = sn.heatmap(matrix, annot=True, cmap='BuPu',fmt=".1f")

ax.set_title('Confusion \n');
ax.set_xlabel('\nPredicted disease Category')
ax.set_ylabel('Actual disease Category ');

## Ticket labels - List must be in alphabetical order
ax.xaxis.set_ticklabels(['Covid','Normal', 'Pneumonia'])
ax.yaxis.set_ticklabels(['Covid','Normal', 'Pneumonia'])

## Display the visualization of the Confusion Matrix.
plt.show()

"""# **VGG16**"""

VGG_model = Sequential()
model_3=tf.keras.applications.VGG16(
    include_top= False,
    weights="imagenet",
    input_shape=(100,100,3),
    classes=3,
    classifier_activation="softmax",
)
for layer in model_3.layers:
  layer.trainable= False
VGG_model.add(keras.Input(shape=(100, 100, 3)))
# VGG_model.add(tf.keras.layers.Rescaling(scale=1./255))
# VGG_model.add(tf.keras.layers.RandomCrop(100, 100, seed=42))
VGG_model.add(model_3)
VGG_model.add(Flatten())
VGG_model.add(Dense(32,activation='relu'))
# VGG_model.add(BatchNormalization(epsilon=1e-06,momentum=0.8))
# VGG_model.add(Dense(512,activation='relu'))
# Xception_model.add(BatchNormalization(epsilon=1e-06,momentum=0.8))
# Xception_model.add(Dense(1024,activation='relu'))
VGG_model.add(Dense(3,activation='softmax'))
VGG_model.summary()

plot_model(VGG_model, to_file='model_plotVGG.png', show_shapes=True, show_layer_names=True,show_layer_activations=True,rankdir='LR')

initial_learning_rate = 0.01
lr_schedule = ExponentialDecay(initial_learning_rate,
                                  decay_steps=10000, #more
                                  decay_rate=0.8, #less
                                  staircase=True
                                  )


VGG_model.compile(optimizer=tf.keras.optimizers.Adadelta(learning_rate=0.01),loss='categorical_crossentropy',metrics=['accuracy']) ##check learning rate, categorical_crossentropy= multi class output label
No_epochs=30
# callback = EarlyStopping(monitor='loss', patience=5)
fit_model2=VGG_model.fit(All_Train_Data,
                           All_Train_Labels,
                           batch_size=32,
                           epochs=No_epochs,
                           validation_data=(All_Validation_Data,All_Validation_Labels)#,callbacks=[callback]
                           )



print("number of epochs used :",len(fit_model2.history['loss']))
pred=VGG_model.evaluate(All_Test_Data,All_Test_Labels,batch_size=10)
print("Test loss, Test acc:", pred)
predictions=VGG_model.predict(All_Test_Data)
print("predictions shape:", predictions.shape)

acc = fit_model2.history['accuracy']
val_acc = fit_model2.history['val_accuracy']

loss = fit_model2.history['loss']
val_loss = fit_model2.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.show()

import pickle
with open('/content/drive/MyDrive/Colab Notebooks/vggmodelfit', 'wb') as file_pi:
    pickle.dump(fit_model2.history, file_pi)
object1 = pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/vggmodelfit')

VGG_model.save('/content/drive/MyDrive/Colab Notebooks/vggmodelsave')
VGG_model= keras.models.load_model('/content/drive/MyDrive/Colab Notebooks/vggmodelsave')

# object1 = pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/AdadeltaFitModel')
object2=pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/ResnetAdadelta')
object3= pd.read_pickle(r'/content/drive/MyDrive/Colab Notebooks/vggmodelfit')

# print(object1['accuracy'])
print(object2['accuracy'])
print(object3['accuracy'])

# acc = fit_model.history['accuracy']
# val_acc = fit_model.history['val_accuracy']

# loss = fit_model.history['loss']
# val_loss = fit_model.history['val_loss']

plt.figure(figsize=(8, 8))
plt.subplot(2, 1, 1)
# plt.plot(object1['accuracy'], label='Training Accuracy of Xception')
# plt.plot(object1['val_accuracy'], label='Validation Accuracy of Xception')
plt.plot(object2['accuracy'], label='Training Accuracy of Resnet50' )
plt.plot(object2['val_accuracy'], label='Validation Accuracy of Resnet50')
plt.plot(object3['accuracy'], label='Training Accuracy of VGG')
plt.plot(object3['val_accuracy'], label='Validation Accuracy of VGG')
plt.legend(loc='lower right')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy')

plt.subplot(2, 1, 2)
# plt.plot(object1['loss'], label='Training Loss of Xception')
# plt.plot(object1['val_loss'], label='Validation Loss of Xception')
plt.plot(object2['loss'], label='Training Loss  of Resnet50')
plt.plot(object2['val_loss'], label='Validation Loss  of Resnet50')
plt.plot(object3['loss'], label='Training Loss of VGG')
plt.plot(object3['val_loss'], label='Validation Loss of VGG')
plt.legend(loc='upper right')
plt.ylabel('Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epoch')
plt.show()



matrix = sklearn.metrics.confusion_matrix(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1))
print(matrix)

from sklearn.metrics import classification_report
target_names = ['Covid', 'Normal', 'Pneumonia']
print(classification_report(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1), target_names=target_names))
matrix = sklearn.metrics.confusion_matrix(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1))
# pp_matrix_from_data(All_Test_Labels.argmax(axis=1), predictions.argmax(axis=1))

# sn.set(font_scale=1) # for label size
# sn.heatmap(matrix, annot=True, annot_kws={"size": 13}) # font size
# plt.show()
ax = sn.heatmap(matrix, annot=True, cmap='BuPu',fmt=".1f")

ax.set_title('Confusion Matrix \n');
ax.set_xlabel('\nPredicted disease Category')
ax.set_ylabel('Actual disease Category ');

## Ticket labels - List must be in alphabetical order
ax.xaxis.set_ticklabels(['Covid','Normal', 'Pneumonia'])
ax.yaxis.set_ticklabels(['Covid','Normal', 'Pneumonia'])

## Display the visualization of the Confusion Matrix.
plt.show()
