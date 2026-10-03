import argparse
def main(argv=None):
    """Run evaluation with a reproducible seed."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.parse_args(argv)
    raise NotImplementedError("TODO(Harshit): implement evaluation run")
if __name__ == "__main__": main()
