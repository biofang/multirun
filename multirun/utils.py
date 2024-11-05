#!/usr/bin/env python
# -*- coding: UTF-8 -*-

'Utils for multiRun'

# import logging
from pathlib import Path

# logger = logging.getLogger('tttmp')

def job_state(job):
    '''
    Check the status of the job before running
    '''
    job_done_file = Path(f"{job}.done")
    if job_done_file.exists():
        return True
    else:
        return False

def check_cmd(cmd_num_tuple,job,cmds_list):
    '''
    Check if cmd runs successfully
    '''
    undo_cmd_list = []
    sub_dir = Path(job).parent
    for cmd_num in cmd_num_tuple:
        cmd_done_file = Path(f"{sub_dir}/.TMP_DIR/sub.{cmd_num}.done")
        if not cmd_done_file.exists():
            # logger.error(f"Faild {cmds_list[cmd_num]}")
            undo_cmd_list.append(cmds_list[cmd_num])
    return undo_cmd_list

def spend_time(stime,etime):
    spend=int(etime)-int(stime)
    h = int(spend/3600)
    remain = spend%3600
    m = int(remain/60)
    s = remain%60
    return "%sh %s m %ss" %(h,m,s)

def get_log_prefix(cmds_file):
    pass


