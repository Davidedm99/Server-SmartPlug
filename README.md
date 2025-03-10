# Creating your middleware
To create your own middleware edit the file [main.py](./main.py) following the todos. 
This allows to change 3 things:
- **Options** are the settings of your program. An option has a name, a value which can be either a string, integer, float, bool or a path.
    Also options can be hidden (`visible=False`) for programmatic usage that should not appear in the Options window.
- **The main frame** the GUI specific to the application. The `MainWindow` class exposes a `main_frame` attribute, which should be the parent of all your GUI.
- **API** routes can be specified to make the middleware available on the network. They are all POST methods.
> DESCRIBE BETTER HOW TO SPECIFY AN API

You can write the rest of your code then and reference it in these methods

# Build the executable
When you're done, the exe can be built using [pytinstaller](https://pyinstaller.org/en/stable/index.html). 
The following command should suffice in most cases:
```shell
pyinstaller -y main.spec
```

Sometimes pyinstaller may miss some of your dependencies. If that's your case, usually adding the option `--collect-all MODULENAME`
can solve the issue.