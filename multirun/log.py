from loguru import logger
import sys

def setup_logger(prefix):

    logger.remove()

    time_format = "{time:YYYY-MM-DD at HH:mm:ss}"

    # 打印到屏幕中
    logger.add(sys.stderr, level="DEBUG", format= time_format + " | {level} | {message}",enqueue=True)

    # job 日志
    logger.add(f"{prefix}.jobs.log", level="INFO", format= time_format + " | {level} | {message}",
               filter=lambda record: "CmdError" not in record["extra"],   
               enqueue=True)

    # cmd 错误日志
    logger.add(f"{prefix}.cmds.log", level="ERROR", format="{message}",
               filter=lambda record: "CmdError" in record["extra"],
               enqueue=True)

# def setup_logger(prefix):
#     logger.remove()
    
#     # 只写入 "a" logger 的消息
#     logger.add(f"{prefix}a.log", filter=lambda record: record["extra"].get("name") == "a")
    
#     # 只写入 "b" logger 的消息
#     logger.add(f"{prefix}b.log", format="{message}", filter=lambda record: record["extra"].get("name") == "b")

#     logger_a = logger.bind(name="a")
#     logger_b = logger.bind(name="b")
    
#     return logger_a, logger_b