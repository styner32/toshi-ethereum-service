ALTER TABLE collectible_transfer_events ADD COLUMN collectible_address VARCHAR;
UPDATE collectible_transfer_events SET collectible_address = contract_address;
ALTER TABLE collectible_transfer_events ALTER COLUMN indexed_arguments SET DEFAULT ARRAY[TRUE, TRUE, FALSE];

CREATE INDEX IF NOT EXISTS idx_collectible_transfer_events_collectible_address ON collectible_transfer_events (collectible_address);
