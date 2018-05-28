import numpy as np
import pandas as pd
from sklearn import metrics
import matplotlib.pyplot as plt


def plot_roc(model, parameters, y_true):
    """
    Arguments:
    model - trained model such as DecisionTreeClassifier, etc.
    parameters - array-like or sparse matrix of shape  [n_samples, n_features]. The input samples.
    y_true - True binary labels in range {0, 1} or {-1, 1}. If labels are not binary, pos_label should be explicitly given.
    """
    if model is None:
        return 0., 0., np.array([])

    predicted = model.predict_proba(parameters)[: ,1]
    threshold = 0.5
    predicted_binary = (predicted > threshold).astype(int)

    fpr, tpr, threshold = metrics.roc_curve(y_true, predicted, pos_label=1)

    roc_auc = metrics.auc(fpr, tpr)
    ks = np.max(tpr - fpr) # Kolmogorov-Smirnov test

    print('ROC_auc = ', roc_auc)
    print('KS_test = ', ks)
    print('AUC score: %f ' % metrics.roc_auc_score(y_true, predicted))

    try:
        plt.title('%s ROC curve ' % model.__class__.__name__)
        plt.plot(fpr, tpr, 'b', label='AUC = %0.2f' % roc_auc)
        plt.legend(loc='lower right')
        plt.plot([0 ,1], [0 ,1], 'r--')
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')

        # plt.savefig('ROC_curve.png')
        plt.show()
    except: pass
    return roc_auc, ks, threshold

