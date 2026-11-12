# Native Power BI report

Open `ProductAnalytics.pbip` in current Power BI Desktop. Choose **Home → Refresh**
on first open: the project stores a portable, compressed data snapshot in its M
partitions. No local path editing, credentials, gateway, or online source is needed.
Keep the `.Report` and `.SemanticModel` folders beside the `.pbip` file.

Use the page tabs for performance, experiment inference, and concentration.
Slicers affect descriptive pages. The experiment page has no slicers and disables
cross-visual filtering: its inferential table is a disconnected full-sample snapshot.
Percent-format effect cards display differences in rate units (read as percentage
points); confidence bounds in the inference table use rate units.

Rebuild after changing the analytical inputs:
`python scripts/run_all.py`. Close Desktop before rebuilding; reopen and refresh.
The report is generated from `outputs/bi` and `outputs/metrics.json`. Editing a
generated report is supported, but the next build overwrites generated definitions.
Keep custom layouts in a separate project or edit the Python generator.

The model uses single-direction dimension-to-fact filters. Cohorts are descriptive
retention patterns; segment-specific retention is partly true by construction.
Deciles are fixed full-population rankings. All statistical decisions use Python
outputs; slicers do not produce new tests. The sample is an incomplete local prefix
of the published Cookie Cats file, not a verified representative sample.

No PBIX or cloud publication is required. Desktop's local cache is ignored by Git.
See `validation.md` for actual engine and layout checks.
