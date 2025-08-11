const { neon } = require('@neondatabase/serverless');
const fetch = require('node-fetch');

// Configure your Neon database connection
// You'll need to set your DATABASE_URL environment variable
const sql = neon(process.env.DATABASE_URL);

async function fetchRosterData() {
  const url = 'https://api.sleeper.app/v1/league/1257449367455944704/rosters';
  
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching roster data:', error);
    throw error;
  }
}

async function seedDatabase() {
  try {
    console.log('Fetching roster data from Sleeper API...');
    const rosters = await fetchRosterData();
    console.log(`Fetched ${rosters.length} rosters`);

    // Create the table if it doesn't exist
    const schemaSQL = `
      CREATE TABLE IF NOT EXISTS sleeper_rosters (
        id SERIAL PRIMARY KEY,
        roster_id INTEGER NOT NULL,
        league_id VARCHAR(50) NOT NULL,
        owner_id VARCHAR(50) NOT NULL,
        players JSONB,
        starters JSONB,
        keepers JSONB,
        reserve JSONB,
        taxi JSONB,
        co_owners JSONB,
        metadata JSONB,
        player_map JSONB,
        wins INTEGER DEFAULT 0,
        losses INTEGER DEFAULT 0,
        ties INTEGER DEFAULT 0,
        fpts DECIMAL(10, 2) DEFAULT 0,
        total_moves INTEGER DEFAULT 0,
        waiver_position INTEGER,
        waiver_budget_used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(league_id, roster_id)
      );
      
      CREATE INDEX IF NOT EXISTS idx_sleeper_rosters_league_id ON sleeper_rosters(league_id);
      CREATE INDEX IF NOT EXISTS idx_sleeper_rosters_owner_id ON sleeper_rosters(owner_id);
      CREATE INDEX IF NOT EXISTS idx_sleeper_rosters_roster_id ON sleeper_rosters(roster_id);
    `;

    await sql(schemaSQL);
    console.log('Table schema created/verified');

    // Clear existing data for this league (optional - remove if you want to keep historical data)
    await sql`DELETE FROM sleeper_rosters WHERE league_id = '1257449367455944704'`;
    console.log('Cleared existing data for this league');

    // Insert each roster
    for (const roster of rosters) {
      const insertSQL = `
        INSERT INTO sleeper_rosters (
          roster_id,
          league_id,
          owner_id,
          players,
          starters,
          keepers,
          reserve,
          taxi,
          co_owners,
          metadata,
          player_map,
          wins,
          losses,
          ties,
          fpts,
          total_moves,
          waiver_position,
          waiver_budget_used
        ) VALUES (
          ${roster.roster_id},
          ${roster.league_id},
          ${roster.owner_id},
          ${JSON.stringify(roster.players)},
          ${JSON.stringify(roster.starters)},
          ${JSON.stringify(roster.keepers)},
          ${JSON.stringify(roster.reserve)},
          ${JSON.stringify(roster.taxi)},
          ${JSON.stringify(roster.co_owners)},
          ${JSON.stringify(roster.metadata)},
          ${JSON.stringify(roster.player_map)},
          ${roster.settings.wins},
          ${roster.settings.losses},
          ${roster.settings.ties},
          ${roster.settings.fpts},
          ${roster.settings.total_moves},
          ${roster.settings.waiver_position},
          ${roster.settings.waiver_budget_used}
        )
        ON CONFLICT (league_id, roster_id) 
        DO UPDATE SET
          owner_id = EXCLUDED.owner_id,
          players = EXCLUDED.players,
          starters = EXCLUDED.starters,
          keepers = EXCLUDED.keepers,
          reserve = EXCLUDED.reserve,
          taxi = EXCLUDED.taxi,
          co_owners = EXCLUDED.co_owners,
          metadata = EXCLUDED.metadata,
          player_map = EXCLUDED.player_map,
          wins = EXCLUDED.wins,
          losses = EXCLUDED.losses,
          ties = EXCLUDED.ties,
          fpts = EXCLUDED.fpts,
          total_moves = EXCLUDED.total_moves,
          waiver_position = EXCLUDED.waiver_position,
          waiver_budget_used = EXCLUDED.waiver_budget_used,
          updated_at = CURRENT_TIMESTAMP
      `;

      await sql(insertSQL);
      console.log(`Inserted/Updated roster ${roster.roster_id} for owner ${roster.owner_id}`);
    }

    console.log('Database seeding completed successfully!');
    
    // Verify the data was inserted
    const count = await sql`SELECT COUNT(*) FROM sleeper_rosters WHERE league_id = '1257449367455944704'`;
    console.log(`Total rosters in database for this league: ${count[0].count}`);

  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
}

// Run the seeding function
seedDatabase();