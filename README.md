# Tuza’s conjecture for graphs of maximum degree ten

Code and certificates for the finite checks in the degree ten proof. 
## Code

| Part of the proof | Sources |
| --- | --- |
| Lemma 3.1 — subcubic links | [lemma-3.1](verification/lemma-3.1/) |
| Common neighborhood of size 4 | [codegree-4](verification/cases/codegree-4/) |
| Common neighborhood of size 5 | [codegree-5](verification/cases/codegree-5/) |
| Common neighborhood of size 6 | [codegree-6](verification/cases/codegree-6/) |
| Common neighborhood of size 7 | [codegree-7](verification/cases/codegree-7/) |
| Common neighborhood of size 8 | [codegree-8](verification/cases/codegree-8/) |
| Common neighborhood of size 9 | [codegree-9](verification/cases/codegree-9/) |
| Input restoration and scope checks | [shared](verification/shared/) |
| Earlier degree bounds used in the checks | [inherited](verification/inherited/) |
| Certificate construction and search | [search](verification/search/) |

The [case index](verification/index.md) identifies the checkers, inputs and reports for each part. Search programs construct certificates. Verification programs check the recorded domains and witnesses.

The visible source copies omit comments and docstrings. Their algorithms agree with the archived sources, as recorded in [normalization.json](verification/normalization.json). Run the checks through `verification/run.py` to restore the required inputs and paths.

## Run

Use Python 3.10 or later without `-O` or `-OO`. The saved scope check uses the standard library:

```sh
python3 verification/run.py
```

This checks the saved reports and their input bindings for all forty endpoint degree pairs. It does not repeat the enumerations.

Fresh checks use NumPy. Some cases also require nauty and a C compiler. The [replay instructions](verification/replay.md) list the requirements.

```sh
python3 -m pip install -r verification/requirements.txt
python3 verification/run.py --case subcubic
python3 verification/run.py --case c4
```

Use `subcubic` for Lemma 3.1, `c4` through `c9` for the corresponding cases, or `all` for every case. The runner saves logs and new reports under `.replay/` and removes successful workspaces. Use `--keep-work` to retain them.

## Data and checks

[archive/verification.zip](archive/verification.zip) contains the frozen sources, inputs, certificates and reports required by the replay. It omits manuscripts and editorial files. [archive-provenance.json](verification/archive-provenance.json) records the removals and retained file hashes.

[validation.json](verification/validation.json) records the independent replays. [runner-validation.json](verification/runner-validation.json) records packaging and runner checks. These records distinguish fresh calculations from checks of saved reports. The code verifies finite steps of the proof and relies on its stated mathematical lemmas.

[CITATION.cff](CITATION.cff) gives the software citation. [THIRD_PARTY.md](THIRD_PARTY.md) records attribution for retained third party material.
