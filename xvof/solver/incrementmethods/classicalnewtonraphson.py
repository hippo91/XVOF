#!/usr/bin/env python2.7
# -*- coding: iso-8859-1 -*-
"""
Classe d�finissant la correction classique appliqu�e sur la variable d'un Newton Raphson
"""
from xvof.solver.incrementmethods.newtonraphsonincrementbase import NewtonRaphsonIncrementBase


class ClassicalNewtonRaphsonIncrement(NewtonRaphsonIncrementBase):
    '''
    Classe d�finissant un incr�ment classique de l'algorithme de Newton-Raphson
    '''
    def __init__(self):
        super(ClassicalNewtonRaphsonIncrement, self).__init__()

    def computeIncrement(self, function_value, derivative_function_value):
        '''
        Calcul de l'incr�ment
        '''
        return - function_value / derivative_function_value