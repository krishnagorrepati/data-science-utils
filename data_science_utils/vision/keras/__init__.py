import keras
from keras.utils import np_utils
import numpy as np
import pandas as pd
from keras.datasets import mnist
from keras.datasets import fashion_mnist
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, balanced_accuracy_score, accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from IPython.display import display
import seaborn as sns
from .visualize_layer import visualize_layer
from .adabound import AdaBound
from .one_cycle_lr import OneCycleLR
from .lr_finder import LRFinder
from .gradcam import *
from .layer_utils import *
from .regularizers import *
from keras.datasets import cifar10

from keras import backend as K
import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix, balanced_accuracy_score, accuracy_score
from keras.models import Sequential
from keras.layers.convolutional import Convolution2D, MaxPooling2D, DepthwiseConv2D, Conv2D, SeparableConv2D, AveragePooling2D
from keras.layers import Input, concatenate
from keras.layers import Activation, Flatten, Dense, Dropout, Lambda, SpatialDropout2D, Add
from keras.layers.normalization import BatchNormalization
from keras.layers.pooling import GlobalAveragePooling2D, GlobalMaxPooling2D
from keras.utils import np_utils
from keras.preprocessing.image import ImageDataGenerator
from keras.optimizers import SGD, Nadam, Adam
from keras.preprocessing.image import ImageDataGenerator
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, LearningRateScheduler
from keras.regularizers import l2
from keras_contrib.callbacks import CyclicLR
from keras.models import Model
import tensorflow as tf
import random

def get_mnist_labels():
    return list(range(0, 10))

def get_mnist_data(preprocess=False):
    (X_train, y_train), (X_test, y_test) = mnist.load_data()
    X_train, y_train = shuffle(X_train, y_train)
    X_test, y_test = shuffle(X_test, y_test)

    X_train = X_train.reshape(X_train.shape[0], 28, 28, 1)
    X_test = X_test.reshape(X_test.shape[0], 28, 28, 1)

    if preprocess:
        X_train = X_train.astype('float32')
        X_test = X_test.astype('float32')
        X_train /= 255
        X_test /= 255

    Y_train = np_utils.to_categorical(y_train, 10)
    Y_test = np_utils.to_categorical(y_test, 10)
    return X_train, Y_train, X_test, Y_test

def get_fashion_mnist_labels():
    labelNames = ["top", "trouser", "pullover", "dress", "coat",
                  "sandal", "shirt", "sneaker", "bag", "ankle boot"]
    return labelNames

def get_fashion_mnist_data(preprocess=False):
    (X_train, y_train), (X_test, y_test) = fashion_mnist.load_data()
    X_train, y_train = shuffle(X_train, y_train)
    X_test, y_test = shuffle(X_test, y_test)

    X_train = X_train.reshape(X_train.shape[0], 28, 28, 1)
    X_test = X_test.reshape(X_test.shape[0], 28, 28, 1)

    if preprocess:
        X_train = X_train.astype('float32')
        X_test = X_test.astype('float32')
        X_train /= 255
        X_test /= 255

    Y_train = np_utils.to_categorical(y_train, 10)
    Y_test = np_utils.to_categorical(y_test, 10)
    return X_train, Y_train, X_test, Y_test


def get_cifar10_labels():
    return ['airplane','automobile','bird','cat','deer','dog','frog','horse','ship','truck']

def get_imagenet_labels():
    from .imagenet_classes import imagenet_classes
    return imagenet_classes

def get_cifar10_data(preprocess=False):
    (X_train, y_train), (X_test, y_test) = cifar10.load_data()
    num_classes = len(np.unique(y_train))
    X_train, y_train = shuffle(X_train, y_train)
    X_test, y_test = shuffle(X_test, y_test)

    if preprocess:
        X_train = X_train.astype('float32')
        X_test = X_test.astype('float32')
        X_train /= 255
        X_test /= 255

    Y_train = np_utils.to_categorical(y_train, num_classes)
    Y_test = np_utils.to_categorical(y_test, num_classes)
    return X_train, Y_train, X_test, Y_test




def inspect_predictions(score, predictions,labels, classes, print_results=False, plot_results=True):

    test_score = score
    test_predictions = predictions

    test_predictions = np.argmax(test_predictions, axis=1)
    test_predictions = [classes[p] for p in test_predictions]

    y_test = np.argmax(labels, axis=1)
    y_test = [classes[p] for p in y_test]

    test_precision,test_recall,test_f1,test_support = precision_recall_fscore_support(y_test, test_predictions, average=None, labels=classes)

    results = pd.DataFrame({"classes": classes,
                                 "average":[None]*len(test_precision),
                                  "precision": test_precision,
                                  "recall": test_recall,
                                  "support": test_support,
                                  "data_source": ["test"] * len(test_precision)})

    test_precision, test_recall, test_f1, test_support = precision_recall_fscore_support(y_test, test_predictions,
                                                                                         average='micro', labels=classes)

    results_test = pd.DataFrame({"classes": [None],
                                 "average":['micro'],
                                  "precision": [test_precision],
                                  "recall": [test_recall],
                                  "support": [test_support],
                                  "data_source": ["test"]})

    results = pd.concat((results,results_test))

    # =======

    test_precision, test_recall, test_f1, test_support = precision_recall_fscore_support(y_test, test_predictions,
                                                                                         average='macro',
                                                                                         labels=classes)

    results_test = pd.DataFrame({"classes": [None],
                                 "average": ['macro'],
                                 "precision": [test_precision],
                                 "recall": [test_recall],
                                 "support": [test_support],
                                 "data_source": ["test"]})

    results = pd.concat((results, results_test))

    # ==============
    test_precision, test_recall, test_f1, test_support = precision_recall_fscore_support(y_test, test_predictions,
                                                                                         average='weighted',
                                                                                         labels=classes)

    results_test = pd.DataFrame({"classes": [None],
                                 "average": ['weighted'],
                                 "precision": [test_precision],
                                 "recall": [test_recall],
                                 "support": [test_support],
                                 "data_source": ["test"]})

    results = pd.concat((results, results_test))
    cm = confusion_matrix(y_test, test_predictions)
    balanced_accuracy = balanced_accuracy_score(y_test, test_predictions)
    accuracy = accuracy_score(y_test, test_predictions)


    if print_results:
        print(" =-= " * 20)
        print("Score = ", test_score)
        print("Balanced Accuracy = {:2.2f}%, Accuracy = {:2.2f}%".format(balanced_accuracy * 100, accuracy*100))


    if plot_results:
        print()
        plt.figure(figsize=(16,6))
        sns.barplot(x="classes",y="precision",data=results[~pd.isna(results.classes)])
        lower_bound = max(results['precision'].min() - 0.05,0)
        upper_bound = 1.05
        plt.ylim((lower_bound,upper_bound))
        plt.title("Precision per Class")
        plt.show()

        plt.figure(figsize=(16, 6))
        sns.barplot(x="classes", y="recall", data=results[~pd.isna(results.classes)])
        lower_bound = max(results['recall'].min() - 0.05, 0)
        upper_bound = 1.05
        plt.ylim((lower_bound, upper_bound))
        plt.title("Recall per Class")
        plt.show()

        cmap = plt.get_cmap('Blues')
        figsize = 6*int(np.ceil(len(classes)/10))
        fig, ax = plt.subplots(nrows=1, ncols=1, sharex=True, sharey=True, figsize=(figsize,figsize))
        im = ax.imshow(cm, cmap=cmap)  # Plot the confusion matrix

        # Show all ticks
        ax.set_xticks(np.arange(len(cm[0])))
        ax.set_yticks(np.arange(len(cm[1])))

        ax.set_xticklabels(classes)
        ax.set_yticklabels(classes)

        # Label each axis
        ax.set_ylabel("True Label")
        ax.set_xlabel("Predicted label\n\nAccuracy={:2.2f}% ".format(balanced_accuracy * 100))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        fig.tight_layout()
        ax.set_title("Confusion Matrix")
        thresh = cm.max() / 2
        for i in range(len(cm[0])):
            for j in range(len(cm[1])):
                text = ax.text(i, j, cm[i, j],ha="center", va="center", color="white" if cm[i, j] > thresh else "black")
        plt.show()

    return test_score,results


def evaluate(model, X_test, Y_test, classes,datagen=None, print_results=False, plot_results=True):
    # TODO: Graph P-R-F1 per class for seeing where we fail most
    # TODO: print class with lowest and highest P-R-F1

    assert (X_test is not None and Y_test is not None) or (datagen is not None)
    if datagen is not None:
        X_test, Y_test = datagen.next()
    test_score = model.evaluate(X_test, Y_test, verbose=0)
    test_predictions = model.predict(X_test)
    return inspect_predictions(test_score, test_predictions,labels=Y_test,classes=classes,
                               print_results=print_results, plot_results=plot_results)


def plot_model_history(model_history, clip_beginning=0):
    fig, axs = plt.subplots(1,2,figsize=(18,6))
    # summarize history for accuracy
    acc = model_history.history['acc']
    val_acc = model_history.history['val_acc']
    axs[0].plot(range(clip_beginning+1,len(acc)+1),acc[clip_beginning:])
    axs[0].plot(range(clip_beginning+1,len(val_acc)+1),val_acc[clip_beginning:])
    axs[0].set_title('Model Accuracy: Train = %.3f, Validation = %.3f'%(acc[-1],val_acc[-1]))
    axs[0].set_ylabel('Accuracy')
    axs[0].set_xlabel('Epoch')
    axs[0].set_xticks(np.arange(clip_beginning+1,len(acc)+1),len(acc)/10)
    axs[0].legend(['train', 'val'], loc='best')
    # summarize history for loss
    loss = model_history.history['loss']
    val_loss = model_history.history['val_loss']
    axs[1].plot(range(clip_beginning+1,len(loss)+1),loss[clip_beginning:])
    axs[1].plot(range(clip_beginning+1,len(val_loss)+1),val_loss[clip_beginning:])
    axs[1].set_title('Model Loss: Train = %.3f, Validation = %.3f'%(loss[-1],val_loss[-1]))
    axs[1].set_ylabel('Loss')
    axs[1].set_xlabel('Epoch')
    axs[1].set_xticks(np.arange(clip_beginning+1,len(loss)+1),len(loss)/10)
    axs[1].legend(['train', 'val'], loc='best')
    plt.show()

def show_examples(X,y,classes):
    rows = int(np.ceil(len(X)/5))
    if X.shape[1] > 64:
        multiplier = 2
    else:
        multiplier = 1
    fig = plt.figure(figsize=(10*multiplier, rows*2*multiplier))
    for idx in np.arange(len(X)):
        img = X[idx]
        assert (len(img.shape)==3 and img.shape[2] in [1,3,4]) or len(img.shape)==2
        ax = fig.add_subplot(rows, 5, idx + 1, xticks=[], yticks=[])
        cmap = None
        if (len(img.shape)==3 and img.shape[2]==1) or len(img.shape)==2:
            cmap="binary"
        if len(img.shape)==3 and img.shape[2]==1:
            img = img.reshape((img.shape[0],img.shape[1]))
        ax.imshow(img,cmap=cmap)
        ax.set_title(classes[np.argmax(y[idx])])
    plt.show()


def show_misclassified(X, Y_ohe, Y_pred, classes,
                       columns=5, total=25,
                       pick_randomly=True, image_size_multiplier=4):
    y_true = np.argmax(Y_ohe, axis=1)
    yp = np.argmax(Y_pred, axis=1)
    misclassified = y_true != yp
    X = X[misclassified]
    Y_ohe = Y_ohe[misclassified]
    Y_pred = Y_pred[misclassified]
    y_true = y_true[misclassified]
    yp = yp[misclassified]
    total = min(total, len(X))
    rows = int(np.ceil(total / columns))

    indexes = np.random.choice(len(X), total, replace=False) if pick_randomly else list(range(0, total))

    X = np.take(X, indexes, axis=0)
    Y_ohe = np.take(Y_ohe, indexes, axis=0)
    Y_pred = np.take(Y_pred, indexes, axis=0)
    y_true = np.take(y_true, indexes, axis=0)
    yp = np.take(yp, indexes, axis=0)

    fig_height = rows * image_size_multiplier * 2
    fig_width = columns * image_size_multiplier

    fig = plt.figure(figsize=(fig_width, fig_height))
    plt.subplots_adjust(bottom=0.1, top=1.0)
    idx1 = 0
    idx2 = 0
    jdx = 0
    for row in range(rows):
        for column in range(columns):
            if idx1 >= len(X):
                break
            img = X[idx1]
            assert (len(img.shape) == 3 and img.shape[2] in [1, 3, 4]) or len(img.shape) == 2
            ax = fig.add_subplot(rows * 2, columns, jdx + 1, xticks=[], yticks=[])
            cmap = None
            if (len(img.shape) == 3 and img.shape[2] == 1) or len(img.shape) == 2:
                cmap = "binary"
            if len(img.shape) == 3 and img.shape[2] == 1:
                img = img.reshape((img.shape[0], img.shape[1]))
            ax.imshow(img, cmap=cmap)
            ax.set_xlabel("Predicted = %s, Actual = %s" % (classes[yp[idx1]], classes[y_true[idx1]]))
            idx1 += 1
            jdx += 1

        for column in range(columns):
            if idx2 >= len(Y_pred):
                break
            yps = Y_pred[idx2]
            ax = fig.add_subplot(rows * 2, columns, jdx + 1, xticks=[], yticks=[])
            ind = np.arange(len(classes))
            rects = ax.bar(ind, yps, 0.25, label='Labels')
            ax.set_ylabel('Probability')
            ax.set_yticks(np.arange(0, 1.2, 0.2))
            ax.set_xticks(ind)
            ax.set_xticklabels(classes, rotation=90, ha='left')
            ax.legend()
            ax.tick_params(axis='both', which='major', labelsize=8)
            ax.tick_params(axis='both', which='minor', labelsize=6)
            idx2 += 1
            jdx += 1
    plt.show()


def show_kernel_activation():
    pass