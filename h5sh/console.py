# -*- coding: utf-8 -*-

from __future__ import (division, absolute_import, print_function, )
from six.moves import input
#-----------------------------------------------------------------------------#
from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import BashLexer
import shlex

from .commands import COMMANDS
from .commands.system import INTERRUPT_CMD, NULL_CMD

###############################################################################

class Console(object):
    def __init__(self, state):
        # Command-line state
        self.state = state
        # Prompt session
        self.session = PromptSession(
                lexer=PygmentsLexer(BashLexer))
        # Debug mode
        self.debug = False

    def prompt(self):
        with patch_stdout(raw=True):
            text = self.session.prompt(self.state.get_prompt())
        return text

    def read(self):
        """Prompt for and read a single command.
        """
        try:
            text = self.prompt()
        except KeyboardInterrupt:
            cmd = INTERRUPT_CMD.name
            args = ()
        except EOFError:
            cmd = "exit"
            args = ()
        else:
            args = shlex.split(text)
            if args:
                cmd = args[0]
                args = args[1:]
            else:
                (cmd, args) = ("__NULL__", ())
        return (cmd, args)

    def interact(self):
        while True:
            (cmd_name, args) = self.read()
            try:
                cmd = COMMANDS[cmd_name]
            except KeyError:
                print("h5sh: {}: command not found".format(cmd_name))
                continue

            try:
                cmd(self.state, *args)
            except KeyboardInterrupt:
                INTERRUPT_CMD(self.state)
            except Exception as e:
                if self.debug:
                    import logging as log
                    log.exception(e)
                    raise
                if isinstance(e, (TypeError, ValueError)):
                    print("{}: {!s}".format(cmd_name, e))
                    continue

