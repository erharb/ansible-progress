# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: progress_dots
    callback_type: aggregate
    requirements:
      - place in callback_plugins folder
    short_description: Adds progress dots to display while tasks do work
    version_added: "2.0"
    description:
        - This callback displays dots on the screen only (not logged) to show indeterminate progress while tasks are doing remote work
    options:
      progress:
        description: Time in seconds between progress dots displaying after each task starts
        env:
          - name: PROGRESS_TIME
        default: 2
    note:
      - "TODO: expand configuration options now that plugins can leverage Ansible's configuration"
'''

import os
import sys
import threading
import time
from ansible.module_utils._text import to_bytes, to_text

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    """
    This callback module displays dots only on screen as remote task work is being done
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = 'progress_dots'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        self._prev_carried_msg = None
        self._progress = None

        super(CallbackModule, self).__init__()
        
    def v2_playbook_on_task_start(self, task, is_conditional):
        # stop previous task progress thread and spawn a new task progress thread for this task
        if self._progress is not None:
            self._progress.keep_alive = False

        self._progress = ProgressThread(self._print_progress_dot)
        self._progress.start()
            
    def v2_playbook_on_play_start(self, play):
        if self._progress is not None:
            # stop previous task progress thread since new play means new tasks
            self._progress.keep_alive = False
            self._progress = None

        if self._prev_carried_msg is not None:
            # print blank line so last carried messages are not overwritten
            self._clear_carried_msg()
            self.progress_display('')
            
    def v2_playbook_on_stats(self, stats):
        if self._prev_carried_msg is not None:
            # print blank line so last carried messages are not overwritten by command prompt
            self._clear_carried_msg()
            self.progress_display('')

    def progress_display(self, msg, color=None, stderr=False, end_line=True):
        """ Display a message to the user (modification of Ansible's ansible.utils.Display.display() to prevent automatic newline)
        https://github.com/ansible/ansible/blob/devel/lib/ansible/utils/display.py
        Note: msg *must* be a unicode string to prevent UnicodeError tracebacks.
        """
        nocolor = msg
        if color:
            msg = stringc(msg, color)

        if msg is not None:

            if end_line:
                msg2 = msg + u'\n'
            else:
                msg2 = msg + u' '

            if not end_line:
                self._store_carried_msg(nocolor)

            elif self._prev_carried_msg is not None:
                # print blank with newline to write to next line instead of carried line
                self._clear_carried_msg()
                self.progress_display('')

            msg2 = to_bytes(msg2, encoding=self._display._output_encoding(stderr=stderr))
            if sys.version_info >= (3,):
                # Convert back to text string on python3
                # We first convert to a byte string so that we get rid of
                # characters that are invalid in the user's locale
                msg2 = to_text(msg2, self._display._output_encoding(stderr=stderr), errors='replace')

            # Note: After Display() class is refactored need to update the log capture
            # code in 'bin/ansible-connection' (and other relevant places).
            if not stderr:
                fileobj = sys.stdout
            else:
                fileobj = sys.stderr

            fileobj.write(msg2)

            try:
                fileobj.flush()
            except IOError as e:
                # Ignore EPIPE in case fileobj has been prematurely closed, eg.
                # when piping to "head -n1"
                if e.errno != errno.EPIPE:
                    raise

    def _print_progress_dot(self, dot='.', color=None):
        self.progress_display(dot, color=color, end_line=False)

    def _store_carried_msg(self, msg):
        # could haved used a boolean, but just in case length of message is needed it will be here
        if self._prev_carried_msg is None:
            self._prev_carried_msg = ''
        self._prev_carried_msg = self._prev_carried_msg + msg

    def _clear_carried_msg(self):
        self._prev_carried_msg = None
    

class ProgressThread(threading.Thread):
    def __init__(self, function_to_call, sleep_time=os.getenv('PROGRESS_TIME', 2)):
        threading.Thread.__init__(self)
        self.daemon = True
        self.runnable = function_to_call
        self.sleep_time = float(sleep_time)

        self.keep_alive = True

    def run(self):
        time.sleep(self.sleep_time)
        while self.keep_alive:
            self.runnable()
            time.sleep(self.sleep_time)
            
