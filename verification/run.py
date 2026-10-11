import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import time
import urllib.request
import zipfile
from derive_c4_input import derive


ARCHIVE_SHA256 = "1c91ac287d56c46065c432fbc6a98835cfe50240b229ade07adc830f04429a5a"
ARCHIVE_URL = "https://raw.githubusercontent.com/Amkan2026/tuza-degree-ten/main/archive/verification.zip"
REPLAY = Path(__file__).resolve().parents[1] / ".replay"
CASES = {
    "subcubic": [("tuza_degree10_subcubic_link_basis_check.py",)],
    "c4": [("tuza_degree10_c4_old_transfer_check.py",),
           ("tuza_degree10_c4_final_independent.py",),
           ("tuza_degree10_c4_side_independent_check.py",)],
    "c5": [("tuza_degree10_c5_independent_check.py", "work/tuza_degree10_c5_seven_ten_complete.json", "work/replay_c5_7_10.json"),
           ("tuza_degree10_c5_independent_check.py", "work/tuza_degree10_c5_eight_ten_complete.json", "work/replay_c5_8_10.json"),
           ("tuza_degree10_c5_packed_independent_check.py", "work/tuza_degree10_c5_nine_ten_compressed.json", "work/replay_c5_9_10.json"),
           ("tuza_degree10_c5_packed_independent_check.py", "work/tuza_degree10_c5_ten_ten_compressed.json", "work/replay_c5_10_10.json"),
           ("tuza_degree10_c5_h0_human_templates.py",),
           ("tuza_degree10_c5_h0_nontriangle_human.py",),
           ("tuza_degree10_c5_saturated_edge_independent.py", "work/tuza_degree10_c5_h3_edge_intervals.json", "work/replay_c5_h3.json"),
           ("tuza_degree10_c5_star_independent.py",)],
    "c6": [("tuza_degree10_c6_fresh_source_replay.py",),
           ("tuza_degree10_c6_dense_uncovered.py",),
           ("tuza_degree10_c6_complete_fast_check.py", "--source", "tuza_degree10_c6_merged_certificates.json", "--report", "replay_c6_coverage.json"),
           ("tuza_degree10_c6_K24_private_edges_human_check.py",),
           ("tuza_degree10_c6_K24_one_private_edge_human_check.py",),
           ("tuza_degree10_c6_K24_full_leaf_human_check.py",),
           ("tuza_degree10_c6_K24_two_leaf_human_check.py",)],
    "c7": [("tuza_degree10_c7_core_check.py",),
           ("tuza_degree10_c7_side_check.py",),
           ("tuza_degree10_c7_check.py", "work/tuza_degree10_c7_compressed_certificates.json")],
    "c8": [("tuza_degree10_c8_core_check.py",),
           ("tuza_degree10_c8_residual_check.py",)],
    "c9": [("tuza_degree10_c9_full_children_check.py",)],
}
PORTABILITY = '''import os
from pathlib import Path
import subprocess
import sys

OriginalPopen = subprocess.Popen

class PortablePopen(OriginalPopen):
    def __init__(self, args, *rest, **options):
        if isinstance(args, (list, tuple)):
            args = list(args)
            commands = {"/opt/homebrew/bin/geng": "TUZA_GENG", "/opt/homebrew/bin/labelg": "TUZA_LABELG", "/usr/bin/clang": "TUZA_CC"}
            key = commands.get(str(args[0]))
            if key and os.environ.get(key):
                args[0] = os.environ[key]
            if sys.platform != "darwin" and "-dynamiclib" in args:
                index = args.index("-dynamiclib")
                args[index:index + 1] = ["-shared", "-fPIC"]
        super().__init__(args, *rest, **options)

subprocess.Popen = PortablePopen
'''


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def archive_path(supplied):
    bundled = Path(__file__).resolve().parents[1] / "archive/verification.zip"
    archive = Path(supplied).expanduser().resolve() if supplied else bundled if bundled.is_file() else REPLAY / "verification.zip"
    if not archive.is_file():
        if supplied:
            raise FileNotFoundError(archive)
        archive.parent.mkdir(parents=True, exist_ok=True)
        temporary = archive.with_suffix(".download")
        print("Downloading the verification archive", flush=True)
        urllib.request.urlretrieve(ARCHIVE_URL, temporary)
        if digest(temporary) != ARCHIVE_SHA256:
            temporary.unlink()
            raise ValueError("The downloaded archive has the wrong SHA256")
        temporary.replace(archive)
    if digest(archive) != ARCHIVE_SHA256:
        raise ValueError("The archive has the wrong SHA256")
    return archive


def extract(archive, target):
    with zipfile.ZipFile(archive) as source:
        names = set()
        for entry in source.infolist():
            path = PurePosixPath(entry.filename)
            if path.is_absolute() or ".." in path.parts or "\\" in entry.filename or stat.S_ISLNK(entry.external_attr >> 16):
                raise ValueError(f"Unsafe archive entry: {entry.filename}")
            if entry.filename in names:
                raise ValueError(f"Duplicate archive entry: {entry.filename}")
            names.add(entry.filename)
        disk_root = target
        while not disk_root.exists():
            disk_root = disk_root.parent
        required = sum(entry.file_size for entry in source.infolist()) + 96 * 1024 * 1024
        if shutil.disk_usage(disk_root).free < required:
            raise RuntimeError(f"Replay needs at least {required // (1024 * 1024)} MiB of available disk space")
        source.extractall(target)
    with zipfile.ZipFile(target / "outputs/tuza_degree9_verification.zip") as older:
        for name in ("tuza_degree9_c4_side_direct7_audit.txt", "tuza_degree9_c4_side_direct8_audit.txt", "tuza_degree9_c4_side_direct9.txt"):
            member = "work/" + name
            (target / member).write_bytes(older.read(member))
    restoration = derive(target)
    (target / "c4_restoration.json").write_text(json.dumps(restoration, indent=2) + "\n")


def executable(value, names):
    if value:
        path = shutil.which(value)
        if not path:
            raise FileNotFoundError(f"Executable not found: {value}")
        return path
    return next((path for name in names if (path := shutil.which(name))), "")


def environment(args, wrapper):
    result = os.environ.copy()
    result.pop("PYTHONOPTIMIZE", None)
    result["PYTHONPATH"] = str(wrapper) + (os.pathsep + result["PYTHONPATH"] if result.get("PYTHONPATH") else "")
    result["TUZA_GENG"] = executable(args.geng, ("geng", "nauty-geng", "/opt/homebrew/bin/geng"))
    result["TUZA_LABELG"] = executable(args.labelg, ("labelg", "nauty-labelg", "/opt/homebrew/bin/labelg"))
    result["TUZA_CC"] = executable(args.cc, ("clang", "cc"))
    return result


def preserve(snapshot, baseline, target):
    changed = []
    for path in snapshot.rglob("*"):
        if path.is_file():
            name = path.relative_to(snapshot)
            value = digest(path)
            if baseline.get(str(name)) != value:
                saved = target / name
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, saved)
                changed.append({"path": str(name), "sha256": value})
    return changed


def execute(command, snapshot, environment, log):
    print("Running " + command[1], flush=True)
    with log.open("a") as output:
        output.write(" ".join(command) + "\n")
        output.flush()
        process = subprocess.Popen(command, cwd=snapshot, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="", flush=True)
            output.write(line)
        result = process.wait()
    if result:
        raise subprocess.CalledProcessError(result, command)


def main():
    if sys.flags.optimize:
        raise RuntimeError("Run Python without -O or -OO. The checkers require assertions.")
    parser = argparse.ArgumentParser(description="Replay finite checks for Lemma 3.1 and the codegree cases.")
    parser.add_argument("--archive", help="Use a local verification.zip instead of downloading it")
    parser.add_argument("--case", nargs="+", choices=[*CASES, "all"], help="Rerun selected case checks instead of the saved-report check")
    parser.add_argument("--geng", help="Path or command name for nauty geng")
    parser.add_argument("--labelg", help="Path or command name for nauty labelg")
    parser.add_argument("--cc", help="Path or command name for a C compiler")
    parser.add_argument("--keep-work", action="store_true", help="Keep each full extracted workspace after a successful check")
    args = parser.parse_args()
    archive = archive_path(args.archive)
    selected = list(CASES) if args.case and "all" in args.case else list(dict.fromkeys(args.case or []))
    commands = [item for case in selected for item in CASES[case]] if selected else [("tuza_degree10_global_root_check.py",)]
    if selected and importlib.util.find_spec("numpy") is None:
        raise RuntimeError("Install dependencies with python3 -m pip install -r verification/requirements.txt")
    run = REPLAY / (time.strftime("run_%Y%m%d_%H%M%S") + "_" + str(os.getpid()))
    wrapper = run / "platform"
    wrapper.mkdir(parents=True)
    (wrapper / "sitecustomize.py").write_text(PORTABILITY)
    env = environment(args, wrapper)
    if any(case in selected for case in ("subcubic", "c4", "c6", "c7", "c8", "c9")) and not env["TUZA_GENG"]:
        raise RuntimeError("Install nauty or provide --geng")
    if "c9" in selected and not env["TUZA_LABELG"]:
        raise RuntimeError("Install nauty or provide --labelg")
    if "c6" in selected and not env["TUZA_CC"]:
        raise RuntimeError("Provide a C compiler with --cc")
    receipt = {"archive_sha256": ARCHIVE_SHA256, "cases": selected or ["saved"], "steps": []}
    try:
        for number, command in enumerate(commands, 1):
            step = run / f"{number:02d}_{Path(command[0]).stem}"
            snapshot = step / "snapshot"
            extract(archive, snapshot)
            originals = step / "saved_reports"
            originals.mkdir(parents=True)
            shutil.copy2(snapshot / "c4_restoration.json", step / "c4_restoration.json")
            for report in (snapshot / "work").glob("*verified.json"):
                shutil.copy2(report, originals / report.name)
            log = step / "replay.log"
            execute([sys.executable, "work/tuza_degree10_restore_inputs.py"], snapshot, env, log)
            baseline = {str(path.relative_to(snapshot)): digest(path) for path in snapshot.rglob("*") if path.is_file()}
            execute([sys.executable, "work/" + command[0], *command[1:]], snapshot, env, log)
            changed = preserve(snapshot, baseline, step / "new_reports")
            if not args.keep_work:
                shutil.rmtree(snapshot)
            receipt["steps"].append({"script": command[0], "result": "PASS", "directory": str(step.relative_to(run)), "outputs": changed})
            (run / "replay.json").write_text(json.dumps(receipt, indent=2) + "\n")
    except BaseException:
        receipt["result"] = "FAIL"
        (run / "replay.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print("Replay stopped. Logs and files remain in " + str(run), flush=True)
        raise
    receipt["result"] = "PASS"
    (run / "replay.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print("PASS. Reports and logs: " + str(run), flush=True)


if __name__ == "__main__":
    main()
