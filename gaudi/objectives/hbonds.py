#!/usr/bin/python

##############
# GAUDIasm: Genetic Algorithms for Universal
# Design Inference and Atomic Scale Modeling
# Authors:  Jaime Rodriguez-Guerra Pedregal
#            <jaime.rodriguezguerra@uab.cat>
#           Jean-Didier Marechal
#            <jeandidier.marechal@uab.cat>
# Web: https://bitbucket.org/jrgp/gaudi
##############

"""
:mod:`gaudi.objectives.hbonds` is a wrapper around Chimera's
`FindHBond`. It returns the number of hydrogen bonds that can
be formed between the target molecule and its environment.

.. todo::

    Evaluate the possible HBonds with some kind of function that
    gives a rough idea of the strength (energy) of each of them.
"""

# Python
import logging
# Chimera
import chimera
import FindHBond
# GAUDI
from gaudi.objectives import ObjectiveProvider
import gaudi.box

logger = logging.getLogger(__name__)


def enable(**kwargs):
    return Hbonds(**kwargs)


class Hbonds(ObjectiveProvider):

    def __init__(self, probe=None, distance_tolerance=0.4, angle_tolerance=20.0, radius=5.0,
                 *args, **kwargs):
        ObjectiveProvider.__init__(self, **kwargs)
        self._probe = probe
        self.distance_tolerance = distance_tolerance
        self.angle_tolerance = angle_tolerance
        self.radius = radius

    @property
    def molecules(self):
        return tuple(m.compound.mol for m in self.parent.genes.values()
                     if m.__class__.__name__ == "Molecule")

    @property
    def probe(self):
        return self.parent.genes[self._probe].compound.mol

    def evaluate(self):
        test_atoms = self.surrounding_atoms()
        hbonds = FindHBond.findHBonds(self.molecules, cacheDA=self._cache,
                                      donors=test_atoms, acceptors=test_atoms,
                                      distSlop=self.distance_tolerance,
                                      angleSlop=self.angle_tolerance)
        hbonds = FindHBond.base.filterHBondsBySel(
            hbonds, self.probe.atoms, 'any')

        return len(hbonds)

    def display(self, bonds):
        return gaudi.box.draw_interactions(bonds, name=self.name,
                                           startCol='00FFFF', endCol='00FFFF')

    ###
    def surrounding_atoms(self):
        self.env.clear()
        self.env.add(self.probe.atoms)
        self.env.merge(chimera.selection.REPLACE,
                       chimera.specifier.zone(
                           self.env, 'atom', None, self.radius, self.molecules
                       )
                       )
        return self.env.atoms()
