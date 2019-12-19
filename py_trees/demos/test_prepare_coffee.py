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
# HELP FUNCTIONS
##############################################################################


def compare_objects(emphasis_object1, emphasis_object2):
    if emphasis_object1.emphasis > emphasis_object2.emphasis:
        return True
    else:
        return False


# array is an array of emphasis objects!
def partition(array, start, end, compare_objects):
    pivot = array[start]

    low = start + 1
    high = end

    while True:
        lambda x, y: x.emphasis < y.emphasis
        while low <= high and compare_objects(array[high], pivot):
            high = high - 1

        while low <= high and not compare_objects(array[low], pivot):
            low = low + 1

        if low <= high:
            array[low], array[high] = array[high], array[low]
        else:
            break

    array[start], array[high] = array[high], array[start]

    return high


def quick_sort(array, start, end, compare_objects):
    if start >= end:
        return

    p = partition(array, start, end, compare_objects)
    quick_sort(array, start, p - 1, compare_objects)
    quick_sort(array, p + 1, end, compare_objects)


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
    Sets post-condition to blackboard
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
        self.blackboard.register_key(key="/parameters/emphasis_list", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="/parameters/object", access=py_trees.common.Access.WRITE)

        json_schema: object = load_schema('/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees'
                                          '/py_trees/schemas/emphasis.json')

        # Initialize emphasis_list
        emphasis_list_from_json = json_schema['parameters']['emphasis_list']
        self.blackboard.set("/parameters/emphasis_list", emphasis_list_from_json)
        # Initialize current object in state scene
        object_scene_json = json_schema['parameters']['object']
        self.blackboard.set("/parameters/object", object_scene_json)

        self.logger.debug("%s.__init__()" % (self.__class__.__name__))


    def update(self):
        """
        Write a dictionary to the blackboard and return :data:`~py_trees.common.Status.SUCCESS`.
        """
        self.logger.debug("%s.update()" % (self.__class__.__name__))
        try:
            json_schema: object = load_schema('/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees'
                                              '/py_trees/schemas/emphasis.json')
            # Assume for now that the emphasis is already set. Writer just passes the emphasis list of objects
            # to the blackboard

            emphasis_list_from_json = json_schema['parameters']['emphasis_list']
            distance_read_from_json = json_schema['parameters']['distance_to_object']
            alpha = json_schema['parameters']['alpha']
            beta = json_schema['parameters']['beta']
            rmin = json_schema['parameters']['rmin']
            rmax = json_schema['parameters']['rmax']
            object_task = json_schema['parameters']['object']
            emphasis: float = 0.01

            if rmin < distance_read_from_json < rmax:
                emphasis = alpha * distance_read_from_json + beta
            if distance_read_from_json < rmin:
                emphasis = 0
            if distance_read_from_json > rmax:
                emphasis = 1.0

            # Update emphasis list in blackboard
            emphasis_key = "emphasis_" + object_task
            emphasis_list_from_json[emphasis_key] = emphasis

            self.blackboard.set("/parameters/emphasis_list", emphasis_list_from_json)
            self.blackboard.set("/parameters/object", object_task)

        except AttributeError:
            pass
        return py_trees.common.Status.SUCCESS


class Emphasis:
    def __init__(self, object, emphasis):
        self.object = object
        self.emphasis = emphasis

    def __str__(self):
        return self.emphasis


class SetEmphasis(py_trees.behaviour.Behaviour):
    """
    set emphasis value in the blackboard and update emphasis list
    """

    def __init__(self, name="SetEmphasizedObject"):
        super().__init__(name=name)

        self.parameters = self.attach_blackboard_client("SetEmphasizedObject", "parameters")
        self.parameters.register_key(
            key="emphasis_list",
            access=py_trees.common.Access.READ)
        self.parameters.register_key(
            key="emphasized_value",
            access=py_trees.common.Access.WRITE)
        self.parameters.register_key(
            key="emphasized_object",
            access=py_trees.common.Access.WRITE
        )

    def initialise(self):
        try:
            pass
        except KeyError as e:
            raise RuntimeError("Could not initialise emphasis variable [{}]".format(str(e)))

    def update(self):

        '''
        Read the emphasis list from blackboard and set the highest emphasis
        Highest emphasis value will be mapped with the object and set in the blackboard
        emphasis and object variables will be then used to expand the tree

        The highest emphasis is set applying QuickSort algorithm
        '''

        # Define set of emphasis objects based on blackboard values

        emphasis_list = self.parameters.emphasis_list
        emphasis_items = len(emphasis_list.items())
        emphasis_objects = [None] * emphasis_items
        index_array = 0

        # Create array of emphasis objects
        for each_object in emphasis_list:
            emphasis_object = Emphasis(object=each_object, emphasis=emphasis_list[str(each_object)])
            emphasis_objects[index_array] = emphasis_object
            index_array += 1

        # Sort emphasis values from min to max
        quick_sort(emphasis_objects, 0, emphasis_items - 1, lambda x, y: x.emphasis < y.emphasis)

        # Set highest emphasis and object to blackboard
        self.parameters.set("emphasized_value", emphasis_objects[emphasis_items - 1].emphasis)

        # Retrieve object from key "emphasis_object"
        start = emphasis_objects[emphasis_items - 1].object.find('_') + 1
        object_string = emphasis_objects[emphasis_items - 1].object[start:]

        # Set object to blackboard
        self.parameters.set("emphasized_object", object_string)

        # Update emphasis list
        quick_sort(emphasis_objects, 2, emphasis_items - 1, lambda x, y: x.emphasis < y.emphasis)

        return py_trees.common.Status.SUCCESS



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


def create_behavior_tree(json_schema):
    # pdb.set_trace()
    root = py_trees.composites.Parallel("Prepare Coffee")
    # Set sequence node to avoid parallel access. ToDo: guards
    emphasis_root = py_trees.composites.Sequence("Check Emphasis")
    # emphasis_root = py_trees.composites.Parallel("Check Emphasis")
    write_blackboard_variable = BlackboardWriter(name="Writer")
    set_emphasized_object = SetEmphasis()
    emphasis_root.add_children([
        write_blackboard_variable,
        set_emphasized_object
    ])
    root.add_child(emphasis_root)

    ####################
    # TREE EXPANSION
    ####################

    # Read which object has highest emphasis from blackboard
    # pdb.set_trace()
    blackboard = py_trees.blackboard.Client(name="Read Emphasized Object for Tree Expansion")
    print(blackboard)
    blackboard.register_key(key="/parameters/object", access=py_trees.common.Access.READ)
    emphasized_object = blackboard.parameters.object
    prepare_coffee_root = py_trees.idioms.emphasized_tree(
        name="Emphasized Tree",
        object=emphasized_object,
        schema=json_schema
    )

    root.add_child(prepare_coffee_root)

    behaviour_tree = py_trees.trees.BehaviourTree(root=root)
    print(behaviour_tree)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.visitors.append(py_trees.visitors.DisplaySnapshotVisitor(display_blackboard=True))
    behaviour_tree.add_post_tick_handler(functools.partial(post_tick_handler, snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)

    return behaviour_tree


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

    ####################
    # Rendering
    ####################
    if args.render:
        behaviour_tree = create_behavior_tree(json_schema)
        py_trees.display.render_dot_tree(behaviour_tree, with_blackboard_variables=True)
        sys.exit()

    ####################
    # Tick Tock
    ####################
    if args.interactive:
        py_trees.console.read_single_keypress()
    # create and execute tree until all post-conditions are achieved
    #for unused_i in range(1, 11):
    while True:
        try:
            behaviour_tree = create_behavior_tree(json_schema)
            behaviour_tree.tick()

            if args.interactive:
                py_trees.console.read_single_keypress()
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")
