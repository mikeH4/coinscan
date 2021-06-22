# Query 1
EXPLAIN ANALYZE SELECT
    tokens.address,
    tokens.name,
    tokens.symbol,
    token_meta.source_verified AS source_verified,
    token_meta.holders AS holders,
    token_meta.block_time AS created,
    listings.listings AS listings,
    address_labels.labels AS labels
FROM tokens
LEFT JOIN (
    SELECT
        listings.token,
        string_agg(listings.platform, ',') AS listings
    FROM listings
    GROUP BY listings.token
) as listings ON tokens.address = listings.token
LEFT JOIN token_meta ON tokens.address = token_meta.address
LEFT JOIN (
    SELECT
        address_labels.address,
        string_agg(address_labels.label, ',') AS labels
    FROM address_labels
    GROUP BY address_labels.address
) as address_labels ON token_meta.creator = address_labels.address
LEFT JOIN listings as listings_full ON listings_full.token = tokens.address
WHERE
(
    (
        platform = 'coingecko' AND
        local_slug = 'safemoon'
    ) OR
    tokens.address IN (
        '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82'
    )
)

# Query 2

EXPLAIN ANALYZE SELECT
    tokens.address,
    tokens.name,
    tokens.symbol,
    token_meta.source_verified AS source_verified,
    token_meta.holders AS holders,
    token_meta.block_time AS created,
    listings.listings AS listings,
    address_labels.labels AS labels
FROM tokens
LEFT JOIN (
    SELECT
        listings.token,
        string_agg(listings.platform, ',') AS listings
    FROM listings
    GROUP BY listings.token
) as listings ON tokens.address = listings.token
LEFT JOIN token_meta ON tokens.address = token_meta.address
LEFT JOIN (
    SELECT
        address_labels.address,
        string_agg(address_labels.label, ',') AS labels
    FROM address_labels
    GROUP BY address_labels.address
) as address_labels ON token_meta.creator = address_labels.address
LEFT JOIN listings as listings_full ON listings_full.token = tokens.address
WHERE
(
    tokens.address IN (
        '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82'
    )
    OR tokens.address IN (
        SELECT
            listings.token
        FROM listings
        WHERE (
            platform = 'coingecko' AND
            local_slug = 'safemoon'
        )
    )
)