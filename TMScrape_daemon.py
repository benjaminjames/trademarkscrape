# -*- coding: utf-8 -*-

import os
import time


def killScreens():
    for scrn in getScreenNames():
        if 'daemon' not in scrn.lower():
            print 'KILLING %s' % scrn

            cmd = 'screen -X -S %s quit' % scrn
            try:
                os.system(cmd)
            except:
                pass


def getScreenNames():
    # Not used
    screens = os.popen('screen -ls').read()
    screens = [x for x in screens.split('\t') if '.' in x and 'ec2' not in x]
    screens = [x for x in screens if 'detached' and 'socket' not in x.lower() ]
    return screens


def main():
    print 'RUNNING TM SCRAPE..'

    # Terminate all processes running via screen
    os.system('killall screen')

    # Each process gets its own screen
    current_dir = os.popen('pwd').read().replace('\n','')

    processes = [x for x in os.listdir(current_dir)]
    processes = [x for x in processes if '.py' in x]
    processes = [x for x in processes if 'helpers' not in x]
    processes = [x for x in processes if 'daemon' not in x]

    for py_script in processes:
        print 'RUNNING', py_script

        process_name = py_script.split('.')[0].upper()

        # Create a screen and run
        make_screen = 'screen -S %s -d -m' % process_name

        cmd = 'screen -S %s -p 0 -X stuff "python %s\n"'

        run_process = cmd % (process_name,py_script)

        os.system(make_screen)
        os.system(run_process)


main()
