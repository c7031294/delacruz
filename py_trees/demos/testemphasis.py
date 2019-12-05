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
   :module: py_trees.demos.pick_up_where_you_left_off
   :func: command_line_argument_parser
   :prog: py-trees-demo-pick-up-where-you-left-off

.. graphviz:: dot/pick_up_where_you_left_off.dot

.. image:: images/pick_up_where_you_left_off.gif
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

    json_schema: object = load_schema('/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees/py_trees/schemas/pickandplace_schema_v3.json')

    ####################
    # TREE EXPANSION
    ####################

    # -len(some_list) gives you the first element of a list. end of schema will be reached when schema list yields an
    # index -1
    tree_layer = -len(json_schema)

    # create root
    root = create_root_from_schema(schema=json_schema, layer=tree_layer)

    # expand subtrees
    #while tree_layer < -1:
    #root_subtree = create_root_from_schema(schema=json_schema, layer=(tree_layer+1))
    #subtree = expand_subtrees(schema=json_schema, tree_layer=(tree_layer+1), root=root_subtree)
    # add subtree to root
    #root.add_child(subtree)
    # update tree layer
    #tree_layer += 1

    idiom_tree = py_trees.idioms.task_planner(
        name="Task Planner demo",
        schema=json_schema
    )

    root.add_children(idiom_tree)


    ####################
    # Rendering
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root)
        sys.exit()

    ####################
    # Tree Stewardship
    ####################

    behaviour_tree = py_trees.trees.BehaviourTree(root=root)
    print(behaviour_tree)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(functools.partial(post_tick_handler, snapshot_visitor))
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)

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
