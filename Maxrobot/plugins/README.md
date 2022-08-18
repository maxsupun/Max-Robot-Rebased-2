## Maxrobot bot example plugin format here :
You can create your own custom plugin useing this format or use any [pyrogram](http://pyrogram.org) method !


```
from Maxrobot import app
from Maxrobot.utils.commands import *

@app.on_message(command("test"))
async def plug(_, message):
    Theteambots = await message.reply_text(text="Hello I am Maxrobot"
    )
    supun = """
I'm a group management bot with some useful features.
@TheTheMaxrobotbot    
    """
    await Theteambots.edit_text(supun)

__MODULE__ = "test"
__HELP__ = """  
/test - test cmd here
"""
```

