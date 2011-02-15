#!/usr/bin/env python
"""A modules holding all the data models used in kmos.
"""

from kiwi.python import Settable
from utils import CorrectlyNamed

from copy import deepcopy


class Attributes:
    """Handy class that easily allows to define data structures
    that can only hold a well-defined set of fields
    """
    attributes = []
    def __init__(self, **kwargs):
        for attribute in self.attributes:
            if kwargs.has_key(attribute):
                self.__dict__[attribute] = kwargs[attribute]
        for key in kwargs:
            if key not in self.attributes:
                raise AttributeError('Tried to initialize illegal attribute %s' % key)
    def __setattr__(self, attrname, value):
        if attrname in self.attributes:
            self.__dict__[attrname] = value
        else:
            raise AttributeError, 'Tried to set illegal attribute %s' % attrname




class Site(Attributes):
    """A class holding exactly one lattice site
    """
    attributes = ['name', 'x', 'y', 'z', 'site_class']
    # vector is now a list of floats for the graphical representation
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.site_class = kwargs['site_class'] if  'site_class' in kwargs else ''
        self.name = kwargs['name'] if 'name' in kwargs else ''

    def __repr__(self):
        return '<SITE> %s %s %s' % (self.name, (self.x, self.y, self.z), self.site_class)


class ProcessFormSite(Site):
    """This is just a little varient of the site object,
    with the sole difference that it has a layer attribute
    and is meant to be used in the process form. This separation was chosen, since the Site object as in the ProjectTree should not have a layer attribute to avoid data duplication but in the ProcessForm we need this to define processes
    """
    attributes = Site.attributes
    attributes.append('layer')
    def __init__(self, **kwargs):
        Site.__init__(self, **kwargs)
        self.layer = kwargs['layer'] if 'layer' in kwargs else ''


class Grid(Attributes):
    """A grid is simply a guide to the eye to set up
    sites in unit cell at specific location. It has no effect for the kMC model itself
    """
    attributes = ['x','y','z','offset_x','offset_y','offset_z',]
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.x = kwargs['x'] if 'x' in kwargs else 1
        self.y = kwargs['y'] if 'y' in kwargs else 1
        self.z = kwargs['z'] if 'z' in kwargs else 1
        self.offset_x = kwargs['offset_x'] if 'offset_x' in kwargs else 0.0
        self.offset_y = kwargs['offset_y'] if 'offset_y' in kwargs else 0.0
        self.offset_z = kwargs['offset_z'] if 'offset_z' in kwargs else 0.0

    def __repr__(self):
        return ('<GRID> %s %s %s\noffset: %s %s %s' %
            (self.x, self.y, self.z,
            self.offset_x,
            self.offset_y,
            self.offset_z))
        
class Layer(Attributes, CorrectlyNamed):
    """A class that defines exactly one layer
    """
    attributes = ['name', 'grid','sites', 'site_classes', 'active']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.grid = kwargs['grid'] if 'grid' in kwargs else Grid()
        self.name = kwargs['name'] if 'name' in kwargs else ''
        self.active = kwargs['active'] if 'active' in kwargs else True
        self.sites = []

    def __repr__(self):
        return "<LAYER> %s\n[%s]\n" % (self.name, self.grid)

    def add_site(self, site):
        """Add a new site to a layer
        """
        self.sites.append(site)

            
    def get_info(self):
        if self.active:
            return 'visible'
        else:
            return 'invisible'


class ConditionAction(Attributes):
    """Class that holds either a condition or an action. Since both have the same attributes we use the same class here, and just store them in different lists, depending on its role
    """
    attributes = ['species', 'coord']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return "<COND_ACT> Species: %s Coord:%s\n" % (self.species, self.coord)

class Coord(Attributes):
    """Class that holds exactly one coordinate as used in the description
    of a process. The distinction between a Coord and a Site may seem superfluous but it is crucial to avoid to much data duplication
    """
    attributes = ['offset', 'name', 'layer']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        if len(self.offset) == 1 :
            self.offset = (self.offset[0], 0, 0)
        if len(self.offset) == 2 :
            self.offset = (self.offset[0], self.offset[1], 0)


    def __repr__(self):
        return '<COORD> %s.%s.%s' % (self.name, tuple(self.offset), self.layer)

    def __neg__(self):
        """When negating a lattice coordinate we only mean to negate to supercell part"""
        return Coord(name=self.name,layer=self.layer,offset=[-x for x in self.offset])

    def __sub__(a, b):
        """When subtracting to lattice coordinates from each other, i.e. a-b, we want
        to keep the name and layer from a, and just take the difference in suppercells
        """
        diff = [ (x-y) for (x,y) in zip(a.offset, b.offset) ]
        return Coord(name=a.name,layer=a.layer,offset=diff)

    def ff(self):
        """ff like 'Fortran Form'"""
        return "(/%s, %s, %s, %s_%s/)" % (self.offset[0], self.offset[1], self.offset[2], self.layer, self.name, )


class Species(Attributes):
    """Class that represent a species such as oxygen, empty, ... . Not empty
    is treated just like a species.
    """
    attributes = ['name', 'color', 'id']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return '<SPECIES> Name: %s Color: %s ID: %s\n' % (self.name, self.color, self.id)


class SpeciesList(Attributes):
    """A list of species
    """
    attributes = ['default_species', 'name']
    def __init__(self, **kwargs):
        kwargs['name'] = 'Species'
        Attributes.__init__(self, **kwargs)


class ProcessList(Settable):
    """A list of processes
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Processes'
        Settable.__init__(self, **kwargs)

    def __lt__(self, other):
        return self.name < other.name

class ParameterList(Settable):
    """A list of parameters
    """
    def __init__(self, **kwargs):
        kwargs['name'] = 'Parameters'
        Settable.__init__(self, **kwargs)


class LayerList(Attributes):
    """A list of layers
    """
    attributes = ['name', 'cell_size_x', 'cell_size_y', 'cell_size_z', 'default_layer']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.name = 'Lattice(s)'
        self.cell_size_x = kwargs['cell_size_x'] if 'cell_size_x' in kwargs else 1.
        self.cell_size_y = kwargs['cell_size_y'] if 'cell_size_y' in kwargs else 1.
        self.cell_size_z = kwargs['cell_size_z'] if 'cell_size_z' in kwargs else 1.
        self.default_layer = kwargs['default_layer'] if 'default_layer' in kwargs else 'default'


class Parameter(Attributes, CorrectlyNamed):
    """A parameter that can be used in a rate constant expression
    and defined via some init file
    """
    attributes = ['name', 'value']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)

    def __repr__(self):
        return '<PARAMETER> Name: %s Value: %s\n' % (self.name, self.value)

    def on_name__content_changed(self, _):
        self.project_tree.update(self.process)

    def get_info(self):
        return self.value


class Meta(Settable, object):
    """Class holding the meta-information about the kMC project
    """
    name = 'Meta'
    def __init__(self):
        Settable.__init__(self, email='', author='', debug=0, model_name='', model_dimension=0, )

    def add(self, attrib):
        for key in attrib:
            if key in ['debug', 'model_dimension']:
                self.__setattr__(key, int(attrib[key]))
            else:
                self.__setattr__(key, attrib[key])

    def get_extra(self):
        return "%s(%s)" % (self.model_name, self.model_dimension)



class Process(Attributes):
    """One process in a kMC process list
    """
    attributes = ['name', 'rate_constant', 'condition_list', 'action_list']
    def __init__(self, **kwargs):
        Attributes.__init__(self, **kwargs)
        self.condition_list = []
        self.action_list = []
            
    def __repr__(self):
        return '[PROCESS] Name:%s Rate: %s\nConditions: %s\nActions: %s' % (self.name, self.rate_constant, self.condition_list, self.action_list)

    def add_condition(self, condition):
        self.condition_list.append(condition)

    def add_action(self, action):
        self.action_list.append(action)

    def get_info(self):
        return self.rate_constant



class OutputList():
    """A dummy class, that will hold the values which are to be printed to logfile.
    """
    def __init__(self):
        self.name = 'Output'

class OutputItem(Attributes):
    """Not implemented yet
    """
    attributes = ['name', 'output']
    def __init__(self, *args, **kwargs):
        Attributes.__init__(self, **kwargs)
