#!/usr/bin/env python2.7
# -*- coding: iso-8859-1 -*-
"""
Classe d�finissant une pression constante
"""
from xvof.pressurelaw.pressurelaw import PressureLaw


class ConstantPressure(PressureLaw):
    """
    Une pression constante
    """
    def __init__(self, value):
        PressureLaw.__init__(self)
        self.__value = value

    def evaluate(self, time, *args, **kwargs):
        return self.__value