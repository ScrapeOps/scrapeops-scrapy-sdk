import time
import sys

def current_time():
    t = time.time()
    return int(round(t, 0))


def get_args():
    arg_dict = {'raw_string': '', 'args': [], 'options': []}
    if sys.argv[0] == 'crawl' or sys.argv[0]  == 'runspider': 
        args = sys.argv[2:]
    else:
        args = sys.argv[1:]
    for index, arg in enumerate(args):
        arg_dict['raw_string'] += append_raw_string(arg)
        if arg.startswith('--'):
            arg_dict['options'].append(arg)
        if arg.startswith('-a'):
            try:                   
                if args[index + 1].startswith('-') == False and args[index + 1].startswith('--') == False: arg_dict['args'].append(args[index + 1])  
            except:
                arg_dict['args'].append(arg)
    return arg_dict



def append_raw_string(arg):
    if ' ' in arg:
         return '"{}"  '.format(arg)
    return "{}  ".format(arg)





