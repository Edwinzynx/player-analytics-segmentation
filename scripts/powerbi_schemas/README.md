# Microsoft Power BI schemas

Unmodified schema contents from Microsoft's public schema endpoint, vendored for
offline validation. `sources.json` records the exact URLs. Formatting is normalized
by `scripts/fetch_powerbi_schemas.py`; schema identifiers and constraints are retained.
The visual configuration schema has a different `$id` spelling from its download
URL; the offline registry registers both identifiers.

Upstream: https://github.com/microsoft/json-schemas
License: https://github.com/microsoft/json-schemas/blob/main/LICENSE

The schema check covers report JSON structure, not rendered appearance or runtime
visual capabilities. Native model/DAX validation is recorded separately.
