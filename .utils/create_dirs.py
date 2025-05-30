import os
import argparse



def main():
    staging_dir = r"C:\Users\u8064927\Desktop\Ali\_work\Normstelle\Teile und Stoffe\Staging"

    parser = argparse.ArgumentParser(description="Hello there")

    parser.add_argument("-r", help="080-086")

    args = parser.parse_args()

    print(args.range) 



if __name__ == "__main__":
    main()