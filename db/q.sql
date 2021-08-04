SELECT
    CASE WHEN holders.token IS NOT NULL
        THEN holders.token ELSE pair_holders.token
    END AS token,
    CASE WHEN holders.wallet IS NOT NULL
        THEN holders.wallet ELSE pair_holders.wallet
    END AS wallet,
    holders.supply,
    pair_holders.liquidity
FROM (
    SELECT
        contract AS token,
        holder AS wallet,
        holding AS supply
    FROM holders
    ORDER BY holders.contract ASC
    LIMIT 20000
) AS holders
FULL OUTER JOIN (
    SELECT
        pairs.token AS token,
        holders.holder AS wallet,
        holders.holding AS liquidity
    FROM holders
    JOIN pairs ON pairs.pair = holders.contract
    ORDER BY holders.contract ASC
    LIMIT 20000
) AS pair_holders ON
    pair_holders.token = holders.token AND
    pair_holders.wallet = holders.wallet