#!/usr/bin/env python2.7
# -*- coding: iso-8859-1 -*-
"""
Classe d�finissant un �l�ment enrichi en 1d
"""
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
############ IMPORTATIONS DIVERSES  ####################
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
from xvof.element import Element1d
from xvof.node import Node1dUpgraded
import numpy as np

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
####### DEFINITION DES CLASSES & FONCTIONS  ###############
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$


class Element1dUpgraded(Element1d):
    """
    Une classe pour les �l�ments enrichis dans le cas 1d
    """
    def __init__(self, element_origin, pos_discontin):
        Element1d.__init__(self, element_origin.proprietes,
                           element_origin.indice, element_origin.noeuds)
        #
        if(pos_discontin < 0.) or (pos_discontin > 1.):
            message = "La position de la discontinuit� dans"
            message += " l'�l�ment enrichi doit �tre comprise entre 0 et 1!"
            raise SystemExit(message)
        # Les noeuds d'un �l�ment enrichi sont �galement enrichis
        self._noeuds = map(Node1dUpgraded, self.noeuds)
        #
        self._pression_t_classique = element_origin.pression_t
        self._pression_t_plus_dt_classique = element_origin.pression_t_plus_dt
        self._rho_t_classique = element_origin.rho_t
        self._rho_t_plus_dt_classique = element_origin.rho_t_plus_dt
        self._nrj_t_classique = element_origin.nrj_t
        self._nrj_t_plus_dt_classique = element_origin.nrj_t_plus_dt
        self._pseudo_plus_undemi_classique = element_origin.pseudo
        self._cson_t_classique = element_origin.cson_t
        self._cson_t_plus_dt_classique = element_origin.cson_t_plus_dt
        #
        self._pression_t_enrichi = 0.
        self._pression_t_plus_dt_enrichi = 0.
        self._rho_t_enrichi = 0.
        self._rho_t_plus_dt_enrichi = 0.
        self._nrj_t_enrichi = 0.
        self._nrj_t_plus_dt_enrichi = 0.
        self._pseudo_plus_undemi_enrichi = 0.
        self._cson_t_enrichi = 0.
        self._cson_t_plus_dt_enrichi = 0.
        #
        self._taille_gauche_t = element_origin.taille_t * pos_discontin
        self._taille_gauche_t_plus_dt = element_origin.taille_t_plus_dt * pos_discontin
        self._taille_droite_t = element_origin.taille_t * (1. - pos_discontin)
        self._taille_droite_t_plus_dt = element_origin.taille_t_plus_dt * (1. - pos_discontin)

    @property
    def taille_t_gauche(self):
        """
        Taille de la partie gauche de l'�l�ment au temps t
        """
        return self._taille_gauche_t

    @property
    def taille_t_droite(self):
        """
        Taille de la partie droite de l'�l�ment au temps t
        """
        return self._taille_droite_t

    @property
    def taille_t_plus_dt_gauche(self):
        """
        Taille de la partie gauche de l'�l�ment au temps t+dt
        """
        return self._taille_gauche_t_plus_dt

    @property
    def taille_t_plus_dt_droite(self):
        """
        Taille de la partie droite de l'�l�ment au temps t+dt
        """
        return self._taille_droite_t_plus_dt

    @property
    def pression_t_gauche(self):
        """
        Pression dans la partie gauche de l'�l�ment au temps t
        """
        return self._pression_t_classique - self._pression_t_enrichi

    @property
    def pression_t_droite(self):
        """
        Pression dans la partie droite de l'�l�ment au temps t
        """
        return self._pression_t_classique + self._pression_t_enrichi

    @property
    def rho_t_gauche(self):
        """
        Densit� dans la partie gauche de l'�l�ment au temps t
        """
        return self._rho_t_classique - self._rho_t_enrichi

    @property
    def rho_t_droite(self):
        """
        Densit� dans la partie droite de l'�l�ment au temps t
        """
        return self._rho_t_classique + self._rho_t_enrichi

    @property
    def rho_t_plus_dt_gauche(self):
        """
        Densit� dans la partie gauche de l'�l�ment au temps t+dt
        """
        return self._rho_t_plus_dt_classique - self._rho_t_plus_dt_enrichi

    @property
    def rho_t_plus_dt_droite(self):
        """
        Densit� dans la partie droite de l'�l�ment au temps t+dt
        """
        return self._rho_t_plus_dt_classique + self._rho_t_plus_dt_enrichi

    @property
    def nrj_t_gauche(self):
        """
        Densit� dans la partie gauche de l'�l�ment au temps t
        """
        return self._nrj_t_classique - self._nrj_t_enrichi

    @property
    def nrj_t_droite(self):
        """
        Energie dans la partie droite de l'�l�ment au temps t
        """
        return self._nrj_t_classique + self._nrj_t_enrichi

    @property
    def nrj_t_plus_dt_gauche(self):
        """
        Energie dans la partie gauche de l'�l�ment au temps t+dt
        """
        return self._nrj_t_plus_dt_classique - self._nrj_t_plus_dt_enrichi

    @property
    def nrj_t_plus_dt_droite(self):
        """
        Energie dans la partie droite de l'�l�ment au temps t+dt
        """
        return self._nrj_t_plus_dt_classique + self._nrj_t_plus_dt_enrichi

    #------------------------------------------------------------
    # DEFINITIONS DES METHODES
    #------------------------------------------------------------
    def calculer_nouvo_pression(self):
        """
        Calcul du triplet energie, pression, vitesse du son
        au pas de temps suivant
        Formulation v-e
        """
        nrj_t_plus_dt_g, pression_t_plus_dt_g, cson_t_plus_dt_g = \
        Element1d.newton_raphson_for_ve(self.proprietes.material.eos,
                self.rho_t_gauche, self.rho_t_plus_dt_gauche,
                self.pression_t_gauche, self.pseudo_gauche,
                self.nrj_t_gauche)
        nrj_t_plus_dt_d, pression_t_plus_dt_d, cson_t_plus_dt_d = \
        Element1d.newton_raphson_for_ve(self.proprietes.material.eos,
                self.rho_t_droite, self.rho_t_plus_dt_droite,
                self.pression_t_droite, self.pseudo_droite,
                self.nrj_t_droite)
        #
        self._pression_t_plus_dt_classique = (pression_t_plus_dt_g +
            pression_t_plus_dt_d) / 2.0
        self._pression_t_plus_dt_enrichi = (pression_t_plus_dt_g -
            pression_t_plus_dt_d) / 2.0
        #
        self._nrj_t_plus_dt_classique = (nrj_t_plus_dt_g +
            nrj_t_plus_dt_d) / 2.0
        self._nrj_t_plus_dt_enrichi = (nrj_t_plus_dt_g -
            nrj_t_plus_dt_d) / 2.0
        #
        self._cson_t_plus_dt_classique = (cson_t_plus_dt_g +
            cson_t_plus_dt_d) / 2.0
        self._nrj_t_plus_dt_enrichi = (cson_t_plus_dt_g -
            cson_t_plus_dt_d) / 2.0

    def calculer_nouvo_taille(self, delta_t):
        """
        Calcul des nouvelles longueurs de l'�l�ment

        TEST UNITAIRE
        >>> import numpy as np
        >>> from xvof.node import Node1d
        >>> from xvof.miscellaneous import *
        >>> from xvof.equationsofstate import MieGruneisen
        >>> ee = MieGruneisen()
        >>> num_props = numerical_props(0.2, 1.0, 0.35)
        >>> mat_props = material_props(1.0e+05, 0.0, 8129., ee)
        >>> geom_props = geometrical_props(1.0e-06)
        >>> props = properties(num_props, mat_props, geom_props)
        >>> noda = Node1d(1, poz_init=np.array([0.6]), section=1.0e-06)
        >>> nodb = Node1d(1, poz_init=np.array([-0.2]), section=1.0e-06)
        >>> my_elem = Element1d(props, 123, [noda, nodb])
        >>> my_elem_up = Element1dUpgraded(my_elem, 0.5)
        >>> my_elem_up.calculer_nouvo_taille(1.0e-06)
        >>> print my_elem_up.taille_t_plus_dt_gauche
        [ 0.4]
        >>> print my_elem_up.taille_t_plus_dt_droite
        [ 0.4]
        """
        # Les noeuds sont class�s par coord croissante
        nod_g = self.noeuds[0]
        nod_d = self.noeuds[1]
        self._taille_gauche_t_plus_dt = self.taille_t_gauche + \
            (0.5 * (nod_d.upundemi_classique - nod_g.upundemi_enrichi) -
             0.5 * (nod_g.upundemi_classique - nod_g.upundemi_enrichi)) \
            * delta_t
        self._taille_droite_t_plus_dt = self.taille_t_droite + \
            (0.5 * (nod_d.upundemi_classique + nod_d.upundemi_enrichi) -
             0.5 * (nod_g.upundemi_classique + nod_d.upundemi_enrichi)) \
             * delta_t

    def calculer_nouvo_densite(self):
        """
        Calcul des nouvelles densit�s
        """
        densite_gauche_t_plus_dt = self.rho_t_gauche * self.taille_t_gauche \
            / self.taille_t_plus_dt_gauche
        densite_droite_t_plus_dt = self.rho_t_droite * self.taille_t_droite \
            / self.taille_t_plus_dt_droite
        self._rho_t_plus_dt_classique = \
            (densite_gauche_t_plus_dt + densite_droite_t_plus_dt) * 0.5
        self._rho_t_plus_dt_enrichi = \
            (densite_droite_t_plus_dt - densite_gauche_t_plus_dt) * 0.5
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
#######          PROGRAMME PRINCIPAL        ###############
#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
if __name__ == "__main__":
    import doctest
    TESTRES = doctest.testmod(verbose=0)
    if(TESTRES[0] == 0):
        print "TESTS UNITAIRES : OK"