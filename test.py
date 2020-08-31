import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-u","--upgrade", help="fully automatized upgrade")
    args = parser.parse_args()

    if args.upgrade:
        print("Starting with upgrade procedure")
main()
