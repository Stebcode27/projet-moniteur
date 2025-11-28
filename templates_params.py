"""Definition des templates paramètres du moniteur multiparamétrique"""

import numpy as np

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
    
    def __init__(self):
        super(Ecg, self).__init__("ecg")
        Param._set_maxpoint_(self, 250)


class Saturation(Param):

    def __init__(self):
        super(Saturation, self).__init__("saturation")
        Param._set_maxpoint_(self, 50)

class Pression(Param):

    def __init__(self):
        super(Pression, self).__init__("pression")
        
    
if __name__ == '__main__':
    ecg = Ecg()
    ecg._set_data_(50*np.ones(50))
    print(ecg._get_data_())