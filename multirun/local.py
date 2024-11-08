#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import time
import subprocess 
from multiprocessing import Pool
from pathlib import Path
# import logging

from loguru import logger
from log import setup_logger
from tools import Tools
from utils import job_state,spend_time,check_cmd

'''
cmd_list  # 为项目要运行的所有命令文件
job 为单个子shell脚本,用于subprocess运行,内部可能包含多个cmd
cmd 为cmds_file 中每一行命令,cmd为任务的最小单位(each line)
Logger
# 主要多进程日志问题，是否有更优化的方案
需要建立两套日志，一套用于输出jobs日志信息，另一套用于error级别的cmd，方便后续查看；

# 注意
windows 与 linux 多进程方式有差异;
'''

class LocalRun:
    def __init__(self,cmd_file,wkdir,name,split_method,unit_num,log_prefix) -> None:
        self.cmd_file = Path(cmd_file)
        self.wkdir = wkdir
        self.name = name

        self.tool = Tools(cmd_file,wkdir,name)

        self.cmds_list = self.tool.cmds_list

        # get split mthod line or part;
        if split_method == "line":
            self.jobs_dict = self.tool.split_cmds_by_lines(unit_num)
        else:
            self.jobs_dict = self.tool.split_cmds_by_parts(unit_num)

        self.log_prefix = log_prefix

        # set logger 
        setup_logger(self.log_prefix)

        logger.info(f"LocalRun initialized with command file: {cmd_file}")

    def single_job(self,cmd_tuple,job):
        '''
        运行单个job
        '''  
        cmd = f"sh {job} 1>{job}.std 2>{job}.err && touch {job}.done"
        if job_state(job):                       # xxx.done 存在时，则跳过不允许任务
            logger.info("# Attention cmd sikpped! due to %s exisit" % (job))
        else:
            start_time = time.time()
            signal = subprocess.call(cmd, shell=True)
            if signal == 0 :  
                # 信号为0,仅说明job从头运行到尾,且结尾无报错;job里面的cmd也可能是运行错误的,；
                logger.info(f"Job Done!\t{spend_time(start_time,time.time())}\t{job}")
            else :
                logger.error(f"Job Fail!\t{spend_time(start_time,time.time())}\t{job}")
            undo_cmds = check_cmd(cmd_tuple,job,self.cmds_list)
            if undo_cmds:
                for undo_cmd in undo_cmds:
                    logger.bind(CmdError=True).error(f"{undo_cmd}")
    
    def run(self,parallel_num):
        '''
        本地并行
        '''
        logger.info(f"MultiRun initialized with local")
        pool = Pool(parallel_num)
        for cmd_tuple,job in self.jobs_dict.items():
            pool.apply_async(self.single_job,args=(cmd_tuple,job,))
        pool.close()
        pool.join()
    
    def check(self):
        '''
        检查任务完成情况
        '''
        all_cmds_num = len(self.cmds_list)
        all_jobs_num = len(self.jobs_dict)

        sub_dir = Path(self.tool.sub_dir)  # xxx.run dir 
        tmp_dir = Path(self.tool.tmp_dir)  # xxx.run/.TMP_DIR dir 
        
        jobs_done_num = len(list(sub_dir.glob(f"{self.name}.*.done")))
        cmds_done_num = len(list(tmp_dir.glob(f"sub.*.done")))

        if jobs_done_num == all_jobs_num and cmds_done_num == all_cmds_num:
            logger.info("Congratulations, all cmds have been completed!")
            Path(f"{self.wkdir}/{self.cmd_file.name}.Success").touch()
        else:
            logger.error(f"Attention! Some cmds[{cmds_done_num}/{all_cmds_num}] did not run successfully!")
            logger.error(f"Please check the unfinished cmds log : {Path(self.log_prefix).absolute()}.cmds.log")
            Path(f"{self.wkdir}/{self.cmd_file.name}.Failure").touch()
        