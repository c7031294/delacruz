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
from py_trees.behaviour import Behaviour


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


# Debugging
# pdb.set_trace()

def expand_tree(schema: list, root, tree_layer, children_layer, children_json):
    """

    :type tree_layer: int
    """
    # 2. add children to root
    #children_json = json_schema[tree_layer]['children']
    # add control nodes. Control nodes are of :class:`~py_trees.composites.Composite`
    pdb.set_trace()
    for child in children_json:
        children_layer += 1
        # pdb.set_trace()
        print("Child in json: ", child)
        print("tree layer: ", tree_layer)
        print("root: ", root)

        if "sequence" in child:
            new_child = py_trees.composites.Sequence(child)
            root.add_child(new_child)
            # update root

            root = new_child
            tree_layer += 1
            if tree_layer <= -1: return
            #expand_tree(schema, root, tree_layer, children_layer)
            else:
                return root

        if "selector" in child:
            new_child = py_trees.composites.Selector(child)
            root.add_child(new_child)
            # update root

            root = new_child
            tree_layer += 1
            print("children layer: ", children_layer)
            if tree_layer <= -1: return
            # expand_tree(schema, root, tree_layer, children_layer)
            else:
                return root
        if "parallel" in child:
            new_child = py_trees.composites.Parallel(child)
            root.add_child(new_child)
            # update root

            root = new_child
            tree_layer += 1
        # expand_tree(schema, root, tree_layer, children_layer)

        # 3. update level and keep on expanding

        execution_node = py_trees.behaviours.Count(name=child,
                                                   fail_until=0,
                                                   running_until=1,
                                                   success_until=10)
        #pdb.set_trace()
        root.add_child(execution_node)
        print("root: ", root)

        if children_layer >= len(children_json):
            print("going back. Tree layer: ", tree_layer+1)
            #children_layer = -len(schema[tree_layer + 1]['children'])
            children_layer=0
            #root = create_root_from_schema(schema)
            return root
            #expand_tree(schema, root, tree_layer+1, children_layer)




def create_root_from_schema(schema: object) -> object:
    root_json = schema[0]['name']
    if ('sequence' in root_json):
        root = py_trees.composites.Sequence(root_json)
    if ('selector' in root_json):
        root = py_trees.composites.Selector(root_json)
    if ('parallel' in root_json):
        root = py_trees.composites.Parallel(root_json)

    return root


def create_root():
    root = list()
    return root
    # read task execution order
    # schema = load_schema('/home/pilar/Documents/PhD/py_trees/py_trees/schemas/pickandplace_schema_v2.json', 'r')
    # print(schema)
    # children = list()

    # expand_tree(schema, root)


'''
    root = py_trees.composites.Selector("Selector")
    print(type(root))
    sequence01 = py_trees.composites.Sequence("Sequence")

    selector01 = py_trees.composites.Selector("Selector01")
    selector02 = py_trees.composites.Selector("Selector02")
    selector03 = py_trees.composites.Selector("Selector03")

    tree = py_trees.trees.BehaviourTree(root)
    tree.insert_subtree(child=sequence01, unique_id=root.id, index=0)
    tree.insert_subtree(child=selector01, unique_id=sequence01.id, index=1)
    tree.insert_subtree(child=selector02, unique_id=sequence01.id, index=2)
    tree.insert_subtree(child=selector03, unique_id=sequence01.id, index=3)

    # add sequence 01
    # sequence01= py_trees.composites.Sequence("Sequence")
    # root.add_child(sequence01)

    # add childrens to sequence 01

    # children_layer01 = list()
    # children_layer01.append("Selector01", "Selector02", "Selector03")

    # sequence01.add_children([selector01,selector02,selector03])
    # sequence01.insert_subtree(self, child, unique_id, index)
    # root.add_child(selector01)

    # adding subtree 1 to selector01
    for action in ["Action 1", "Action 2", "Action 3"]:
        success_after_two = py_trees.behaviours.Count(name=action,
                                                      fail_until=0,
                                                      running_until=1,
                                                      success_until=10)
        selector01.add_child(success_after_two)
    # add subtree 2
    for action in ["Action 4", "Action 5", "Action 6"]:
        success1_after_two = py_trees.behaviours.Count(name=action,
                                                       fail_until=0,
                                                       running_until=1,
                                                       success_until=10)
   
        selector02.add_child(success1_after_two)
   '''


##############################################################################
# Main
##############################################################################


def main():
    """
    Entry point for the demo script.
    """
    args = command_line_argument_parser().parse_args()
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    ####################
    # JSON
    ####################

    json_schema = load_schema('/home/pilar/Documents/PhD/py_trees/py_trees/schemas/pickandplace_schema_v3.json')

    ####################
    # TREE EXPANSION
    ####################

    # -len(some_list) gives you the first element of a list
    # end of schema will be reached when schema list yields an index -1
    tree_layer = -len(json_schema)
    #children_layer = len(json_schema[0]['children'])
    children_layer = 0
    # 2. expand tree
    root = py_trees.composites.Sequence(name="demo tree")

    # pdb.set_trace()
    while(tree_layer<=len(json_schema)):
        # 1. retrieve root
        #root = create_root_from_schema(json_schema, tree_layer)
        children_json = json_schema[tree_layer]['children']
        subtree = expand_tree(json_schema, root, tree_layer, children_layer, children_json)
        #root.add_child(expand_tree(json_schema, root, tree_layer, children_layer))
        tree_layer += 1
    # py_trees.display.ascii_tree(root)

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
