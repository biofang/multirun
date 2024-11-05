# import importlib
# import multirun            # 为自编写模块
# importlib.reload(multirun)

import typer
import shutil
from pathlib import Path
from enum import Enum

from local import LocalRun

# from log import Logger

# if __name__ == '__main__':
#     # logger = logging.getLogger(__name__)
#     # logger = Logger('./my_log_file.log').get_logger()
#     # logger = logger_instance.logger  # 获取配置好的 logger
#     shutil.rmtree("./tmp.cmd.run",ignore_errors=True)
#     local_run = LocalRun("./tmp.cmd","dddd.log")
#     local_run.run(2)

__version__ = "0.0.1"

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
app = typer.Typer(help='''Design for selecting model;\n
                        用于筛选模型；
                  ''',
                  context_settings=CONTEXT_SETTINGS, add_completion=False)

class SplitMethod(str,Enum):
    line = "line",
    part = "part",

@app.command(name="local",no_args_is_help=True,help="Local Run")
def local_run(
    cmd_file: Path = typer.Argument(..., help="Input cmds file."),                     # 输入命令文件
    split_method: SplitMethod = typer.Option("line","--split_method","-s",help="File splitting method. split by lines, or plit by parts."),    # 文件切分方式
    unit_num: int = typer.Option(1,"--unit_num","-un",help = """Split by line, the number of lines in each sub-file,
                                or split by part, the total number of parts"""), # 切分子文件内，或者份数
    process_num: int = typer.Option(4,"--process_num","-pn",help="'max number of local subprocess."),        # 进程数 
    force :  bool = typer.Option(False,"-f/-nf","--force/--not-force",help= "froce check for the cmd done file"),
    ):
    # pass
    cmd_path = Path(cmd_file)
    wk_dir = cmd_file.parent.absolute()  
    cmd_stem = cmd_path.stem
    # wk_done = Path(F"{cmd_file}.Done") # 后续整个任务的done

    if force:
        shutil.rmtree(f"{cmd_path}.run",ignore_errors=True)

    local_run = LocalRun(cmd_file,split_method,unit_num,cmd_stem)
    local_run.run(process_num)

@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
        version: bool = typer.Option(False, '--version', '-v', help='Show version informatio.'),
):
    if version:
        typer.echo(f'multiRun version: {__version__}')
        raise typer.Exit()

if __name__ == "__main__":
    app()
