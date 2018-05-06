import pandas as pd
import gc
import xgboost as xgb
from xgboost import XGBClassifier, plot_importance
from sklearn import metrics
from lib.utils  import *
from lib.feature_lib import *



class Solution:
    train_df = None
    label_df = None
    test_df = None

    f_ppl = []
    train_f_set = None
    test_f_set = None

    model = None
    train_result = None
    test_result = None

    log = None
    method = 'xgb'
    input_path = '../input/'
    output_path = '../output/'
    data_set = None
    transductive =False
    para_tune_fcg = None

    def __init__(self):
        pass

    def load_dataset(self):
        tic = report("Load Dataset Start")
        if self.transductive:
            self.data_set.load_train(self)
            self.data_set.load_test(self)
        else:
            self.data_set.load_test(self)
        report("Load Dataset Done", tic)

    def build_features(self):
        tic = report("Build Features Start")
        if self.transductive:
            merge = pd.concat([self.train_df, self.test_df])

            merge, f_set = build_features(merge, self.f_ppl)

            self.train_f_set,self.test_f_set = f_set,f_set

            self.train_df, self.test_df = merge[:self.train_df.shape[0]],merge[self.train_df.shape[0]:].reset_index(drop=True)
        else:
            self.train_df, self.train_f_set = build_features(self.train_df, self.f_ppl)

            self.test_df, self.test_f_set = build_features(self.test_df, self.f_ppl)

            if self.train_f_set !=self.test_f_set:

                print("Warning training featue set is different with testing feature set")

        print("Feature Selected:\t{0}".format(','.join(self.train_f_set)))
        report("Build Features Done", tic)
        print(self.train_df.head(5))
        print(self.test_df.head(5))

    def init_model(self):
        if self.method == 'xgb':
            xgb_init(self)
        elif self.method == 'lgbm':
            pass

    def para_tune(self):
        tic = report("Parameter Tuning Start")
        if self.method == 'xgb':
            xgb_pt(self)
        elif self.method == 'lgbm':
            pass
        report("Parameter Tuning Done", tic)

    def train(self):
        tic = report("Model training Start")
        if self.method == 'xgb':
            xgb_train(self)
        elif self.method == 'lgbm':
            pass
        report("Model training Done", tic)

    def test(self):
        tic = report("Test Start")
        if self.method == 'xgb':
            xgb_test(self)
        elif self.method == 'lgbm':
            pass
        report("Test Done", tic)

    def save_test(self):
        check_dir(self.output_path)
        self.test_result.to_csv(self.output_path + self.result_filename, float_format='%.8f', index=False)








def xgb_init(s):
    s.model =  XGBClassifier(learning_rate=0.3,
                          n_estimators=1000,
                          objective='binary:logistic',
                          nthread=8,
                          max_depth=5,
                          min_child_weight=0,
                          subsample=0.9,
                          colsample_bytree=0.7,
                          reg_alpha=4,
                          scale_pos_weight=9,
                          seed=99)



def modelfit(model, train_df, label_df, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
    if useTrainCV:
        xgb_param = model.get_xgb_params()
        dtrain = xgb.DMatrix(train_df.values, label=label_df.values)
        cvresult = xgb.cv(xgb_param, dtrain, num_boost_round=model.get_params()['n_estimators'], nfold=cv_folds,
            metrics='auc', early_stopping_rounds=early_stopping_rounds, verbose_eval=True)
        model.set_params(n_estimators=cvresult.shape[0])
        del dtrain, cvresult
        gc.collect()
    # Fit the algorithm on the data
    model.fit(train_df, label_df, eval_metric='auc')

def xgb_train(s,eval_metric='auc'):
    modelfit(s.model,s.train_df,s.label_df)
    s.train_result = s.model.predict_proba(s.train_df)[:,1]
    print("\nModel Report")
    print("AUC Score (Train):", metrics.roc_auc_score(s.label_df.values, s.train_result))
