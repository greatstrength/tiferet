# Group 5: source-contract efficacy, not a new tester API

Conclusion: retain the original Ly pytest guards. Existing callable execution can express real signature and annotation observations, but the measured source-string/AST-dump candidates are not equivalent replacements. No inspect/AST product API, new YAML syntax, runtime change, default-suite retirement or consumer-source edit is introduced.

## Pinned inputs and boundaries

Build experiment parent: 8730307817d66bd410e6012d91e72d5620cac7cb, the two-file Group 4 review-fix continuation of frozen f3cbc03478d9f6379d8db7d19bceab6e9e43cb22. Actual Ly input: 230047b81bdc8594098b3992a0a95bda30f65724. The executable report checks both the actual Git HEAD and absence of tracked changes. Togusa's source-contract-checks draft recommends efficacy evaluation before adding inspection machinery; this experiment tests that proposal rather than presuming API approval.

The subjects fixture exposes actual LexText.execute, LayoutProfileView, LayoutFilter.apply and raw layout source. It does not calculate assertion verdicts, classify imports or normalize contracts for YAML. Fixed Python experiment code constructs source-derived AST mutants in copied namespaces; source-import mutants are parsed but never executed. No YAML eval, callbacks or user-supplied mutation program is added. The original native pytest functions are loaded directly and run with temporary in-memory substitutions. A dedicated regression proves restoration of actual callable/class identities, Path.read_text and source bytes.

## Six baseline YAML candidates

| Candidate | Execute steps | Assertions | What it actually proves |
| --- | ---: | ---: | --- |
| signature_names | 5 | 1 | Exact seven LexText.execute parameter names/order only. |
| signature_exact | 10 | 3 | Those names plus text kind POSITIONAL_OR_KEYWORD and rewrites default None. |
| annotation_fields | 6 | 1 | Exact eight protocol annotation field names only. |
| annotation_exact | 12 | 2 | Those names plus apply's profile annotation object identity. |
| source_substring | 2 | 1 | Raw source lacks the literal tiferet_ly.domain. |
| source_ast_patterns | 6 | 3 | ast.dump lacks three literal ImportFrom/alias patterns. |

These are 328 lines of expanded YAML for six baseline cases, without hiding observations in a verdict helper. The exact-signature candidate is intentionally narrower in subject scope but stricter about all parameter names than the original LexText guard, which constrains text's position/kind and the rewrites default plus forwarding behavior. Neither signature candidate replaces LexerService/ParserService public-surface guards, parse signature.bind, function metadata checks or behavioral forwarding. The annotation candidate omits the original Protocol MRO/_is_protocol, domain non-inheritance and public-export checks. These residuals are not alleged runtime impossibilities: adding more reflection steps would increase coupling and maintenance, not establish an economic case for moving the guards.

## Measured drift matrix

P means the guard passes; F means it rejects. Every candidate has a passing real-source baseline. Rows record the actual original native guard first, then the two candidates in the order named above. The 15-row experiment produces 45 measured verdicts, including three positive family baselines, ten contract-drift mutants and two benign-source controls. results.json is generated, not inferred from red test output.

| Family/mode | Native | Weak YAML | Stronger YAML |
| --- | --- | --- | --- |
| signature/baseline | P | P | P |
| signature/signature_order | F | F | F |
| signature/signature_kind | F | P | F |
| signature/signature_default | F | P | F |
| annotation/baseline | P | P | P |
| annotation/annotation_identity | F | P | F |
| annotation/protocol_field | F | F | F |
| source/baseline | P | P | P |
| source/import_absolute | F | F | F |
| source/import_relative | F | P | F |
| source/import_relative_child | F | P | P |
| source/import_alias | F | F | F |
| source/import_from_root | P | P | P |
| source/comment_only | P | F | P |
| source/ast_literal_only | P | P | F |

The stronger signature and annotation candidates kill all five selected corresponding mutants, but do not prove the unmodeled native predicates. Raw-source matching misses both relative imports and falsely rejects a comment. AST-dump substring matching misses the relative child import and falsely rejects a harmless string constant containing AST-looking text. An actual traversal could be expressed through additional generic calls or a Python helper, but the latter would put the real guard back in Python under a YAML wrapper; neither is implemented or represented as achieved equivalence here.

The original native source guard itself misses `from tiferet_ly import domain as hidden_domain`: tests/utils/test_layout.py:506 collects ImportFrom.module but not its imported aliases, so it sees only tiferet_ly. This is a reproduced limitation of that original guard, not permission to weaken another guard or silently fix the consumer. Its baseline must be retained and any improvement considered separately. Runtime imported-name checks in test_translation/test_reader are distinct from AST source-import policy and are not claimed equivalent to it.

## Reproduction and fresh validation

Activate the existing Ly-capable project virtual environment, set LY_ROOT to the clean pinned Ly checkout, and run from this build worktree. Measured environment: Python 3.13.5, pytest 9.2.0, Pydantic 2.14.3, PyYAML 6.0.3 and existing PLY. No dependency installation was needed.

```sh
export PYTHONPATH="$PWD:$LY_ROOT"
python -m pytest -q experiments/source_contract_efficacy/tests
python -m experiments.source_contract_efficacy.evaluate > experiments/source_contract_efficacy/results.json
python -m pytest -q experiments/tester_efficacy/consumer_ly/tests
```

Fresh results: 17 source-contract experiment tests pass, including the six-case public YAML entrypoint and explicit restoration regression; prior Ly consumer tests 10 pass; eight original representative Ly guards pass unchanged. The existing core virtual environment runs default pytest: 1379 pass with seven existing warnings; with LY_ROOT on PYTHONPATH the prior core efficacy suite has 93 pass. The PyTables-capable environment runs prior H5 regressions: nine pass. The first core-efficacy invocation omitted the Ly import path and had one collection error; the corrected command passes all 93. One initial native-node selection used an incorrect test name; the corrected eight actual node IDs pass.

The full YAML regression is executed via run_test_module for each existing tests/*.py counterpart, in the Ly/PyTables-capable environments as appropriate, checking every report outcome and failures. Deduplicated union: 76 modules, 1269 passed, zero failed; original released suites remain 69 modules/1248 cases, prior build experiments add six modules/15 cases, and this group adds one module/six cases. Contexts remain 245 and blueprints 78. Ly-environment subset: 75 modules/1267; H5 subset: 74 modules/1259; their overlapping reports agree exactly. No count is inferred from parsed YAML inventory alone.

Recommendation: keep the source/signature pytest guards as focused structural contracts; retain the executable experiment as evidence, not a migration mandate. No new dialect or source inspection API is justified by these results. Any strengthening of the native import-alias blind spot, further YAML reflection expansion or guard retirement requires a separate decision. The product runtime and the frozen Group 4 review worktree remain unchanged.

- major@grokbot via tif-ai
