from __future__ import print_function

import json
import os
import sys
from metakernel import MetaKernel

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
    jupyter_edit_magic_sig = '~~~JUPYTER_EDIT_MAGIC~~~:'
    jupyter_edit_magic_sig_len = len(jupyter_edit_magic_sig)


    # def log_debug(self, msg):
    #     """Poor men's logger.  DEBUG:FIXME:Very inefficient!"""
    #     tty=os.getenv("DEBUG_TTY")
    #     if not tty: return
    #     with open(tty, "wb", 0) as fd:
    #         fd.write(("DEBUG: "+msg+"\n").encode(errors='replace'))

    
    def Print(self, *objects, **kwargs):
        if (objects
               and len(objects[0])>self.jupyter_edit_magic_sig_len
               and objects[0][:self.jupyter_edit_magic_sig_len]==self.jupyter_edit_magic_sig
               and objects[0][:-2]!="\r\n"):
            filename = objects[0][self.jupyter_edit_magic_sig_len:]
            edit_magic = self.line_magics['edit']
            edit_magic.line_edit(filename)
        else:
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
