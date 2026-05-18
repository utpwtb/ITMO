import logging
import sys

from src.machine.main import main as machine
from src.translator.main import main as translate


def start() -> None:
    logging.getLogger().setLevel(logging.DEBUG)
    translate(sys.argv[1], "./dbg/i.txt", "./dbg/d.txt")
    machine("./dbg/i.txt", "./dbg/d.txt", "./dbg/input.txt", [1, 2], logging.DEBUG)
