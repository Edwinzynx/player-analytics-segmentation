# Data quality report

Raw records: 31,332; accepted: 31,331; quarantined: 1.

Raw SHA-256: f6a85f5f022c7dd2bcf06e16abe7767fa8cb54287089058526f45092ef1d3c52

The exact audited incomplete final row is quarantined. All other violations fail the run.

## Hard checks

Schema, nulls, duplicate identifiers, integer/non-negative domains, valid version and strict binary flags.

Result: PASS on accepted rows

## Raw findings

- nulls: sum_gamerounds
- nulls: retention_1
- nulls: retention_7
- integer dtype/domain: sum_gamerounds
- invalid version
- invalid binary flag: retention_1
- invalid binary flag: retention_7

## Soft warnings

- High-round records exceed the IQR fence; retained.
- Zero-round records have retention flags; retained pending source clarification.
- Raw source is a truncated prefix; population representativeness unverified.

IQR upper fence: 120.00; flagged: 3,491; maximum: 2,961; upper percentile: 1077.68.
Zero-round records with a retention flag: 44.

All valid outliers are retained. See metrics.json/data_quality for dtype and check details.
