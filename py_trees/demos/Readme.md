# Guidelines

Each module here is a self-contained code sample for one of the demo scripts.
That means there is a fair bit of copy and paste happening, but that is an
intentional decision to ensure each demo script is self-contained and easy
for beginners to follow and/or copy-paste from.

Keep this in mind when adding additional programs.

# Setup your py_atentional_trees demos

1. in demos/__init___py import desired demo
```$xslt
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# Documentation
##############################################################################

"""
This package contains py_trees demo script code.
"""
##############################################################################
# Imports
##############################################################################

from . import action  # noqa
from . import blackboard  # noqa
from . import blackboard_namespaces  # noqa
from . import blackboard_remappings  # noqa
from . import context_switching  # noqa
from . import dot_graphs  # noqa
from . import lifecycle  # noqa
from . import selector  # noqa
from . import sequence  # noqa
from . import stewardship  # noqa
from . import test_expand_tree_json # noqa
from . import test_automated_planning # noqa

```

2. In tests/sertup.py add desired demos into console_script entries

```$xslt
entry_points={
        'console_scripts': [
            'py-trees-render = py_trees.programs.render:main',
            'py-trees-demo-action-behaviour = py_trees.demos.action:main',
            'py-trees-demo-behaviour-lifecycle = py_trees.demos.lifecycle:main',
            'py-trees-demo-blackboard = py_trees.demos.blackboard:main',
            'py-trees-demo-blackboard-namespaces = py_trees.demos.blackboard_namespaces:main',
            'py-trees-demo-blackboard-remappings = py_trees.demos.blackboard_remappings:main',
            'py-trees-demo-context-switching = py_trees.demos.context_switching:main',
            'py-trees-demo-dot-graphs = py_trees.demos.dot_graphs:main',
            'py-trees-demo-logging = py_trees.demos.logging:main',
            'py-trees-demo-pick-up-where-you-left-off = py_trees.demos.pick_up_where_you_left_off:main',
            'py-trees-demo-selector = py_trees.demos.selector:main',
            'py-trees-demo-sequence = py_trees.demos.sequence:main',
            'py-trees-demo-tree-stewardship = py_trees.demos.stewardship:main',
            'py-trees-demo-expand-tree-json = py_trees.demos.test_expand_tree_json:main',
            'py-trees-demo-automated-planning = py_trees.demos.test_automated_planning:main'
        ],
```

# Run a py_attentional_trees Demo
 
 1. go to root directory py_attentional_trees
2. source virutal environment:
source ./virtualenv.bash
3. Open ./buildinstalldemo.sh with vim and add the desired demo to be built. For example, for running test_automated_planning.py in rendering mode copy the following line of code in your ./buildinstalldemo.sh batch script
```
 #!/bin/bash 

 python setup.py build
 python setup.py install
 
 py-trees-demo-automated-planning -r
 ```

4. Run demo by typing py-trees-demo-automated-planning

