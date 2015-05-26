import logging
import os
import shutil
import sys

formatter = logging.Formatter(u'[%(levelname)s] %(name)s '
                              u'%(lineno)d: %(message)s')
log = logging.getLogger()
sh = logging.StreamHandler()
log.addHandler(sh)


class ChDir(object):

    def __init__(self, goto):
        self.goto = goto
        self.old_dir = os.getcwd()

    def __enter__(self, *args, **kwargs):
        os.chdir(self.goto)

    def __exit__(self, *args, **kwargs):
        os.chdir(self.old_dir)


def remove_dist():
    with ChDir(u'dist'):
        files = os.listdir(os.getcwd())
        for f in files:
            if u'.DS' in f:
                continue
            elif os.path.isfile(f) is True:
                os.remove(f)
            elif os.path.isdir(f) is True:
                shutil.rmtree(f, ignore_errors=True)


commands = {
    u'remove-dist': remove_dist,
    }


def main():
    try:
        cmd = sys.argv[1]
        if cmd not in commands.keys():
            sys.exit(u'Not a valid command:\n\nAvailable '
                     u'commands\n{}'.format(' '.join(commands.keys())))
        else:
            commands[cmd]()
    except IndexError:
        sys.exit(u'You must pass a command')


if __name__ == '__main__':
    main()
