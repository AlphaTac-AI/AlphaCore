import time
import pickle
import json
import os

def report(msg,tic=None,print_out=True):
    length = 100
    report = "\n"+">>>>  "+ msg + " "
    if tic:
        report += '-' * (100 - len(report))
        report +=" TC:{0:.4g}".format(time.time()-tic)
    report+="\n"
    if print_out:
        print(report)
    if not tic:
        return time.time()


def load_obj(filename):
    try:
        with open(filename,'rb') as f:
            obj =  pickle.load(f)
            return obj
    except Exception as e:
        print("Can't load obj:{0}".format(str(e)))

def save_obj(obj,filename):
    try:
        with open(filename,'wb') as f:
            pickle.dump(obj,f,pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print("Can't save obj:{0}".format(str(e)))


def load_json(filename):
    try:
        with open(filename,'r') as f:
            dic =  json.load(f)
        return dic
    except Exception as e:
        print("Can't load dict:{0}".format(str(e)))

def save_json(dic,filename):
    try:
        with open(filename,'w') as f:
            json.dump(dic,f)
    except Exception as e:
        print("Can't save dict:{0}".format(str(e)))


def check_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)