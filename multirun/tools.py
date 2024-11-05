#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pathlib import Path
import math
import shutil

class Tools:
    def __init__(self, cmd_file: Path, prefix :str = "work") -> None:
        self.file = Path(cmd_file)
        self.prefix = prefix

        self.wkdir = self.file.resolve().parent
        self.filename =  self.file.name

        self.cmds_list = self._get_cmds()   # all cmds list 
        self.sub_dir,self.tmp_dir = self._sub_dir()      # sub cmds output dir and tmp dir

    def _get_cmds(self):
        cmds_lst = []
        with open(self.file,"r") as inf:
            for line in inf:
                line = line.strip()
                if line.startswith("#"):
                    continue
                cmds_lst.append(line)
        return cmds_lst

    def _sub_dir(self):
        '''
        Subcommand output directory
        '''
        sub_dir = self.wkdir/f"{self.filename}.run"
        sub_dir.mkdir(exist_ok=True)    # 目录存在时,不报错;

        # 建立临时隐藏目录，用于标识shell内部子命令是否运行成功;
        # 当shell内部有报错时，不容易在外部捕获;
        tmp_dir = sub_dir/".TMP_DIR"
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)
        tmp_dir.mkdir(exist_ok=True)
        return sub_dir,tmp_dir

    def split_cmds_by_lines(self,line_num):
        '''
        Split cmds file by line and create sub cmd files
        按行切分
        '''
        jobs_dict = {}
        cmds_num = len(self.cmds_list)

        if cmds_num % line_num == 0:            # 能整除
            job_nums = int(cmds_num / line_num) # 任务数 
        else: 
            job_nums = int(cmds_num / line_num) + 1
        width = len(str(job_nums))
        for i in range(job_nums):
            sub_file = f"{self.sub_dir}/{self.prefix}.{str(i+1).zfill(width)}.sh"
            with open(sub_file,"w") as outf:
                cmd_num_list = []
                outf.write("set -e\necho start at time `date +%F'  '%H:%M:%S`\n")
                outf.write(f"cd \"{self.wkdir}\"\n")
                for j in range(i*line_num,(i+1)*line_num):
                    if j < cmds_num:
                        cmd_num_list.append(j)
                        outf.write(f"{self.cmds_list[j]} && touch \"{self.tmp_dir}/sub.{j}.done\"\n")
                outf.write(f"touch \"{self.sub_dir}/{self.prefix}.{str(i+1).zfill(width)}.sh.done\"\n")
                outf.write("echo finish at time `date +%F'  '%H:%M:%S`\n")
            jobs_dict[tuple(cmd_num_list)] = sub_file
        return jobs_dict

    def split_cmds_by_parts(self,part_num):
        '''
        Split cmds file by parts and create sub cmd files
        按份切分
        '''
        jobs_dict = {}
        cmds_num = len(self.cmds_list)
        line_num = int(math.ceil(cmds_num / part_num))  # 向上取整,切分的数量
        width = len(str(part_num))
        for i in range(part_num):
            cmd_num_list = []
            sub_file = f"{self.sub_dir}/{self.prefix}.{str(i+1).zfill(width)}.sh"
            with open(sub_file,"w") as outf:
                outf.write("set -e\necho start at time `date +%F'  '%H:%M:%S`\n")
                outf.write(f"cd \"{self.wkdir}\"\n")
                for j in range(i*line_num,(i+1)*line_num):
                    if j < cmds_num:
                        cmd_num_list.append(j)
                        outf.write(f"{self.cmds_list[j]} && touch \"{self.tmp_dir}/sub.{j}.done\"\n")
                outf.write(f"touch \"{self.sub_dir}/{self.prefix}.{str(i+1).zfill(width)}.sh.done\"\n")
                outf.write("echo finish at time `date +%F'  '%H:%M:%S`\n")
            jobs_dict[tuple(cmd_num_list)] = sub_file
        return jobs_dict

# if __name__ == "__main__":
#     tools = Tools("./tmp.cmd","tmp")

#     print(tools.split_cmds_by_parts(4))