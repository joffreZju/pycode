from .moduleY import spam
from .moduleY import spam as ham
from . import moduleY
from ..subpkg1 import moduleY
from ..subpkg2.moduleZ import eggs
from ..moduleA import foo
from .. import moduleA
from ...package import bar
from ...sys import path

spam()

ham()

moduleY.spam()

eggs()

foo()

moduleA.foo()
