#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
.. argparse::
   :module: py_trees.demos.blackboard
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard

.. graphviz:: dot/demo-blackboard.dot
   :align: center
   :caption: Dot Graph

.. figure:: images/blackboard_demo.png
   :align: center

   Console Screenshot
"""

##############################################################################
# Imports
##############################################################################

import argparse
import py_trees
import sys

import py_trees.console as console
import json


##############################################################################
# Classes
##############################################################################


def description():
    content = "Demonstrates usage of the blackboard and related behaviours.\n"
    content += "\n"
    content += "A sequence is populated with a few behaviours that exercise\n"
    content += "reading and writing on the Blackboard in interesting ways.\n"

    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = "\n"
        s += banner_line
        s += console.bold_white + "Blackboard".center(79) + "\n" + console.reset
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += banner_line
    else:
        s = content
    return s


def epilog():
    if py_trees.console.has_colours:
        return console.cyan + "And his noodly appendage reached forth to tickle the blessed...\n" + console.reset
    else:
        return None


def command_line_argument_parser():
    parser = argparse.ArgumentParser(description=description(),
                                     epilog=epilog(),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     )
    render_group = parser.add_mutually_exclusive_group()
    render_group.add_argument('-r', '--render', action='store_true', help='render dot tree to file')
    render_group.add_argument(
        '--render-with-blackboard-variables',
        action='store_true',
        help='render dot tree to file with blackboard variables'
    )
    return parser


####################
# JSON
####################


def load_schema(schema_path):
    # read file
    with open(schema_path, 'r') as myfile:
        data = myfile.read()

    # parse file
    node_schema = json.loads(data)

    return node_schema


class BlackboardWriter(py_trees.behaviour.Behaviour):
    """
    Custom writer that submits a more complicated variable to the blackboard.
    """

    def __init__(self, name="Writer"):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="parameters/emphasis", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="parameters/distance_to_object", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="parameters/alpha", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="parameters/beta", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="parameters/rmin", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="parameters/rmax", access=py_trees.common.Access.WRITE)

        self.logger.debug("%s.__init__()" % (self.__class__.__name__))
        # initialize emphasis variables
        self.blackboard.set("parameters/distance_to_object", 1.0)
        self.blackboard.set("parameters/emphasis", 1.0)
        self.blackboard.set("parameters/alpha", 1)
        self.blackboard.set("parameters/beta", 0)
        self.blackboard.set("parameters/rmin", 0.001)
        self.blackboard.set("parameters/rmax", 10)

    def update(self):
        """
        Write a dictionary to the blackboard and return :data:`~py_trees.common.Status.SUCCESS`.
        """
        self.logger.debug("%s.update()" % (self.__class__.__name__))
        # self.blackboard.parameters = {"distance_to_object": 1.0, "alpha": 1, "beta":0}
        try:
            # self.blackboard.set("parameters", {"distance_to_object": 1.0, "alpha": 1, "beta": 0}, overwrite=False)
            json_schema: object = load_schema('/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees'
                                              '/py_trees/schemas/emphasis.json')

            # load emphasis variables from schema

            distance_read_from_json = json_schema['parameters']['distance_to_object']
            alpha = json_schema['parameters']['alpha']
            beta = json_schema['parameters']['beta']
            rmin = json_schema['parameters']['rmin']
            rmax = json_schema['parameters']['rmax']

            self.blackboard.set("parameters/distance_to_object", distance_read_from_json)
            self.blackboard.set("parameters/alpha", alpha)
            self.blackboard.set("parameters/beta", beta)
            self.blackboard.set("parameters/rmin", rmin)
            self.blackboard.set("parameters/rmax", rmax)


        except AttributeError:
            pass
        return py_trees.common.Status.SUCCESS


class ParamsAndState(py_trees.behaviour.Behaviour):
    """
    A more esotoric use of multiple blackboards in a behaviour to represent
    storage of parameters and state.
    """

    def __init__(self, name="ParamsAndState"):
        super().__init__(name=name)
        # namespaces can include the separator or may leave it out
        # they can also be nested, e.g. /agent/state, /agent/parameters

        self.state = self.attach_blackboard_client("State", "state")
        self.parameters = self.attach_blackboard_client("Params", "parameters")

        self.parameters.register_key(
            key="distance_to_object",
            access=py_trees.common.Access.READ
        )
        self.parameters.register_key(
            key="beta",
            access=py_trees.common.Access.READ
        )
        self.parameters.register_key(
            key="alpha",
            access=py_trees.common.Access.READ
        )
        self.parameters.register_key(
            key="rmin",
            access=py_trees.common.Access.READ
        )
        self.parameters.register_key(
            key="rmax",
            access=py_trees.common.Access.READ
        )
        self.state.register_key(
            key="emphasis",
            access=py_trees.common.Access.WRITE
        )

    def initialise(self):
        try:
            if self.parameters.rmin < self.parameters.distance_to_object < self.parameters.rmax:
                self.state.emphasis = self.parameters.alpha * self.parameters.distance_to_object + self.parameters.beta
            if self.parameters.distance_to_object < self.parameters.rmin:
                self.state.emphasis = 0
            if self.parameters.distance_to_object > self.parameters.rmax:
                self.state.emphasis = 1.0

        except KeyError as e:
            raise RuntimeError("parameter 'distance_to_object' not found [{}]".format(str(e)))

    def update(self):
        # if self.state.emphasis between rmin and rmax
        if 0.001 < self.state.emphasis < 1.5:
            return py_trees.common.Status.SUCCESS
        else:
            self.state.emphasis = self.parameters.distance_to_object
            return py_trees.common.Status.RUNNING


def create_root():
    root = py_trees.composites.Sequence("Attentional Mechanism")
    write_blackboard_variable = BlackboardWriter(name="Writer")
    params_and_state = ParamsAndState()
    root.add_children([
        # set_blackboard_variable,
        write_blackboard_variable,
        # check_blackboard_variable,
        params_and_state
    ])
    return root


##############################################################################
# Main
##############################################################################


def main():
    """
    Entry point for the demo script.
    """
    args = command_line_argument_parser().parse_args()
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    py_trees.blackboard.Blackboard.enable_activity_stream(maximum_size=100)

    root = create_root()

    ####################
    # Rendering
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root, with_blackboard_variables=False)
        sys.exit()
    if args.render_with_blackboard_variables:
        py_trees.display.render_dot_tree(root, with_blackboard_variables=True)
        sys.exit()

    ####################
    # Execute
    ####################
    root.setup_with_descendants()
    unset_blackboard = py_trees.blackboard.Client(name="Unsetter")
    unset_blackboard.register_key(key="parameters", access=py_trees.common.Access.WRITE)
    print("\n--------- Tick 0 ---------\n")
    root.tick_once()
    print("\n")
    print(py_trees.display.unicode_tree(root, show_status=True))
    print("--------------------------\n")
    print(py_trees.display.unicode_blackboard())
    print("--------------------------\n")
    print(py_trees.display.unicode_blackboard(display_only_key_metadata=True))
    print("--------------------------\n")
    unset_blackboard.unset("parameters")
    print(py_trees.display.unicode_blackboard_activity_stream())
