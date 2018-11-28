#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      User
#
# Created:     29-11-2018
# Copyright:   (c) User 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# StdLib
import os
import logging
import subprocess
# local
import common

class FailureRunner():# WIP
    """Run prepared functions when triggered"""
    def __init__(self):# TODO: Choose what to store here
        self.failure_funcs = []# [(function,args),...]
        return
    def fail(self):
        """Trigger all failure hooks"""
        for func, args in self.failure_funcs:
##            try:
                func(*args)# TODO: Make sure args get passed correctly
##            except Exception:
##                pass# We want all the outputs to fire
        return




class CliRunner():# WIP
    """Run prepared command line commands when triggered"""
    def __init__(self):# TODO: Choose what to store here
        self.commands = []# [['commandone.exe0','arg1','arg2'],...]
        return

    def run_commands(self):
        for command in self.commands:
            self.run_command(command)

    def run_command(self, command):
        logging.info('Running command: {0!r}'.format(command))
        cmd_output = subprocess.check_output(command, shell=True)
        logging.info('cmd_output = {0!r}'.format(command))
        return



def example():# WIP
    """Example/testing for other code"""
    logging.info('start example()')
    fr = FailureRunner()
    cr = CliRunner()
    cr.commands.append(['echo', '"LOLDONGS \n TEST STRING \n THIRD LINE"', '>', 'on_fail_example.txt'])# Does not work
    cr.commands.append("""type nul >triggered.txt""")# Creates empty file
    cr.commands.append('dir > triggered2.txt')# Lists dir contents
    fr.failure_funcs.append( (cr.run_commands, {} ) )
    fr.fail()
    logging.info('end example()')
    return


def main():
    example()
    pass

if __name__ == '__main__':
    common.setup_logging(os.path.join("debug", "on_fail.log.txt"))# Setup logging
    try:
        main()
    # Log exceptions
    except Exception, e:
        logging.critical(u"Unhandled exception!")
        logging.exception(e)
    logging.info(u"Program finished.")
