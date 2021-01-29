from __future__ import print_function

import json
import os
import sys
from metakernel import MetaKernel
import re

from . import __version__


def get_kernel_json():
    """Get the kernel json for the kernel.
    """
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'kernel.json')) as fid:
        data = json.load(fid)
    data['argv'][0] = sys.executable
    return data


class BashKernel(MetaKernel):
    app_name = 'calysto_bash'
    implementation = 'Calysto Bash'
    implementation_version = __version__
    language = 'bash'
    language_version = __version__
    banner = "Calysto Bash - interact with bash"
    language_info = {
        'mimetype': 'text/x-sh',
        'name': 'bash',
        'file_extension': '.sh',
        "version": __version__,
        'help_links': MetaKernel.help_links,
    }
    kernel_json = get_kernel_json()
    jupyter_edit_magic_rx = re.compile(r'^~~~JUPYTER_EDIT_MAGIC~~~:(.*?):~~~\r?$', re.MULTILINE)

    # def log_debug(self, msg):
    #     """Poor men's logger.  DEBUG:FIXME:Very inefficient!"""
    #     tty=os.getenv("DEBUG_TTY")
    #     if not tty: return
    #     with open(tty, "wb", 0) as fd:
    #         fd.write(("DEBUG: "+msg+"\n").encode(errors='replace'))


#    def __init__(self, *objects, **kwargs):
#        super().__init__(*objects, **kwargs)
#        cmd = """JUPYTER_EDITOR_FN_BODY='myedit() { touch "$1"; printf "%s$1"; }'; export JUPYTER_EDITOR_FN_BODY"""%self.jupyter_edit_magic_sig
#        self.log_debug(f"About to execute: '{cmd}'")
#        self.do_execute_direct(cmd)
#        self.log_debug(f"Back.")
    
    
    def Print(self, *objects, **kwargs):
        self.log.debug(f"Printing objects: {objects}")
        if (objects):
            arg0 = objects[0]
            mo = self.jupyter_edit_magic_rx.search(arg0)
            if mo:
                filename = mo.group(1)
                self.log.debug(f"Detected edit magic for '{filename}'")
                edit_magic = self.line_magics['edit']
                edit_magic.line_edit(filename)
                arg0 = arg0[:mo.start()]+arg0[mo.end():]
                objects = (arg0,) + objects[1:]
                self.log.debug(f"Modified objects: {objects}")

        return super().Print(*objects, **kwargs)

            
    def get_usage(self):
        return "This is the bash kernel."

    def do_execute_direct(self, code):
        if not code.strip():
            return
        self.log.debug('execute: %s' % code)
        shell_magic = self.line_magics['shell']
        try:
            shell_magic.eval(code.strip(), True)
            cwd = shell_magic.eval('pwd').rstrip("\n").rstrip("\r")
            if os.path.exists(cwd):
                os.chdir(cwd)
            else:
                self.log.debug("Path '%s' does not exists" % cwd)
            
        except Exception as e:
            self.Error(e)
        self.log.debug('execute done')

    def get_completions(self, info):
        shell_magic = self.line_magics['shell']
        return shell_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=1, none_on_fail=False):
        code = info['code'].strip()
        if not code or len(code.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        shell_magic = self.line_magics['shell']
        return shell_magic.get_help_on(info, 1)

    def repr(self, data):
        return data
