
"""Definition des templates paramètres du moniteur multiparamétrique"""
import sys
import os

# Obtenir le chemin absolu du dossier racine du projet (mon_projet/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

import numpy as np
import serial
from scipy.signal import butter, filtfilt

#Template pour tous les paramètres du moniteur
class Param(object):

    def __init__(self, param_name):
        self.maxpoint = 1   #pour eviter les messages d'erreur en cas de manque de données
        self._data_ = np.zeros(self.maxpoint, dtype='int16')
        self.param_name = param_name

    #Les getters de chaque attribut
    def _get_data_(self):
        return self._data_
    def get_param_name(self):
        return self.param_name
    def get_maxpoint(self):
        return self.maxpoint
    
    #Les setters de chaque attribut
    def _set_maxpoint_(self, maxpoint):
        self.maxpoint = maxpoint
    def _set_data_(self, data):
        self._data_ = data

class Ecg(Param):
    
    def __init__(self, maxpoint):
        super(Ecg, self).__init__("ecg")
        Param._set_maxpoint_(self, maxpoint=maxpoint)
        self._set_data_(np.zeros(self.maxpoint))
        self.ptr=0
        self.update_interval = 100
        self.x_data = np.arange(self.ptr-self.maxpoint,self.ptr)
    
    def update_data(self):
        new_val = np.exp(-(self.ptr+1))+np.random.normal(size=1, scale=1, loc=0.5)*0.015
        self._data_[:-1]=self._data_[1:]
        self._data_[-1] = new_val[0]

        self.ptr+=1
        self.ptr%=10
        self.x_data = np.arange(self.ptr-self.maxpoint,self.ptr)


class Saturation(Param):

    def __init__(self):
        super(Saturation, self).__init__("saturation")
        Param._set_maxpoint_(self, 50)

class Pression(Param):

    def __init__(self):
        super(Pression, self).__init__("pression")
        
