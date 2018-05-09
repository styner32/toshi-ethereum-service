ALTER TABLE tokens ADD COLUMN custom BOOLEAN DEFAULT FALSE;
ALTER TABLE token_balances ADD COLUMN name VARCHAR;
ALTER TABLE token_balances ADD COLUMN symbol VARCHAR;
ALTER TABLE token_balances ADD COLUMN decimals INTEGER;
ALTER TABLE token_balances ADD COLUMN visibility INTEGER DEFAULT 1;

CREATE INDEX IF NOT EXISTS idx_token_balance_eth_address_contract_address ON token_balances (eth_address, contract_address);
CREATE INDEX IF NOT EXISTS idx_token_balance_eth_address_visibility_value ON token_balances (eth_address, visibility, value);
