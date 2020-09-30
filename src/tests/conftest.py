import sys
from os.path import dirname


p = dirname(dirname(__file__))
sys.path.insert(0, p)

print("final path:", sys.path)
