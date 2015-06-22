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
:mod:`gaudi.objectives.distance` calculates the distance between two
given atoms. It returns the absolute differenec between the calculated
distance and the target value.
"""

# Python
import numpy
import logging
# Chimera
import chimera
# GAUDI
from gaudi.objectives import ObjectiveProvider
import gaudi.parse

logger = logging.getLogger(__name__)


def enable(**kwargs):
    return Distance(**kwargs)


class Distance(ObjectiveProvider):

    def __init__(self, threshold=None, tolerance=-0.1, target=None, probes=None,
                 *args, **kwargs):
        ObjectiveProvider.__init__(self, **kwargs)
        self.threshold = threshold
        self.tolerance = tolerance
        self._probes = probes
        self._mol, self._serial = gaudi.parse.parse_rawstring(target)

    @property
    def target(self):
        try:
            if isinstance(self._serial, int):
                atom = next(a for a in self.parent.genes[self._mol].compound.mol.atoms
                            if self._serial == a.serialNumber)
            else:
                atom = next(a for a in self.parent.genes[self._mol].compound.mol.atoms
                            if self._serial == a.name)
        except KeyError:
            logger.exception("Molecule not found")
            raise
        except StopIteration:
            logger.exception("No atoms matched for target %s", atom)
            raise
        else:
            return atom

    @property
    def probes(self):
        for probe in self._probes:
            mol, serial = gaudi.parse.parse_rawstring(probe)
            try:
                if isinstance(serial, int):
                    atom = next(a for a in self.parent.genes[mol].compound.mol.atoms
                                if serial == a.serialNumber)
                elif serial == 'last':
                    atom = self.parent.genes[mol].compound.acceptor
                else:
                    atom = next(a for a in self.parent.genes[mol].compound.mol.atoms
                                if serial == a.name)
            except KeyError:
                logger.exception("Molecule not found")
                raise
            except StopIteration:
                logger.exception("No atoms matched for target %s", probe)
                raise
            else:
                yield atom
    ###

    def evaluate(self):
        distances = []
        for a in self.probes:
            d = self._distance(a, self.target)
            if self.threshold == 'covalent':
                threshold = chimera.Element.bondLength(
                    a.element, self.target.element)
            else:
                threshold = self.threshold
            d = d - threshold
            if d < self.tolerance:
                distances.append(-1000 * self.weight)
            else:
                distances.append(d)

        return numpy.mean(numpy.absolute(distances))

    @staticmethod
    def _distance(atom1, atom2):
        return atom1.xformCoord().distance(atom2.xformCoord())
