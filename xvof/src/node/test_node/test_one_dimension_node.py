#!/usr/bin/env python2.7
# -*- coding: iso-8859-1 -*-
"""
Classe de test du module node1d
"""
import numpy as np
import unittest
import mock
import os

from xvof.src.mesh.topology1d import Topology1D
from xvof.src.node.one_dimension_node import OneDimensionNode
from xvof.src.mass_matrix.mass_matrix_utilities import inverseMasse
from xvof.src.data.data_container import DataContainer


class Node1dTest(unittest.TestCase):
    """
    Test case utilis� pour test les fonctions du module 'Node1d'
    """
    def setUp(self):
        """
        Pr�paration des tests
        """
        data_file_path = os.path.join(os.path.dirname(__file__), "../../../tests/0_UNITTEST/XDATA_hydro.xml")
        self.test_datacontainer = DataContainer(data_file_path)

        class element:
            def __init__(self, poz, pressure, pseudo, masse):
                self.coord = poz
                self.pression_new = pressure
                self.pseudo = pseudo
                self.masse = masse

        self.elem_0 = element(np.array([-0.5]), 2.5e+09, 1.0e+09, 1. / 4.)
        self.elem_1 = element(np.array([0.5]), 1.0e+09, 0.5e+09, 1. / 4.)
        self.elem_2 = element(np.array([1.5]), 2.0e+09, 0.e+09, 1. / 2.)
        self.my_nodes = OneDimensionNode(4, np.array([[-1., ], [0., ], [1., ], [2., ]], ndmin=2),
                                         np.array([[0., ], [0., ], [0., ], [0., ]], ndmin=2),
                                         section=1.0e-06)

    def tearDown(self):
        DataContainer.clear()
        pass

    def test_compute_new_force(self):
        """
        Test de la m�thode Node1d.compute_new_force()
        """
        topo = Topology1D(4, 3)
        vecteur_contrainte = np.array([self.elem_0.pression_new, self.elem_1.pression_new, self.elem_2.pression_new])
        self.my_nodes.compute_new_force(topo, vecteur_contrainte)
        np.testing.assert_array_equal(self.my_nodes.force.flatten(), np.array([2500., -1500., 1000., -2000.]))

    def test_compute_new_velocity(self):
        """
        Test de la m�thode Node1d.compute_new_velocity()
        """
        topo = Topology1D(4, 3)
        vecteur_contrainte = np.array([self.elem_0.pression_new, self.elem_1.pression_new, self.elem_2.pression_new])
        self.my_nodes.compute_new_force(topo, vecteur_contrainte)  # V�rifi�e par test dans test_node.py
        mask = np.empty([4], dtype=bool)
        mask[:] = True
        mass_matrix = np.array([[1./8., ], [1./4., ], [3./8., ], [1./4., ]])
        inv_mass_matrix = inverseMasse(mass_matrix)
        self.my_nodes.compute_new_velocity(1.0e-03, mask, inv_mass_matrix)
        np.testing.assert_allclose(self.my_nodes.upundemi.flatten(), np.array([20., -6., 2.6666667, -8.]))

    def test_apply_pressure(self):
        """
        Test de la methode apply_pressure() de one_dimension_node
        """
        topo = Topology1D(4, 3)
        vecteur_contrainte = np.array([self.elem_0.pression_new, self.elem_1.pression_new, self.elem_2.pression_new])
        self.my_nodes.compute_new_force(topo, vecteur_contrainte)  # V�rifi�e par test dans test_node.py

        self.my_nodes.apply_pressure(0, 1.e+09)
        np.testing.assert_array_equal(self.my_nodes.force[0], np.array([3500.]))

    def test_apply_correction_reference_bar(self):
        """
        Test de la m�thode apply_correction_reference_bar
        """
        delta_t = 1.
        mask = np.array([False, False, True, True])
        inv_complete_mass_matrix = np.array([[1, 2], [2, 3]])
        inv_wilkins_mass_matrix = np.array([[2, 3], [4, 5]])
        self.my_nodes._force = np.array([[1, ],  [2,],  [3, ], [3, ]])
        self.my_nodes._upundemi = np.zeros([4, 1])

        self.my_nodes.apply_correction_reference_bar(delta_t, inv_complete_mass_matrix, inv_wilkins_mass_matrix, mask)

        exact = np.array([[-6.,], [-12., ]])
        np.testing.assert_allclose(self.my_nodes.upundemi[mask], exact)


if __name__ == '__main__':
    unittest.main()
