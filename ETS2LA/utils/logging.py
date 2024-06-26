from rich.logging import RichHandler
from ETS2LA.utils.colors import *
import logging
import os

def SetupGlobalLogging():
    # Print levels in color
    logging.addLevelName(logging.INFO, f"{DARK_GREEN}[INF]{END}")
    logging.addLevelName(logging.WARNING, f"{DARK_YELLOW}[WRN]{END}")
    logging.addLevelName(logging.ERROR, f"{DARK_RED}[ERR]{END}")
    logging.addLevelName(logging.CRITICAL, f"{RED}[CRT]{END}")

    # Set up logging
    logging.basicConfig(format=
                        f'[dim][link file://%(pathname)s]%(filename)s[/link file://%(pathname)s][/dim]\t %(message)s', 
                        level=logging.INFO,
                        datefmt=f'%H:%M:%S',
                        handlers=[RichHandler(markup=True, rich_tracebacks=True, show_level=True, show_path=False)]
                        )
    
    
    # If the file path doesn't exist, create it
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # If the log file exists, delete it
    if os.path.exists("logs/ETS2LA.log"):
        try:
            os.remove("logs/ETS2LA.log")
        except:
            logging.error("Could not delete the log file.")
    
    # Write the logs to a file
    file_handler = logging.FileHandler("logs/ETS2LA.log")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(file_handler)
    
    logging.info("Logger initialized.")
    
    return logging.getLogger()

def SetupProcessLogging(name, console_level=logging.INFO, filepath="", use_fancy_traceback=True):
    # Remove the default handler
    logging.getLogger().handlers = []
    logging.getLogger().addHandler(logging.NullHandler())
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Print levels in color
    logging.addLevelName(logging.DEBUG, f"{DARK_GREY}[DBG]{END}")
    logging.addLevelName(logging.INFO, f"{DARK_GREEN}[INF]{END}")
    logging.addLevelName(logging.WARNING, f"{DARK_YELLOW}[WRN]{END}")
    logging.addLevelName(logging.ERROR, f"{DARK_RED}[ERR]{END}")
    logging.addLevelName(logging.CRITICAL, f"{RED}[CRT]{END}")

    # Set up logging
    logging.basicConfig(format=
                        f'[dim][link file://%(pathname)s]%(filename)s[/link file://%(pathname)s][/dim]\t %(message)s',
                        level=logging.DEBUG,
                        datefmt=f'%H:%M:%S',
                        handlers=[RichHandler(markup=True, rich_tracebacks=use_fancy_traceback, show_level=True)]
                        )
    
    # Create a file handler
    if filepath != "":
        if not filepath.endswith(".log"):
            filepath += f"{name}.log"
            
        # Check that the directory exists
        if not os.path.exists(os.path.dirname(filepath)):
            os.makedirs(os.path.dirname(filepath))
        # Remove the file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        # Write the logs to a file
        file_handler = logging.FileHandler(filepath)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(file_handler)
        
    # Create a console handler with a higher log level
    logging.getLogger().addHandler(RichHandler(markup=True, rich_tracebacks=use_fancy_traceback, show_level=True, level=console_level, log_time_format="%H:%M:%S"))
    return logging.getLogger()