from rich import print
from time import time

class Logger:
    def __init__(self, filepath):
        self.filepath = filepath
    
    def internal_error(self, message, error):
        print("[bold red]" + message + "[/bold red]")
        print("[bold red]" + error + "[/bold red]")
        print("[blue]" + self.filepath + "[/blue]")
        print("[blue]" + str(time()) + "[/blue]")
        print("=" * 50)
    
    def error(self, message):
        print("[bold red]" + message + "[/bold red]")
        print("[blue]" + self.filepath + "[/blue]")
        print("[blue]" + str(time()) + "[/blue]")
        print("=" * 50)


if __name__ == "__main__":
    logger = Logger(__file__)
    logger.internal_error("Internal Error", "Something went wrong")