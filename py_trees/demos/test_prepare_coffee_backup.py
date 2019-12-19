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
   :module: py_trees.demos.test_automated_planning
   :func: command_line_argument_parser
   :prog: py-trees-demo-automated-planning

.. graphviz:: dot/task_planner_demo.dot

.. image:: images/task_planner_demo.gif
"""

##############################################################################
# Imports
##############################################################################

import argparse
import functools
from typing import List, Any

import py_trees
import sys
import time
import json
import pdb

import py_trees.console as console


##############################################################################
# JSON
##############################################################################


def load_schema(schema_path):
    # read file
    with open(schema_path, 'r') as myfile:
        data = myfile.read()

    # parse file
    node_schema = json.loads(data)

    return node_schema


##############################################################################
# Classes
##############################################################################


def description(root):
    content = "A demonstration of the 'pick up where you left off' idiom.\n\n"
    content += "A common behaviour tree pattern that allows you to resume\n"
    content += "work after being interrupted by a high priority interrupt.\n"
    content += "\n"
    content += "EVENTS\n"
    content += "\n"
    content += " -  2 : task one done, task two running\n"
    content += " -  3 : high priority interrupt\n"
    content += " -  7 : task two restarts\n"
    content += " -  9 : task two done\n"
    content += "\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = "\n"
        s += banner_line
        s += console.bold_white + "Trees".center(79) + "\n" + console.reset
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
    parser = argparse.ArgumentParser(description=description(create_root()),
                                     epilog=epilog(),
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     )
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-r', '--render', action='store_true', help='render dot tree to file')
    group.add_argument('-i', '--interactive', action='store_true', help='pause and wait for keypress at each tick')
    return parser


def pre_tick_handler(behaviour_tree):
    """
    This prints a banner and will run immediately before every tick of the tree.

    Args:
        behaviour_tree (:class:`~py_trees.trees.BehaviourTree`): the tree custodian

    """
    print("\n--------- Run %s ---------\n" % behaviour_tree.count)


def post_tick_handler(snapshot_visitor, behaviour_tree):
    """
    Prints an ascii tree with the current snapshot status.
    """
    print(
        "\n" + py_trees.display.unicode_tree(
            root=behaviour_tree.root,
            visited=snapshot_visitor.visited,
            previously_visited=snapshot_visitor.previously_visited
        )
    )


class BlackboardWriter(py_trees.behaviour.Behaviour):
    """
    Custom writer that submits a more complicated variable to the blackboard.
    """

    def __init__(self, name="Writer"):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client()
        #self.blackboard.register_key(key="parameters/emphasis", access=py_trees.common.Access.WRITE)
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
            object_task = json_schema['parameters']['object']

            self.blackboard.set("parameters/object", object_task)
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

        self.state = self.attach_blackboard_client("EmphasisList", "emphasis_list")
        self.parameters = self.attach_blackboard_client("Params", "parameters")
        self.parameters.register_key(
            key="parameters/emphasis_list/emphasis",
            access=py_trees.common.Access.WRITE)
        self.parameters.register_key(
            key="object",
            access=py_trees.common.Access.READ
        )
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
        #should not be called emphasis_object?
        self.state.register_key(
            key="emphasis_list",
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
        if self.parameters.rmin < self.state.emphasis < self.parameters.rmax:
            return py_trees.common.Status.SUCCESS
        else:
            self.state.emphasis = self.parameters.distance_to_object
            return py_trees.common.Status.RUNNING



def create_root_from_schema(schema, layer):
    root_json = schema[layer]['name']
    if ('sequence' in root_json):
        root = py_trees.composites.Sequence(root_json)
        return root
    if ('selector' in root_json):
        root = py_trees.composites.Selector(root_json)
        return root
    if ('parallel' in root_json):
        root = py_trees.composites.Parallel(root_json)
        return root


def create_root():
    root = list()
    return root


def expand_subtrees(schema, root, tree_layer):
    # retrieve children
    children_json = schema[tree_layer]['children']
    # add the childs to root of subtree
    for child in children_json:
        execution_node = py_trees.behaviours.Count(name=child,
                                                   fail_until=0,
                                                   running_until=1,
                                                   success_until=10)
        root.add_child(execution_node)

    return root


##############################################################################
# Main
##############################################################################

# Debugging: add pdb.set_trace() line for breakpoint

def main():
    """
        Entry point for the demo script.
        """
    args = command_line_argument_parser().parse_args()
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    ####################
    # JSON
    ####################

    json_schema: object = load_schema(
        '/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees/py_trees/schemas/prepare_coffee_emphasis.json')

    #############################
    # Tree Creation and Expansion
    #############################

    root = py_trees.composites.Parallel("Prepare Coffee")
    # Set sequence node to avoid parallel access. ToDo: guards
    emphasis_root = py_trees.composites.Sequence("Check Emphasis")
    # emphasis_root = py_trees.composites.Parallel("Check Emphasis")
    write_blackboard_variable = BlackboardWriter(name="Writer")
    params_and_state = ParamsAndState()
    emphasis_root.add_children([
        write_blackboard_variable,
        params_and_state
    ])
    root.add_child(emphasis_root)

    # expand subtrees
    tree_layer = -len(json_schema)

    # prepare_coffee_root = py_trees.composites.Selector("Prepare Coffee")
    '''
    prepare_coffee_root = create_root_from_schema(schema=json_schema, layer=tree_layer)
    while tree_layer < -1:
        root_subtree = create_root_from_schema(schema=json_schema, layer=(tree_layer+1))
        subtree = expand_subtrees(schema=json_schema, tree_layer=(tree_layer+1), root=root_subtree)
        # add subtree to root
        prepare_coffee_root.add_child(subtree)
        # update tree layer
        tree_layer += 1
    '''
    # create subtree prepare_coffee from task_planner idiom
    ####################
    # TREE EXPANSION
    ####################

    prepare_coffee_root = py_trees.idioms.task_planner(
        name="Prepare Coffee Task",
        schema=json_schema
    )

    root.add_child(prepare_coffee_root)

    #############################
    # Behavior Tree
    #############################

    behaviour_tree = py_trees.trees.BehaviourTree(root=root)
    print(behaviour_tree)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(functools.partial(post_tick_handler, snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)

    ####################
    # Rendering
    ####################
    # if args.render:
    #   py_trees.display.render_dot_tree(root)
    #  sys.exit()

    ####################
    # Rendering
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root, with_blackboard_variables=True)
        sys.exit()

    ####################
    # Tick Tock
    ####################
    if args.interactive:
        py_trees.console.read_single_keypress()
    for unused_i in range(1, 11):
        try:
            behaviour_tree.tick()
            if args.interactive:
                py_trees.console.read_single_keypress()
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")
