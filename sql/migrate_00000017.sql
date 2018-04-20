ALTER TABLE collectibles ADD COLUMN image_url_format_string VARCHAR;

CREATE TABLE IF NOT EXISTS fungible_collectibles (
    contract_address VARCHAR PRIMARY KEY,
    collectible_address VARCHAR,
    name VARCHAR,
    token_uri VARCHAR,
    creator_address VARCHAR,
    image VARCHAR,
    last_block INTEGER DEFAULT 0,
    ready BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS fungible_collectible_balances (
    contract_address VARCHAR,
    owner_address VARCHAR,
    balance VARCHAR,

    PRIMARY KEY (contract_address, owner_address)
);
