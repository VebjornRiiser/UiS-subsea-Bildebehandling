import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--cam', default='both', type=str.lower, choices=["front","back","none","both"], help='Velg kamera som skal brukes')
args = parser.parse_args()

print(args)