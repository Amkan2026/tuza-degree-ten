# Verification

The source copies are grouped by Lemma 3.1 and the maximum codegree of the selected edge. Comments and leading docstrings have been removed. [normalization.json](normalization.json) records source hashes and equivalence checks. Moving the files into these directories preserves their bytes.

These directories organize the sources for reading. Their imports and working paths retain the archived layout. To run a check, use [run.py](run.py), which extracts the bound original sources into a separate working copy and restores their inputs. The [replay instructions](replay.md) give the commands and dependencies.

## Lemma 3.1

The [subcubic basis check](lemma-3.1/tuza_degree10_subcubic_link_basis_check.py) verifies the finite link classification. The [table check](lemma-3.1/degree10_subcubic_table_check.py) and [root check](lemma-3.1/tuza_book3_condensed_root_check.py) verify its supporting certificates.

## Cases

Here the codegree is the number of common neighbors of the selected edge.

| Codegree | Checks | Fresh replay evidence |
| --- | --- | --- |
| 4 | [Final coverage](cases/codegree-4/tuza_degree10_c4_final_independent.py), [selection bounds](cases/codegree-4/tuza_degree10_c4_selection_independent_check.py), [side census](cases/codegree-4/tuza_degree10_c4_side_independent_check.py) | [Final result and log](reports/public-c4/02_tuza_degree10_c4_final_independent/), [side census](reports/public-c4/03_tuza_degree10_c4_side_independent_check/) |
| 5 | [Certificates](cases/codegree-5/tuza_degree10_c5_independent_check.py), [compressed replay](cases/codegree-5/tuza_degree10_c5_packed_independent_check.py), [fresh catalogue](cases/codegree-5/tuza_degree10_c5_source_independent.cpp) | [Degree 9 and 10](reports/common5_9_10/), [degree 10 and 10](reports/common5_10_10/) |
| 6 | [Complete replay](cases/codegree-6/tuza_degree10_c6_complete_fast_check.py), [literal verifier](cases/codegree-6/tuza_degree10_c6_complete_coverage_check.py), [fresh source replay](cases/codegree-6/tuza_degree10_c6_fresh_source_replay.py) | [All 780 new domains](reports/common6_full_coverage/), [fresh catalogue](reports/common6_fresh_source_and_domains/) |
| 7 | [Full check](cases/codegree-7/tuza_degree10_c7_check.py), [side intervals](cases/codegree-7/tuza_degree10_c7_side_check.py) | [Full coverage](reports/common7_full_coverage/), [side intervals](reports/common7_sides/) |
| 8 | [Residual check](cases/codegree-8/tuza_degree10_c8_residual_check.py), [interval check](cases/codegree-8/tuza_degree10_c8_intervals237_check.py) | [Full coverage](reports/common8_full_coverage/) |
| 9 | [Coverage](cases/codegree-9/tuza_degree10_c9_check.py), [all child deletions](cases/codegree-9/tuza_degree10_c9_full_children_check.py) | [Coverage](reports/common9_full_coverage/), [child deletions](reports/common9_full_children/) |

Each case directory also contains its subsidiary certificate checks. The runner uses a separate copy for each command, so regenerated reports cannot change another check's frozen inputs. Certificate checks verify the witnesses directly and do not use a solver's negative answers.

## Shared and inherited checks

The [global root check](shared/tuza_degree10_global_root_check.py) checks the saved bindings and forty endpoint degree pairs. The default command runs this check without repeating the enumerations. Its [code-only archive result](reports/code-only/saved/) records the final packaged archive.

[Shared sources](shared/) contain the global checks and input restoration. [Inherited sources](inherited/) contain the degree eight and nine checks. The runner restores the earlier certificates and three C4 side inputs with their recorded hashes.

[Search and generation sources](search/) preserve certificate construction. They are not replay entry points. Some retain temporary working paths from those runs. Search programs using a solver need OR-Tools in addition to the replay dependencies.

[validation.json](validation.json) distinguishes fresh recomputation from checks of saved records and links the reports and logs. The human reductions remain mathematical premises of the certificate checks.
