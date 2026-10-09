import sys
import run

CHECKS = (
    [("tuza_degree10_global_root_check.py",)]
    + run.CASES["subcubic"]
    + run.CASES["c4"]
    + run.CASES["c5"]
    + run.CASES["c9"]
    + run.CASES["c6"][:2]
    + run.CASES["c6"][3:]
    + run.CASES["c7"][:2]
    + run.CASES["c8"][:1]
    + [("tuza_degree10_c9_check.py",)]
)


def main():
    if sys.argv[1:] == ["--list"]:
        for command in CHECKS:
            print(" ".join(command))
        return
    run.CASES["paper-alignment"] = CHECKS
    sys.argv[1:1] = ["--case", "paper-alignment"]
    run.main()


if __name__ == "__main__":
    main()
