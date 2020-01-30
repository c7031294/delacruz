#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################
"""
A library of fundamental behaviours for use.
"""

##############################################################################
# Imports
##############################################################################

import operator
import typing
import pdb
import json
from . import behaviour
from . import common
from . import meta


##############################################################################
# JSON FUNCTIONS
##############################################################################

def load_schema(schema_path):
    # read file
    with open(schema_path, 'r') as myfile:
        data = myfile.read()

    # parse file
    node_schema = json.loads(data)

    return node_schema


##############################################################################
# Function Behaviours
##############################################################################


def success(self):
    self.logger.debug("%s.update()" % self.__class__.__name__)
    self.feedback_message = "success"
    return common.Status.SUCCESS


def failure(self):
    self.logger.debug("%s.update()" % self.__class__.__name__)
    self.feedback_message = "failure"
    return common.Status.FAILURE


def running(self):
    self.logger.debug("%s.update()" % self.__class__.__name__)
    self.feedback_message = "running"
    return common.Status.RUNNING


def dummy(self):
    self.logger.debug("%s.update()" % self.__class__.__name__)
    self.feedback_message = "crash test dummy"
    return common.Status.RUNNING


Success = meta.create_behaviour_from_function(success)
"""
Do nothing but tick over with :data:`~py_trees.common.Status.SUCCESS`.
"""

Failure = meta.create_behaviour_from_function(failure)
"""
Do nothing but tick over with :data:`~py_trees.common.Status.FAILURE`.
"""

Running = meta.create_behaviour_from_function(running)
"""
Do nothing but tick over with :data:`~py_trees.common.Status.RUNNING`.
"""

Dummy = meta.create_behaviour_from_function(dummy)
"""
Crash test dummy used for anything dangerous.
"""


##############################################################################
# Standalone Behaviours
##############################################################################


class Periodic(behaviour.Behaviour):
    """
    Simply periodically rotates it's status over the
    :data:`~py_trees.common.Status.RUNNING`, :data:`~py_trees.common.Status.SUCCESS`,
    :data:`~py_trees.common.Status.FAILURE` states.
    That is, :data:`~py_trees.common.Status.RUNNING` for N ticks,
    :data:`~py_trees.common.Status.SUCCESS` for N ticks,
    :data:`~py_trees.common.Status.FAILURE` for N ticks...

    Args:
        name (:obj:`str`): name of the behaviour
        n (:obj:`int`): period value (in ticks)

    .. note:: It does not reset the count when initialising.
    """

    def __init__(self, name, n):
        super(Periodic, self).__init__(name)
        self.count = 0
        self.period = n
        self.response = common.Status.RUNNING

    def update(self):
        self.count += 1
        if self.count > self.period:
            if self.response == common.Status.FAILURE:
                self.feedback_message = "flip to running"
                self.response = common.Status.RUNNING
            elif self.response == common.Status.RUNNING:
                self.feedback_message = "flip to success"
                self.response = common.Status.SUCCESS
            else:
                self.feedback_message = "flip to failure"
                self.response = common.Status.FAILURE
            self.count = 0
        else:
            self.feedback_message = "constant"
        return self.response


class SuccessEveryN(behaviour.Behaviour):
    """
    This behaviour updates it's status with :data:`~py_trees.common.Status.SUCCESS`
    once every N ticks, :data:`~py_trees.common.Status.FAILURE` otherwise.

    Args:
        name (:obj:`str`): name of the behaviour
        n (:obj:`int`): trigger success on every n'th tick

    .. tip::
       Use with decorators to change the status value as desired, e.g.
       :meth:`py_trees.decorators.FailureIsRunning`
    """

    def __init__(self, name, n):
        super(SuccessEveryN, self).__init__(name)
        self.count = 0
        self.every_n = n

    def update(self):
        self.count += 1
        self.logger.debug("%s.update()][%s]" % (self.__class__.__name__, self.count))
        if self.count % self.every_n == 0:
            self.feedback_message = "now"
            return common.Status.SUCCESS
        else:
            self.feedback_message = "not yet"
            return common.Status.FAILURE


class Count(behaviour.Behaviour):
    """
    A counting behaviour that updates its status at each tick depending on
    the value of the counter. The status will move through the states in order -
    :data:`~py_trees.common.Status.FAILURE`, :data:`~py_trees.common.Status.RUNNING`,
    :data:`~py_trees.common.Status.SUCCESS`.

    This behaviour is useful for simple testing and demo scenarios.

    Args:
        name (:obj:`str`): name of the behaviour
        fail_until (:obj:`int`): set status to :data:`~py_trees.common.Status.FAILURE` until the counter reaches this value
        running_until (:obj:`int`): set status to :data:`~py_trees.common.Status.RUNNING` until the counter reaches this value
        success_until (:obj:`int`): set status to :data:`~py_trees.common.Status.SUCCESS` until the counter reaches this value
        reset (:obj:`bool`): whenever invalidated (usually by a sequence reinitialising, or higher priority interrupting)

    Attributes:
        count (:obj:`int`): a simple counter which increments every tick
    """

    def __init__(self, name="Count", fail_until=3, running_until=5, success_until=6, reset=True):
        super(Count, self).__init__(name)
        self.count = 0
        self.fail_until = fail_until
        self.running_until = running_until
        self.success_until = success_until
        self.number_count_resets = 0
        self.number_updated = 0
        self.reset = reset

    def terminate(self, new_status):
        self.logger.debug("%s.terminate(%s->%s)" % (self.__class__.__name__, self.status, new_status))
        # reset only if udpate got us into an invalid state
        if new_status == common.Status.INVALID and self.reset:
            self.count = 0
            self.number_count_resets += 1
        self.feedback_message = ""

    def update(self):
        self.number_updated += 1
        self.count += 1
        if self.count <= self.fail_until:
            self.logger.debug("%s.update()[%s: failure]" % (self.__class__.__name__, self.count))
            self.feedback_message = "failing"
            return common.Status.FAILURE
        elif self.count <= self.running_until:
            self.logger.debug("%s.update()[%s: running]" % (self.__class__.__name__, self.count))
            self.feedback_message = "running"
            return common.Status.RUNNING
        elif self.count <= self.success_until:
            self.logger.debug("%s.update()[%s: success]" % (self.__class__.__name__, self.count))
            self.feedback_message = "success"
            return common.Status.SUCCESS
        else:
            self.logger.debug("%s.update()[%s: failure]" % (self.__class__.__name__, self.count))
            self.feedback_message = "failing forever more"
            return common.Status.FAILURE

    def __repr__(self):
        """
        Simple string representation of the object.

        Returns:
            :obj:`str`: string representation
        """
        s = "%s\n" % self.name
        s += "  Status : %s\n" % self.status
        s += "  Count  : %s\n" % self.count
        s += "  Resets : %s\n" % self.number_count_resets
        s += "  Updates: %s\n" % self.number_updated
        return s


##############################################################################
# Attentional Mechanism Behaviours
##############################################################################

##############################################################################
# HELP FUNCTIONS used for Attentional Mechanism Behaviours
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


class Emphasis:
    def __init__(self, object, emphasis):
        self.object = object
        self.emphasis = emphasis

    def __str__(self):
        return self.emphasis


class PostCondition:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __str__(self):
        return self.value


class SetEmphasis(behaviour.Behaviour):
    """
    This performs two things:
    Reads from json the emphasis parameters and writes them to the blackboard
    Sorts highest emphasis value based on the emphasis list from the blackboard
    (This emphasis list is set in BlackBoardWriter class too, now it has been merged)
    """

    def __init__(self, name="SetEmphasizedObject"):
        '''
        Reads from json the emphasis parameters and writes them to the blackboard
        :param name:
        '''
        super().__init__(name=name)
        self.parameters = self.attach_blackboard_client("SetEmphasizedObject", "parameters")
        self.parameters.register_key(
            key="emphasis_list",
            access=common.Access.WRITE)
        self.parameters.register_key(
            key="emphasized_value",
            access=common.Access.WRITE)
        self.parameters.register_key(
            key="emphasized_object",
            access=common.Access.WRITE
        )
        self.parameters.register_key(
            key="changed_emphasis_flag",
            access=common.Access.WRITE)
        self.parameters.register_key(
            key="object",
            access=common.Access.WRITE
        )
        json_schema: object = load_schema('/home/pilar/Documents/PhD/git-delacruz/delacruz/py_attentional_trees'
                                          '/py_trees/schemas/emphasis.json')
        emphasis_list_from_json = json_schema['parameters']['emphasis_list']
        distance_read_from_json = json_schema['parameters']['distance_to_object']
        alpha = json_schema['parameters']['alpha']
        beta = json_schema['parameters']['beta']
        rmin = json_schema['parameters']['rmin']
        rmax = json_schema['parameters']['rmax']
        object_task = json_schema['parameters']['object']
        if rmin < distance_read_from_json < rmax:
            emphasis = alpha * distance_read_from_json + beta
        if distance_read_from_json < rmin:
            emphasis = 0
        if distance_read_from_json > rmax:
            emphasis = 1.0

        # Update emphasis list in the blackboard. Store old value for flag use.
        emphasis_key = "emphasis_" + object_task
        old_emphasis = emphasis_list_from_json[emphasis_key]
        emphasis_list_from_json[emphasis_key] = emphasis
        # This flag will be checked before expanding PA-BT subtree. New tree will be created
        # only if changed_emphasis_flag is True
        pdb.set_trace()
        if old_emphasis != emphasis:
            self.parameters.set("changed_emphasis_flag", True)
        else:
            self.parameters.set("changed_emphasis_flag", False)
        self.parameters.set("emphasis_list", emphasis_list_from_json)
        self.parameters.set("object", object_task)

    def initialise(self):
        '''
        Reads from json the emphasis parameters and writes them to the blackboard
        :param json_schema:
        :return:
        '''

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
        # Write ChangedEmphasis Flag in blackboard

        return common.Status.SUCCESS

    def __repr__(self):
        """
        Simple string representation of the object.

        Returns:
            :obj:`str`: string representation
        """
        s = "%s\n" % self.name
        s += "  Status : %s\n" % self.status
        return s


class PreConditions(behaviour.Behaviour):
    """
    Set of Functions concerning Preconditions handling.
    This method will be deprecated through PrePostConditions
    """

    def __init__(self, schema, name="PreConditions", ):
        super().__init__(name=name)
        try:
            # Load from json string set of preconditions
            # Create a set of Postcondition objects
            layers_schema = -len(schema)
            # Create a set of Postcondition dictionary with possible values True/False
            precondition_dict = dict()
            while layers_schema <= -1:
                task_parameters = schema[layers_schema]['parameters']
                precondition = task_parameters["precondition"]
                # initalize all postconditions to false
                precondition_dict[precondition] = False
                layers_schema += 1

                parameters = behaviour.blackboard.Client()
                # Set postcondition list to blackboard
                "precondition"
                parameters.register_key(key="/parameters/precondition_list", access=common.Access.WRITE)
                parameters.set("/parameters/postcondition_list", precondition_dict)
            print(parameters)

        except KeyError as e:
            raise RuntimeError("Could not set postcondition list in the blackboard [{}]".format(str(e)))


class PrePostConditions(behaviour.Behaviour):
    """
    Set of Functions concerning Postconditions handling
    """

    def __init__(self, pre, post, schema, name="Pre-Post-Condition Handling", ):
        super().__init__(name=name)

        try:
            # Load from json string set of postconditions
            # Create a set of Postcondition objects
            layers_schema = -len(schema)
            # Create a set of Postcondition dictionary with possible values True/False
            parameters = behaviour.blackboard.Client()

            if pre is True:
                precondition_dict = dict()
                while layers_schema <= -1:
                    task_parameters = schema[layers_schema]['parameters']
                    precondition = task_parameters[0]
                    # initalize all preconditions to false
                    # postcondition = task_parameters[0]
                    precondition_dict[precondition] = False
                    layers_schema += 1

            if post is True:
                postcondition_dict = dict()
                while layers_schema <= -1:
                    task_parameters = schema[layers_schema]['parameters']
                    postcondition = task_parameters[1]
                    # postcondition = task_parameters[0]
                    # initalize all postconditions to false
                    postcondition_dict[postcondition] = False
                    layers_schema += 1

            # Set postcondition list to blackboard
            if pre is True:
                parameters.register_key(key="/parameters/precondition_list", access=common.Access.WRITE)
                parameters.set("/parameters/precondition_list", precondition_dict)
            if post is True:
                parameters.register_key(key="/parameters/postcondition_list", access=common.Access.WRITE)
                parameters.set("/parameters/postcondition_list", postcondition_dict)

            print(parameters)

        except KeyError as e:
            raise RuntimeError("Could not set postcondition list in the blackboard [{}]".format(str(e)))

    def initialise(self):
        '''
        Loads from json string the list of postconditions and intialize them into the blackboard
        :return: Success always
        '''

        '''
        try:
            # Load from json string set of postconditions
            # Create a set of Postcondition objects
            layers_schema = -len(schema)
            # Create a set of Postcondition dictionary with possible values True/False
            postcondition_dict = dict()
            while layers_schema <= -1:
                task_parameters = schema[layers_schema]['parameters']
                postcondition = task_parameters[0]
                # initalize all postconditions to false
                postcondition_dict[postcondition] = False
                layers_schema += 1

            parameters = behaviour.blackboard.Client()
            # Set postcondition list to blackboard
            parameters.register_key(key="/parameters/postcondition_list", access=common.Access.WRITE)
            parameters.set("/parameters/postcondition_list", postcondition_dict)
            print(parameters)
        '''

        try:
            pass
        except KeyError as e:
            raise RuntimeError("Could not set postcondition list in the blackboard [{}]".format(str(e)))

    def updatePostCondition(self, postcondition, value):

        '''
        Update value of postcondition_list
        '''

        self.parameters = self.attach_blackboard_client("UpdatePostConditionsList", "parameters")
        self.parameters.register_key(key="/parameters/postcondition_list", access=common.Access.WRITE)
        postcondition_list = self.parameters.postcondition_list
        postcondition_list[postcondition] = value
        self.parameters.set("/parameters/postcondition_list", postcondition_list)

        return common.Status.SUCCESS


##############################################################################
# Blackboard Behaviours
##############################################################################


class CheckBlackboardVariableExists(behaviour.Behaviour):
    """
    Check the blackboard to verify if a specific variable (key-value pair)
    exists. This is non-blocking, so will always tick with
    status :data:`~py_trees.common.Status.FAILURE`
    :data:`~py_trees.common.Status.SUCCESS`.

    .. seealso::

       :class:`~py_trees.behaviours.WaitForBlackboardVariable` for
       the blocking counterpart to this behaviour.

    Args:
        variable_name: name of the variable look for, may be nested, e.g. battery.percentage
        name: name of the behaviour
    """

    def __init__(
            self,
            variable_name: str,
            name: str = common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name)
        self.variable_name = variable_name
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.READ)

    def update(self) -> common.Status:
        """
        Check for existence.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS` if key found, :data:`~py_trees.common.Status.FAILURE` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        try:
            unused_value = self.blackboard.get(self.variable_name)
            self.feedback_message = "variable '{}' found".format(self.variable_name)
            return common.Status.SUCCESS
        except KeyError:
            self.feedback_message = "variable '{}' not found".format(self.variable_name)
            return common.Status.FAILURE


class WaitForBlackboardVariable(CheckBlackboardVariableExists):
    """
    Wait for the blackboard variable to become available on the blackboard.
    This is blocking, so it will tick with
    status :data:`~py_trees.common.Status.SUCCESS` if the variable is found,
    and :data:`~py_trees.common.Status.RUNNING` otherwise.

    .. seealso::

       :class:`~py_trees.behaviours.CheckBlackboardVariableExists` for
       the non-blocking counterpart to this behaviour.

    Args:
        variable_name: name of the variable to wait for, may be nested, e.g. battery.percentage
        name: name of the behaviour
    """

    def __init__(
            self,
            variable_name: str,
            name: str = common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name, variable_name=variable_name)

    def update(self) -> common.Status:
        """
        Check for existence, wait otherwise.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS` if key found, :data:`~py_trees.common.Status.RUNNING` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        new_status = super().update()
        if new_status == common.Status.SUCCESS:
            self.feedback_message = "'{}' found".format(self.key)
            return common.Status.SUCCESS
        elif new_status == common.Status.FAILURE:
            self.feedback_message = "waiting for key '{}'...".format(self.key)
            return common.Status.RUNNING


class UnsetBlackboardVariable(behaviour.Behaviour):
    """
    Unset the specified variable (key-value pair) from the blackboard.

    This always returns
    :data:`~py_trees.common.Status.SUCCESS` regardless of whether
    the variable was already present or not.

    Args:
        key: unset this key-value pair
        name: name of the behaviour
    """

    def __init__(self,
                 key: str,
                 name: str = common.Name.AUTO_GENERATED,
                 ):
        super().__init__(name=name)
        self.key = key
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.WRITE)

    def update(self) -> common.Status:
        """
        Unset and always return success.

        Returns:
             :data:`~py_trees.common.Status.SUCCESS`
        """
        if self.blackboard.unset(self.key):
            self.feedback_message = "'{}' found and removed".format(self.key)
        else:
            self.feedback_message = "'{}' not found, nothing to remove"
        return common.Status.SUCCESS


class SetBlackboardVariable(behaviour.Behaviour):
    """
    Set the specified variable on the blackboard.

    Args:
        variable_name: name of the variable to set, may be nested, e.g. battery.percentage
        variable_value: value of the variable to set
        overwrite: when False, do not set the variable if it already exists
        name: name of the behaviour
    """

    def __init__(
            self,
            variable_name: str,
            variable_value: typing.Any,
            overwrite: bool = True,
            name: str = common.Name.AUTO_GENERATED,
    ):
        super().__init__(name=name)
        self.variable_name = variable_name
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.WRITE)
        self.variable_value = variable_value
        self.overwrite = overwrite

    def update(self) -> common.Status:
        """
        Always return success.

        Returns:
             :data:`~py_trees.common.Status.FAILURE` if no overwrite requested and the variable exists,  :data:`~py_trees.common.Status.SUCCESS` otherwise
        """
        if self.blackboard.set(
                self.variable_name,
                self.variable_value,
                overwrite=self.overwrite
        ):
            return common.Status.SUCCESS
        else:
            return common.Status.FAILURE


class CheckGoal(behaviour.Behaviour):
    """
        This checks if task execution final goal is completed based on the postcondition list
        stored in the blackboard
        This is True if all postconditions from postcondition list are set to True
        """

    def __init__(self, name="CheckGoal"):
        super().__init__(name=name)

        self.parameters = self.attach_blackboard_client("Task Execution Goal achieved?", "parameters")
        self.parameters.register_key(
            key="postcondition_list",
            access=common.Access.READ)

    def update(self) -> common.Status:

        """
        Check if all post-conditions are achieved.
        If true, goal is achieved and behavior tree node
        returns Success. Otherwise, returns Failure. Default, returns Running
        """
        # pdb.set_trace()
        postcondition_list = self.parameters.postcondition_list
        counter_true_postconditions = 0
        # Create array of emphasis objects
        for postcondition in postcondition_list:
            # Set Goal to false - return FAILURE if any postcondition has not been yet achieved
            if postcondition_list[postcondition] is False:
                self.logger.debug("%s.update()[%s: Failure]" % (self.__class__.__name__, self.parameters))
                self.feedback_message = "Failure"
                return common.Status.FAILURE
        self.logger.debug("%s.update()[%s: success]" % (self.__class__.__name__, self.parameters))
        self.feedback_message = "Success"
        return common.Status.SUCCESS


class CheckBlackboardVariableValue(behaviour.Behaviour):
    """
     Inspect a blackboard variable and if it exists, check that it
     meets the specified criteria (given by operation type and expected value).
     This is non-blocking, so it will always tick with
     :data:`~py_trees.common.Status.SUCCESS` or
     :data:`~py_trees.common.Status.FAILURE`.

     Args:
         variable_name: name of the variable to check, may be nested, e.g. battery.percentage
         expected_value: expected value
         comparison_operator: any method that can compare the value against the expected value
         name: name of the behaviour

     .. note::
         If the variable does not yet exist on the blackboard, the behaviour will
         return with status :data:`~py_trees.common.Status.FAILURE`.

     .. tip::
         The python `operator module`_ includes many useful comparison operations.

     .. _`operator module`: https://docs.python.org/2/library/operator.html
     """

    def __init__(
            self,
            variable_name: str,
            expected_value: typing.Any,
            comparison_operator: typing.Callable[[typing.Any, typing.Any], bool] = operator.eq,
            name: str = common.Name.AUTO_GENERATED
    ):
        super().__init__(name=name)
        self.variable_name = variable_name
        name_components = variable_name.split('.')
        self.key = name_components[0]
        self.key_attributes = '.'.join(name_components[1:])  # empty string if no other parts
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key=self.key, access=common.Access.READ)

        self.expected_value = expected_value
        self.comparison_operator = comparison_operator

    def update(self):
        """
        Check for existence, or the appropriate match on the expected value.

        Returns:
             :class:`~py_trees.common.Status`: :data:`~py_trees.common.Status.FAILURE` if not matched, :data:`~py_trees.common.Status.SUCCESS` otherwise.
        """
        self.logger.debug("%s.update()" % self.__class__.__name__)
        try:
            value = self.blackboard.get(self.key)
            if self.key_attributes:
                try:
                    value = operator.attrgetter(self.key_attributes)(value)
                except AttributeError:
                    self.feedback_message = 'blackboard key-value pair exists, but the value does not have the requested nested attributes [{}]'.format(
                        self.variable_name)
                    return common.Status.FAILURE
        except KeyError:
            self.feedback_message = "key '{}' does value check Failure".format(self.variable_name)
            return common.Status.FAILURE

        # success = self.comparison_operator(value, self.expected_value)
        if self.expected_value is True:
            # if success:
            self.feedback_message = "'%s' comparison succeeded [v: %s][e: %s]" % (
                self.variable_name, value, self.expected_value)
            return common.Status.SUCCESS
        else:
            self.feedback_message = "'%s' comparison failed [v: %s][e: %s]" % (
                self.variable_name, value, self.expected_value)
            return common.Status.FAILURE


class WaitForBlackboardVariableValue(CheckBlackboardVariableValue):
    """
    Inspect a blackboard variable and if it exists, check that it
    meets the specified criteria (given by operation type and expected value).
    This is blocking, so it will always tick with
    :data:`~py_trees.common.Status.SUCCESS` or
    :data:`~py_trees.common.Status.RUNNING`.

    .. seealso::

       :class:`~py_trees.behaviours.CheckBlackboardVariableValue` for
       the non-blocking counterpart to this behaviour.

    .. note::
        If the variable does not yet exist on the blackboard, the behaviour will
        return with status :data:`~py_trees.common.Status.RUNNING`.

    Args:
        variable_name: name of the variable to check, may be nested, e.g. battery.percentage
        expected_value: expected value
        comparison_operator: any method that can compare the value against the expected value
        name: name of the behaviour
    """

    def __init__(
            self,
            variable_name: str,
            expected_value: typing.Any,
            comparison_operator: typing.Callable[[typing.Any, typing.Any], bool] = operator.eq,
            name: str = common.Name.AUTO_GENERATED
    ):
        super().__init__(
            variable_name=variable_name,
            expected_value=expected_value,
            comparison_operator=comparison_operator,
            name=name
        )

    def update(self):
        """
        Check for existence, or the appropriate match on the expected value.

        Returns:
             :class:`~py_trees.common.Status`: :data:`~py_trees.common.Status.FAILURE` if not matched, :data:`~py_trees.common.Status.SUCCESS` otherwise.
        """
        new_status = super().update()
        if new_status == common.Status.FAILURE:
            return common.Status.RUNNING
        else:
            return new_status
