# EXPLAIN ANALYZE Index Comparison

Query: SELECT * FROM scan_events WHERE parent_id = 7;

## Before index
- Plan: Sequential Scan
- Rows matched: 2
- Rows removed: 138
- Execution time: 0.084 ms

## After index
- Plan: Index Scan
- Index: idx_scan_events_parent_id
- Rows matched: 2
- Execution time: 0.050 ms

## Conclusion
The index helped PostgreSQL locate matching rows. These timings are illustrative because the dataset is small.
