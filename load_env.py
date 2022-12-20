import os
from subprocess import run
print(os.getcwd())
run("export $(grep -v '^#' ./ENV | xargs)")