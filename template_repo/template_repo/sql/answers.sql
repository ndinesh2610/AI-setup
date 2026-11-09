-- Variant 3: Parcel SQL exercises

-- 1. First 10 active parcels, newest first
SELECT *
FROM parcels
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10;


-- 2. Count parcels per status
SELECT status, COUNT(*) AS parcel_count
FROM parcels
GROUP BY status
ORDER BY parcel_count DESC;


-- 3. Show each hub with its parent parcel name
SELECT
    h.id AS hub_id,
    h.label,
    h.amount,
    p.id AS parcel_id,
    p.name AS parcel_name
FROM hubs h
JOIN parcels p ON p.id = h.parent_id
ORDER BY p.id, h.id;


-- 4. Parcels with more than 2 hubs
SELECT
    p.id,
    p.name,
    COUNT(h.id) AS hub_count
FROM parcels p
JOIN hubs h ON h.parent_id = p.id
GROUP BY p.id, p.name
HAVING COUNT(h.id) > 2
ORDER BY hub_count DESC;


-- 5. Parcels that have no hubs
SELECT p.*
FROM parcels p
LEFT JOIN hubs h ON h.parent_id = p.id
WHERE h.id IS NULL;


-- 6. Total hub amount per label, only totals above 1000
SELECT
    label,
    SUM(amount) AS total_amount
FROM hubs
GROUP BY label
HAVING SUM(amount) > 1000
ORDER BY total_amount DESC;


-- 7. Rank hubs by amount for each parent parcel
SELECT
    parent_id,
    id AS hub_id,
    label,
    amount,
    RANK() OVER (
        PARTITION BY parent_id
        ORDER BY amount DESC
    ) AS amount_rank
FROM hubs
ORDER BY parent_id, amount_rank;


-- 8. Latest scan event for every hub
WITH ranked_events AS (
    SELECT
        se.*,
        ROW_NUMBER() OVER (
            PARTITION BY parent_id
            ORDER BY happened_at DESC, id DESC
        ) AS rn
    FROM scan_events se
)
SELECT
    h.id AS hub_id,
    h.parent_id AS parcel_id,
    re.id AS scan_event_id,
    re.event,
    re.happened_at
FROM hubs h
LEFT JOIN ranked_events re
    ON re.parent_id = h.id
   AND re.rn = 1
ORDER BY h.id;
