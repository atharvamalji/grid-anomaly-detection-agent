# BI Export (Power BI / Tableau)

Deferred — planned approach documented here for when implemented.

External BI tools connect directly to a read-only view/table in the
backend database (e.g. `anomalies_bi_view` in `backend/grid_agent/db/`),
rather than through a bespoke export API. This is simpler and more
idiomatic for how Power BI and Tableau consume tabular data:

- Power BI: native Postgres/SQLite connector against the read-only view.
- Tableau: native database connector, same view.

The project's own Next.js dashboard remains the primary UX for
investigating a specific anomaly (agent explanation + citations); BI
tools are for trend/aggregate analysis across anomaly history over time.
