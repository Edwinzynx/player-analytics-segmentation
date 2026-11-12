# Native validation

Power BI Desktop 2.159.1231.0 (26.10)+e4e91b9abb6398be07a5422da513c1d5954994c0; analysis engine 17.0.93.23. Refreshed the generated embedded snapshot and executed 9 DAX queries; 1109 field comparisons matched independent pandas expectations recorded in metrics.powerbi.validation_expected.

Checks cover all measures, tier/cohort/decile groups, cumulative shares under cohort filters, and version-filter replacement for arm contrasts. Microsoft JSON schemas validate the report definitions; the installed Microsoft TMDL serializer parses the model.

Visual rendering and interactive click behavior were not reviewed: both available computer-use runtimes failed to initialize before window capture. Open the project, refresh, and inspect each page before presenting it.

Recheck: open the generated project in Desktop, then run `pwsh -File scripts/validate_powerbi.ps1`, followed by `python scripts/powerbi_validation.py`. The script only refreshes the specifically identified local project.
