# Lemma 3.1

These commands replay the computational supplement to Lemma 3.1. The case index follows the common neighborhood size.

Use Python 3.10 or newer. Install the Python dependency from the repository root:

```sh
python3 -m pip install -r verification/requirements.txt
```

Run the saved-report check:

```sh
python3 verification/run.py
```

The runner uses the bundled [verification archive](../archive/verification.zip), checks its SHA256, restores the older inputs, and checks all forty endpoint degree pairs and their source bindings. If the bundled archive is absent, the runner downloads the same file from GitHub. This command checks the saved results. It does not rerun the full enumerations.

For a downloaded copy of the archive, use:

```sh
python3 verification/run.py --archive /path/to/verification.zip
```

The expected SHA256 is:

```text
1c91ac287d56c46065c432fbc6a98835cfe50240b229ade07adc830f04429a5a
```

## Fresh checks

Select the codegree case to rerun:

```sh
python3 verification/run.py --case subcubic
python3 verification/run.py --case c4
python3 verification/run.py --case c5
python3 verification/run.py --case c6
python3 verification/run.py --case c7
python3 verification/run.py --case c8
python3 verification/run.py --case c9
```

`subcubic` rechecks the link classification in Lemma 3.1. Cases `c4` through `c9` replay the saved certificate domains and coverage. Case `c6` also recompiles and reruns the raw domain and density checks. Case `c9` regenerates the nine-vertex graph census and checks all canonical vertex deletions. These commands verify the computational premises. The manuscript contains the mathematical reductions.

You can select several cases or all of them:

```sh
python3 verification/run.py --case c4 c5
python3 verification/run.py --case all
```

The subcubic, C4, C6, C7, C8, and C9 checks need nauty's `geng`. C9 also needs `labelg`, and C6 needs a C compiler. The runner searches the executable path and accepts explicit locations:

```sh
python3 verification/run.py --case c6 --geng /path/to/geng --cc /path/to/clang
python3 verification/run.py --case c9 --geng /path/to/geng --labelg /path/to/labelg
```

The runner redirects the archived macOS executable paths at startup without editing the archived sources. On Linux it replaces the compiler's `-dynamiclib` flag with `-shared -fPIC`. This adaptation preserves the source hashes checked by the archived programs.

Every command runs in a separate copy under `.replay`. The runner preserves its logs, new reports, and copies of the saved reports, then removes successful workspaces. Separate copies prevent one checker's report from changing a later checker's byte bindings. Use `--keep-work` to retain the full workspaces. Failed workspaces remain available for inspection. Full replay can take substantial time.

The runner restores the three omitted C4 side files from the degree-nine archive. It also restores the inherited degree-eight inputs and regenerates the 110 seven-seven witnesses from the archived shared diagrams with [derive_c4_input.py](derive_c4_input.py). The helper checks every packing and cover before writing the derived input. The old-transfer check then verifies that these witnesses cover the inherited side domains.

The shared-diagram source has SHA256 `350ba8ab4d7585a76967eb75f39663a793d6a5fff41c39e91eaec4c6afcf5b80`. The deterministic derived input has SHA256 `a828fc7e90fbc3d0b86f6a0c1d1635db8ab3d536eec10715c7c9c55515ce81c3`. These are derived witnesses rather than a copy of the missing historical file. The [case index](index.md) lists the programs and certificate files for each branch.

Run Python without `-O` or `-OO`. The archived checkers use assertions, and the runner rejects optimized Python.
