ALTER TABLE collectible_tokens ADD COLUMN token_uri VARCHAR;
ALTER TABLE collectible_tokens DROP COLUMN misc;
ALTER TABLE fungible_collectibles ADD COLUMN description VARCHAR;
