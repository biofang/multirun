import shutil
from pathlib import Path
from enum import Enum

import typer
from click import Context
from typer.core import TyperGroup

from local import LocalRun

__version__ = "0.0.1"

class OrderCommands(TyperGroup):
  def list_commands(self, ctx: Context):
    return list(self.commands)

app = typer.Typer(
                cls=OrderCommands,
                help='''A Simple Parallel Cli Tool on Linux Platforms''',
                context_settings=dict(help_option_names=["-h", "--help"]), add_completion=False,)

class SplitMethod(str,Enum):
    line = "line",
    part = "part",

@app.command(name="local",no_args_is_help=True,help="Local Run")
def local_run(
    cmd_file: Path = typer.Argument(..., help="Input cmds file."),                      # 输入命令文件
    wkdir: Path = typer.Option(Path("./"),"--workdir","-w",help="The work dir."),       # 工作目录
    name : str = typer.Option(("work"),"--name","-n",help="The job cmd name."), 
    split_method: SplitMethod = typer.Option("line","--split_method","-s",
                                             help="File splitting method. split by lines, or split by parts."),    # 文件切分方式
    unit_num: int = typer.Option(1,"--unit_num","-un",help = """Split by line, the number of lines in each job,
                                or split by part, the total number of parts"""),                                   # 切分子文件内，或者份数
    process_num: int = typer.Option(4,"--process_num","-pn",help="Maximum number of local parallel jobs."),        # 进程数 
    force :  bool = typer.Option(False,"-f/-nf","--force/--not-force",help= "froce check for the cmd done file"),
    ):

    cmd_path = Path(cmd_file)
    wkdir = Path(wkdir).absolute() # 获取目录的绝对路径
    cmd_stem = cmd_path.stem

    if Path(f"{wkdir}/{cmd_path.name}.Success").exists() and not force:
        print(f"File: {cmd_path.name}.Success exists! Please check the completion status of previous jobs")
        exit(1)
    elif force:
            print("Clean up sub dir and log files!")
            shutil.rmtree(f"{wkdir}/{cmd_path.name}.run",ignore_errors=True)
            Path(f"{wkdir}/{cmd_path.stem}.jobs.log").unlink(missing_ok=True)
            Path(f"{wkdir}/{cmd_path.stem}.cmds.log").unlink(missing_ok=True)
            Path(f"{wkdir}/{cmd_path.name}.Success").unlink(missing_ok=True)

    local_run = LocalRun(cmd_path,wkdir,name,split_method,unit_num,cmd_stem)
    local_run.run(process_num)
    local_run.check()

@app.command(name="clean",no_args_is_help=True,help="clean up log file and tmp dir")
def clean_fun(
    cmd_file: Path = typer.Argument(..., help="Input cmds file."), 
    wkdir: Path = typer.Option(Path("./"),"--workdir","-w",help="The work dir."),
    cleanup: bool = typer.Option(True,"--cleanup","-c",help="Clean up sub directories and log files")
):
    cmd_path = Path(cmd_file)
    wkdir = Path(wkdir).absolute() # 获取目录的绝对路径

    if cleanup:
        print("Clean up sub directories and log files!")
        shutil.rmtree(f"{wkdir}/{cmd_path.name}.run",ignore_errors=True)
        Path(f"{wkdir}/{cmd_path.stem}.jobs.log").unlink(missing_ok=True)
        Path(f"{wkdir}/{cmd_path.stem}.cmds.log").unlink(missing_ok=True)
        Path(f"{wkdir}/{cmd_path.name}.Success").unlink(missing_ok=True)
        Path(f"{wkdir}/{cmd_path.name}.Failure").unlink(missing_ok=True)

@app.callback(invoke_without_command=True, no_args_is_help=True)
def main(
        version: bool = typer.Option(False, '--version', '-v', help='Show version informatio.'),
):
    if version:
        typer.echo(f'multiRun version: {__version__}')
        raise typer.Exit()

if __name__ == "__main__":
    app()
