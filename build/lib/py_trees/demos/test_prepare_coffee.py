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

CONTINUOUS_TICK_TOCK = -1
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


def initialise_postcondition_list(schema):
    '''
    Loads from json string the list of postconditions and intialize them into the blackboard
    :return: Success always
    '''
    try:
        layers_schema = -len(schema)
        # Create a set of Postcondition dictionary with possible values True/False
        postcondition_dict = dict()
        while layers_schema <= -1:
            task_parameters = schema[layers_schema]['parameters']
            postcondition = task_parameters[0]
            # initalize all postconditions to false
            postcondition_dict[postcondition] = False
            layers_schema += 1

        parameters = py_trees.blackboard.Client()
        print(parameters)
        # Set postcondition list to blackboard
        parameters.register_key(key="/parameters/postcondition_list", access=py_trees.common.Access.WRITE)
        parameters.set("/parameters/postcondition_list", postcondition_dict)
    except KeyError as e:
        raise RuntimeError("Could not set postcondition list in the blackboard [{}]".format(str(e)))


def pre_tick_handler(behaviour_tree, schema):
    """
    This prints a banner and will run immediately before every tick of the tree.

    Args:
        behaviour_tree (:class:`~py_trees.trees.BehaviourTree`): the tree custodian

    """
    '''
   If postcondition list not yet set in the blackboard, it loads from json string the list of postconditions 
   and intialize them into the blackboard
   '''
    try:
        pass
    except KeyError as e:
        raise RuntimeError("Could not set postcondition list in the blackboard [{}]".format(str(e)))


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
    This calculates and updates in the the emphasis list of each object in the blackboard based on emphasis.json file
    emphasis.json is dynamic and gives us info about the current bottom-up parameters
    update operation is performed in the following blackboard variables:
    emphasis_list - takes the bottom-up variables rmin, rmax, alpha, beta, distance_to_object
                    needed from emphasis.json file
    object - current active object
    #(postcondition list from blackboard based on) not used?
    """

    def __init__(self, name="Writer"):
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="/parameters/emphasis_list", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="/parameters/object", access=py_trees.common.Access.WRITE)
        self.blackboard.register_key(key="/parameters/postcondition", access=py_trees.common.Access.WRITE)
        emphasis_list_json_schema: object = load_schema('/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees'
                                          '/py_trees/schemas/emphasis.json')

        # Initialize emphasis_list
        self.blackboard.set("/parameters/emphasis_list", emphasis_list_json_schema)
        # Initialize current object in state scene
        object_scene_json = emphasis_list_json_schema['parameters']['object']

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

            emphasis_list_from_json = json_schema['parameters']['emphasis_list']
            distance_read_from_json = json_schema['parameters']['distance_to_object']
            alpha = json_schema['parameters']['alpha']
            beta = json_schema['parameters']['beta']
            rmin = json_schema['parameters']['rmin']
            rmax = json_schema['parameters']['rmax']
            object_task = json_schema['parameters']['object']
            #emphasis: float = 0.01

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

def create_attentional_tree():
    root = py_trees.composites.Sequence("Attentional Trees Root")
    ############################################
    # Emphasized Subtree
    ############################################

    # 2. Write emphasis paramaters into blackboard and Set highest emphasis according to bottom-up regulations

    set_emphasized_behavior = py_trees.behaviours.SetEmphasis()

    # Add Set Emphasis Subtree
    root = py_trees.composites.Selector("Attentional Subtree")

    changed_emphasis_behavior = py_trees.behaviours.CheckBlackboardVariableValue(name="Changed Emphasis?",
                                                                                 variable_name="/parameters/changed_emphasis_flag",
                                                                                 expected_value=True)

    root.add_children([changed_emphasis_behavior, set_emphasized_behavior])

    return root


def create_behavior_tree(json_schema):

    root = py_trees.composites.Sequence("Attentional Trees Root")
    # 1. Initialise Postcondition List in the blackboard
    initialise_prepostcondition_lists_root = py_trees.composites.Sequence("Initialise Blackboard Subtree")
    post_condition_selector = py_trees.composites.Selector("Initialise Postcondition List in Blackboard")
    pre_condition_selector = py_trees.composites.Selector("Initialise PreCondition List in Blackboard")
    check_initialised_precondition_list = py_trees.behaviours.CheckBlackboardVariableExists("/parameters/precondition_list")
    check_initialised_postcondition_list = py_trees.behaviours.CheckBlackboardVariableExists("/parameters/postcondition_list")
    initialise_precondition_list = py_trees.behaviours.PrePostConditions(pre=True, post=False, schema=json_schema)
    initialise_postcondition_list = py_trees.behaviours.PrePostConditions(pre=False, post=True, schema=json_schema)

    ############################################
    # Initialise Pre and Post Conditions Subtree
    ############################################
    pre_condition_selector.add_children([
        check_initialised_precondition_list,
        initialise_precondition_list
    ])
    post_condition_selector.add_children([
        check_initialised_postcondition_list,
        initialise_postcondition_list
    ])

    initialise_prepostcondition_lists_root.add_children([
        pre_condition_selector,
        post_condition_selector
    ])

    ############################################
    # Emphasized Subtree
    ############################################

    # 2. Write emphasis paramaters into blackboard and Set highest emphasis according to bottom-up regulations

    set_emphasized_behavior = py_trees.behaviours.SetEmphasis()

    # Add Set Emphasis Subtree
    attentional_root_selector = py_trees.composites.Selector("Attentional Subtree")

    changed_emphasis_behavior = py_trees.behaviours.CheckBlackboardVariableValue(name="Changed Emphasis?",
                                                                                 variable_name="/parameters/changed_emphasis_flag",
                                                                                 expected_value=True)

    set_emphasis_subtree_sequence = py_trees.composites.Sequence("Set and Update Emphasis")
    set_emphasis_subtree_sequence.add_child(set_emphasized_behavior)

    check_goal_selector = py_trees.behaviours.CheckGoal()

    # Read Emphasized Object for Tree Expansion
    blackboard = py_trees.blackboard.Client(name="Read Emphasized Object for Tree Expansion")
    blackboard.register_key(key="/parameters/object", access=py_trees.common.Access.READ)
    emphasized_object = blackboard.parameters.object
    # Create Task Execution Subtree based on bottom-up regulations and PA-BT Approach
    prepare_coffee_root = py_trees.idioms.emphasized_tree(
        name="Prepare Coffee Subtree Expand",
        object=emphasized_object,
        schema=json_schema
    )
    ###########################
    # Retrieve & Expand Subtree
    ###########################
    retrieve_and_expand_root_parallel = py_trees.composites.Parallel("Executional Subtree")
    retrieve_and_expand_subtree_sequence = py_trees.composites.Sequence("Retrieve & Expand Emphasized Subtree")
    expand_subtree_sequence = py_trees.composites.Sequence("Expand Subtree")
    create_subtree_sequence = py_trees.composites.Sequence("Create Subtree")
    expand_subtree_sequence.add_child(prepare_coffee_root)
    create_subtree_sequence.add_child(prepare_coffee_root)
    retrieve_subtree_selector = py_trees.composites.Selector("Retrieve Subtree")

    # Retrieve Subtree
    retrieve_subtree_selector.add_children([
        changed_emphasis_behavior,
        expand_subtree_sequence
    ])
    # Expand Subtree
    #retrieve_and_expand_subtree_sequence.add_child(retrieve_subtree_selector)
    retrieve_and_expand_subtree_sequence.add_children([
        retrieve_subtree_selector,
        prepare_coffee_root
    ])
    retrieve_and_expand_root_parallel.add_children([
        set_emphasized_behavior,
        retrieve_and_expand_subtree_sequence
    ])
    attentional_root_selector.add_children([
        check_goal_selector,
        retrieve_and_expand_root_parallel
    ])
    #end_tree = py_trees.composites.Sequence("End")
    end_behavior = py_trees.behaviours.Count(name="End", fail_until=0, running_until=1, success_until=1, reset=False)
    #end_tree.add_child(end_behavior)
    #end = root.stop()

    root.add_children([
        initialise_prepostcondition_lists_root,
        #attentional_root_selector,
        end_behavior
    ])
    behaviour_tree = py_trees.trees.BehaviourTree(root=root)
    print(root)
    py_trees.display.render_dot_tree(root)
    #behaviour_tree.add_pre_tick_handler(pre_tick_handler(schema=json_schema))
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
    # Tick Tock
    ####################

    #print(behaviour_tree)

    if args.interactive:
        behaviour_tree = create_behavior_tree(json_schema)
        py_trees.console.read_single_keypress()
    # create and execute tree until all post-conditions are achieved
    #for unused_i in range(1, 4):
        #behaviour_tree = create_behavior_tree(json_schema)

    behaviour_tree = create_behavior_tree(json_schema)
    #attentional_tree = create_attentional_tree()
    period_bt_retrieve_and_expand_ms = 100
    period_check_emphasis_ms = 50
    while True:
        try:
            pdb.set_trace()
            behaviour_tree.tick_tock(period_bt_retrieve_and_expand_ms, number_of_iterations=CONTINUOUS_TICK_TOCK,
                                     pre_tick_handler=None,
                                     post_tick_handler=None)
            #attentional_tree.tick_tock(period_check_emphasis_ms,number_of_iterations=CONTINUOUS_TICK_TOCK,
             #                        pre_tick_handler=None,
              #                       post_tick_handler=None)

            #behaviour_tree.tick()
            if args.interactive:
                py_trees.console.read_single_keypress()
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")

    ####################
    # Rendering
    ####################
    if args.render:
        #pdb.set_trace()
        behaviour_tree = create_behavior_tree(json_schema)
        #py_trees.display.render_dot_tree(py_trees.behaviour.Behaviour(), name="Prepare Coffee", with_blackboard_variables=True)
        #py_trees.display.render_dot_tree(root)
        sys.exit()
