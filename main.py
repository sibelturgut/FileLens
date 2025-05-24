from scanner.cli.terminal import run_cli
from scanner.service import scan

if __name__=="__main__":
    #run_cli()
    scan.scan("/home", 32)