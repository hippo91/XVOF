# -*- coding: iso-8859-1 -*-
"""
Classe d�finissant un �l�ment en 1d
"""
import ctypes
import numpy as np
import os

from xvof.cell import Cell
from xvof.data.data_container import DataContainer
from xvof.solver.functionstosolve.vnrenergyevolutionforveformulation import VnrEnergyEvolutionForVolumeEnergyFormulation
from xvof.solver.newtonraphson import NewtonRaphson


class OneDimensionCell(Cell):
    """
    Une classe pour les �l�ments en 1D
    """
    nbr_noeuds = 2

    @classmethod
    def computePseudo(cls, delta_t, rho_old, rho_new, size_new,
                      cel_son, a_pseudo, b_pseudo):
        """
        Calcul de la pseudo
        """
        # pylint: disable=too-many-arguments
        # 8 arguments semblent n�cessaires
        vnt = 1. / rho_old
        vnplusun = 1. / rho_new
        vnplusundemi = 0.5 * (vnt + vnplusun)
        vpointnplusundemi = 1. / delta_t * (vnplusun - vnt)
        divu = vpointnplusundemi / vnplusundemi
        pseudo = np.zeros(rho_old.shape, dtype=np.float64, order='C')
        mask = divu < 0.
        pseudo[mask] = 1. / vnplusundemi[mask] * \
            (a_pseudo * size_new[mask] ** 2 * vpointnplusundemi[mask] ** 2 / vnplusundemi[mask] ** 2 +
             b_pseudo * size_new[mask] * cel_son[mask] *
             abs(vpointnplusundemi[mask]) / vnplusundemi[mask])
        return pseudo

    @classmethod
    def computeTimeStep(cls, cfl, rho_old, rho_new, taille_new, cson_new,
                        pseudo):
        """
        Calcul du pas de temps
        """
        # pylint: disable=too-many-arguments
        # 7 arguments pour cette m�thode cela semble ok
        delta_t = np.zeros(rho_old.shape, dtype=np.float64, order='C')
        drho = rho_new - rho_old
        mask = drho > 0.1
        delta_t[mask] = cfl * taille_new[mask] / (cson_new[mask] ** 2 + 2. * pseudo[mask] / drho[mask]) ** 0.5
        mask = drho <= 0.1
        delta_t[mask] = cfl * taille_new[mask] / cson_new[mask]
        return delta_t

    def __init__(self, number_of_elements):
        Cell.__init__(self, number_of_elements)
        self._function_to_vanish = VnrEnergyEvolutionForVolumeEnergyFormulation()
        self._solver = NewtonRaphson(self._function_to_vanish)
        #
        if DataContainer().hasExternalSolver():
            self._external_library = DataContainer().getExternalSolverPath()
        else:
            self._external_library = None
        if self._external_library is not None :
            _path = os.path.join(*(os.path.split(__file__)[:-1] + (self._external_library,)))
            self._mod = ctypes.cdll.LoadLibrary(_path)
            self._computePressureExternal = self._mod.launch_vnr_resolution
            self._computePressureExternal.argtypes = ([ctypes.POINTER(ctypes.c_double), ] * 4 +
                [ctypes.c_int, ] + [ctypes.POINTER(ctypes.c_double), ] * 3)

    @property
    def mass(self):
        """ Masse de l'�l�ment """
        return self.size_t * DataContainer().geometric.section * \
               self.density.current_value

    @property
    def pressure_field(self):
        """
        Pressure field
        """
        return self.pressure.current_value

    @property
    def density_field(self):
        """
        Density field
        """
        return self.density.current_value

    @property
    def energy_field(self):
        """
        Internal energy field
        """
        return self.energy.current_value

    @property
    def pseudoviscosity_field(self):
        """
        Pseudoviscosity field
        """
        return self.pseudo.current_value
    # --------------------------------------------------------
    #            DEFINITION DES METHODES                     #
    # --------------------------------------------------------
    def _computeNewPressureWithExternalLib(self, density_current, density_new, pressure_current, pseudo_current,
                                           energy_current, energy_new, pressure_new, vson_new):
        pb_size = ctypes.c_int()
        pb_size.value = energy_new.shape[0]
        c_density = density_current.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        n_density = density_new.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        true_pressure = (pressure_current + 2. * pseudo_current)
        c_pressure = true_pressure.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        c_energy = energy_current.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        n_energy = energy_new.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        n_pressure = pressure_new.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        n_sound_speed = vson_new.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
        self._computePressureExternal(c_density, n_density, c_pressure, c_energy, pb_size,
                                      n_energy, n_pressure, n_sound_speed)
        energy_n = n_energy[0:pb_size.value]
        pressure_n = n_pressure[0:pb_size.value]
        vson_n = n_sound_speed[0:pb_size.value]
        return energy_n, pressure_n, vson_n

    def computeNewPressure(self, mask):
        """
        Calcul du triplet energie, pression, vitesse du son
        au pas de temps suivant
        Formulation v-e
        """
        if self._external_library is not None:
            self.energy.new_value[mask], self.pressure.new_value[mask], self.sound_velocity.new_value[mask] = \
                self._computeNewPressureWithExternalLib(self.density.current_value[mask], self.density.new_value[mask],
                                                        self.pressure.current_value[mask],
                                                        self.pseudo.current_value[mask],
                                                        self.energy.current_value[mask], self.energy.new_value[mask],
                                                        self.pressure.new_value[mask],
                                                        self.sound_velocity.new_value[mask])
        else:
            shape = self.energy.new_value[mask].shape
            new_pressure_value = np.zeros(shape, dtype=np.float64, order='C')
            new_vson_value = np.zeros(shape, dtype=np.float64, order='C')
            dummy = np.zeros(shape, dtype=np.float64, order='C')
            my_variables = {'EquationOfState': DataContainer().material.eos,
                            'OldDensity': self.density.current_value[mask],
                            'NewDensity': self.density.new_value[mask],
                            'Pressure': self.pressure.current_value[mask] + 2. * self.pseudo.current_value[mask],
                            'OldEnergy': self.energy.current_value[mask]}
            self._function_to_vanish.setVariables(my_variables)
            self.energy.new_value[mask] = self._solver.computeSolution(self.energy.current_value[mask])
            DataContainer().material.eos.solveVolumeEnergy(1. / self.density.new_value[mask],
                                                           self.energy.new_value[mask],
                                                           new_pressure_value, new_vson_value, dummy)
            self.pressure.new_value[mask] = new_pressure_value
            self.sound_velocity.new_value[mask] = new_vson_value
            self._function_to_vanish.eraseVariables()

    def computeSize(self, topologie, vecteur_coord_noeuds):
        """
        Calcul de la longueur de l'�l�ment (� t)
        """
        for ielem in xrange(self._shape[0]):
            ind_nodes = topologie.getNodesBelongingToCell(ielem)
            self._size_t[ielem] = abs(vecteur_coord_noeuds[ind_nodes[0]] -
                                      vecteur_coord_noeuds[ind_nodes[1]])

    def computeNewSize(self, topologie, vecteur_coord_noeuds, mask, time_step=None):
        """
        Calcul de la nouvelle longueur de l'�l�ment (� t+dt)
        """
        connectivity = np.array(topologie._nodes_belonging_to_cell)
        size_t_plus_dt = abs(vecteur_coord_noeuds[connectivity[:, 0]] -
                             vecteur_coord_noeuds[connectivity[:, 1]]).reshape(self.number_of_cells)
        self._size_t_plus_dt[mask] = size_t_plus_dt[mask]

    def computeNewDensity(self, mask):
        """
        Calcul de la densite a l'instant t+dt basee sur
        la conservation de la masse
        """
        self.density.new_value[mask] = \
            self.density.current_value[mask] * self.size_t[mask] / self.size_t_plus_dt[mask]

    def computeNewPseudo(self, delta_t, mask):
        """
        Calcul de la nouvelle pseudo
        """
        self.pseudo.new_value[mask] = \
            OneDimensionCell.computePseudo(delta_t, self.density.current_value[mask], self.density.new_value[mask],
                                           self.size_t_plus_dt[mask], self.sound_velocity.current_value[mask],
                                           DataContainer().numeric.a_pseudo, DataContainer().numeric.b_pseudo)

    def computeNewTimeStep(self, mask):
        """
        Calcul du pas de temps dans l'�l�ment
        """
        cfl = DataContainer().numeric.cfl
        dt = \
            OneDimensionCell.computeTimeStep(cfl, self.density.current_value, self.density.new_value,
                                             self.size_t_plus_dt, self.sound_velocity.new_value,
                                             self.pseudo.current_value)
        self._dt[mask] = dt[mask]

    def imposePressure(self, ind_cell, pression):
        """
        On impose la pression � t+dt (par exemple pour endommagement)
        """
        self.pressure.new_value[ind_cell] = pression