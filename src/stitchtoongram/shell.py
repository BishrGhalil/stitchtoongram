from stitchtoongram import __version__

# to not be removed by autoflake
from stitchtoongram.db import Chat
from stitchtoongram.db import Option
from stitchtoongram.db import User

c = Chat
o = Option
u = User

del c
del o
del u

print(f"STITCHTOONGRAM SHELL {__version__}\n")
