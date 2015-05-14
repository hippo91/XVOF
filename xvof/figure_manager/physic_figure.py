#!/usr/bin/env python2.7
# -*- coding: iso-8859-1 -*-
"""
Classe d�finissant une figure
"""
from os import sep

import matplotlib.pyplot as plt


class PhysicFigure(object):
    """
    Figure
    """
    def __init__(self, X, Y, xlabel="X", ylabel="Y", titre="titre", save_path=None):
        self._fig = plt.figure()
        self._ax = self._fig.add_subplot(111)
        self._line, = self._ax.plot(X, Y, '-+')
        self._ax.set_xlabel(xlabel)
        self._ax.set_ylabel(ylabel)
        self._ax.set_title(titre)
        self._save_path = save_path
        self._fig_number = 1
        self._title = titre

    def set_y_limit(self, val_min=0., val_max=1.0):
        """ Fixation des limites en y"""
        self._ax.set_ylim([val_min, val_max])

    def set_x_limit(self, val_min=0., val_max=1.0):
        """ Fixation des limites en x"""
        self._ax.set_xlim([val_min, val_max])

    def update(self, X=None, Y=None, title_comp=None):
        """
        Mise � jour de l'image pour avoir une animation
        Sauvegarde de l'image si pr�sence d'un path
        """
        if(X is not None):
            self._line.set_xdata(X)
        if(Y is not None):
            self._line.set_ydata(Y)
        if(title_comp is not None):
            self._ax.set_title(self._title + ' ' + title_comp)
        self._fig.canvas.draw()
        if (self._save_path is not None):
            fig_path = self._save_path + sep + self._title
            fig_path += "_{:04d}.png".format(self._fig_number)
            fig_path = fig_path.replace(" ", "_")
            self._fig.savefig(fig_path)
            self._fig_number += 1
