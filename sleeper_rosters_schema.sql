-- Create table for Sleeper league rosters
CREATE TABLE IF NOT EXISTS sleeper_rosters (
    id SERIAL PRIMARY KEY,
    roster_id INTEGER NOT NULL,
    league_id VARCHAR(50) NOT NULL,
    owner_id VARCHAR(50) NOT NULL,
    
    -- Player arrays stored as JSONB for flexibility
    players JSONB,
    starters JSONB,
    keepers JSONB,
    reserve JSONB,
    taxi JSONB,
    
    -- Co-owners and metadata
    co_owners JSONB,
    metadata JSONB,
    player_map JSONB,
    
    -- Settings
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    ties INTEGER DEFAULT 0,
    fpts DECIMAL(10, 2) DEFAULT 0,
    total_moves INTEGER DEFAULT 0,
    waiver_position INTEGER,
    waiver_budget_used INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicate rosters
    UNIQUE(league_id, roster_id)
);

-- Create indexes for better query performance
CREATE INDEX idx_sleeper_rosters_league_id ON sleeper_rosters(league_id);
CREATE INDEX idx_sleeper_rosters_owner_id ON sleeper_rosters(owner_id);
CREATE INDEX idx_sleeper_rosters_roster_id ON sleeper_rosters(roster_id);

-- Create a trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_sleeper_rosters_updated_at BEFORE UPDATE
    ON sleeper_rosters FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();