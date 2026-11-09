-- Variant 3: Parcel logistics schema
-- Source CSVs: data/variant_3_parcels/tables/

CREATE TABLE IF NOT EXISTS parcels (
    id         INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    status     TEXT NOT NULL,
    category   TEXT NOT NULL,
    created_at DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS hubs (
    id        INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL REFERENCES parcels(id),
    label     TEXT NOT NULL,
    amount    NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS scan_events (
    id          INTEGER PRIMARY KEY,
    parent_id   INTEGER NOT NULL REFERENCES hubs(id),
    event       TEXT NOT NULL,
    happened_at DATE NOT NULL
);

-- Indexes support joins through the parent relationships.
CREATE INDEX IF NOT EXISTS idx_hubs_parent_id
    ON hubs(parent_id);

CREATE INDEX IF NOT EXISTS idx_scan_events_parent_id
    ON scan_events(parent_id);
