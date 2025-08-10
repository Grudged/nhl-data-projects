# NFL Data Seeder Framework

A reusable, flexible framework for seeding any NFL data into NeonDB with minimal configuration.

## 🚀 Quick Start

```python
from nfl_data_seeder import NFLDataSeeder, NFLDataHelpers

# Initialize seeder (uses NeonDB connection automatically)
seeder = NFLDataSeeder()

# Test connection
seeder.test_connection()

# Seed data from API
seeder.seed_data_from_api(
    api_url="https://api.sportsdata.io/v3/nfl/scores/json/Schedules/2025",
    table_name="nfl_schedule_2025", 
    columns={"game_key": "VARCHAR(20) PRIMARY KEY", "away_team": "VARCHAR(10)"}, 
    processor=my_processor_function,
    primary_key="game_key"
)
```

## 📊 Features

- **Automatic NeonDB Connection**: Uses your existing Poke-Project credentials
- **Flexible Data Processing**: Custom processor functions for any data format
- **Upsert Logic**: Automatically handles inserts vs updates
- **Progress Tracking**: Real-time progress display
- **Error Handling**: Continues processing despite individual record errors
- **Helper Functions**: Common data type conversions (int, float, bool, JSON)
- **Multiple Data Sources**: API endpoints or existing data structures

## 🔧 Core Components

### NFLDataSeeder Class

#### Methods:

- `test_connection()` - Test database connectivity
- `create_table(table_name, columns)` - Create table with schema
- `fetch_data_from_api(url, params)` - Fetch data from API endpoint
- `process_data(raw_data, processor)` - Transform data using custom function
- `upsert_data(table_name, data, primary_key)` - Insert/update data
- `seed_data_from_api()` - Complete workflow from API
- `seed_data_from_dict()` - Complete workflow from existing data

### NFLDataHelpers Class

#### Helper Functions:

- `safe_int(value)` - Safely convert to integer
- `safe_float(value)` - Safely convert to float  
- `safe_bool(value)` - Safely convert to boolean
- `json_field(value)` - Convert to JSON string for JSONB storage

## 📚 Examples

### 1. Player Season Stats

```bash
python examples/seed_player_stats.py 2024
```

Seeds comprehensive player statistics including passing, rushing, receiving, and fantasy points.

### 2. Team Season Stats  

```bash
python examples/seed_team_stats.py 2024
```

Seeds team-level statistics including wins/losses, points, yards, turnovers.

### 3. League Standings

```bash
python examples/seed_standings.py 2024
```

Seeds division standings, conference rankings, and playoff positioning.

### 4. Custom Data

```bash
python examples/seed_custom_data.py
```

Shows how to seed your own data (injury reports, depth charts, etc).

## 🛠️ Creating Custom Seeders

### Step 1: Define Your Processor Function

```python
def process_my_data(raw_record):
    \"\"\"Transform raw API data to your desired format\"\"\"
    return {
        "id": NFLDataHelpers.safe_int(raw_record.get('PlayerID')),
        "name": raw_record.get('Name'), 
        "team": raw_record.get('Team'),
        "stats": NFLDataHelpers.json_field(raw_record.get('Stats', {}))
    }
```

### Step 2: Define Your Table Schema

```python
columns = {
    "id": "INTEGER PRIMARY KEY",
    "name": "VARCHAR(100)",
    "team": "VARCHAR(10)", 
    "stats": "JSONB"
}
```

### Step 3: Seed the Data

```python
seeder = NFLDataSeeder()
seeder.seed_data_from_api(
    api_url="https://api.sportsdata.io/v3/nfl/stats/json/PlayerSeasonStats/2024",
    table_name="my_nfl_data",
    columns=columns,
    processor=process_my_data,
    primary_key="id"
)
```

## 🌐 Available SportsDataIO Endpoints

The framework works with any SportsDataIO NFL endpoint. Popular ones include:

### Schedules & Scores
- `/Schedules/{season}` - Full season schedule
- `/Scores/{season}` - Game results
- `/ScoresByWeek/{season}/{week}` - Week-specific scores

### Player Data  
- `/PlayerSeasonStats/{season}` - Season stats by player
- `/Players` - Player profiles and info
- `/PlayerGameStats/{season}/{week}` - Game-by-game stats

### Team Data
- `/TeamSeasonStats/{season}` - Team season statistics  
- `/Standings/{season}` - League standings
- `/Teams` - Team information

### Advanced Stats
- `/FantasyDefenseProjectionsByGame/{season}/{week}` - Fantasy defense
- `/InjuryReports` - Current injury status
- `/News` - Latest NFL news

## 📋 Column Type Reference

Common PostgreSQL column types for NFL data:

```python
columns = {
    # IDs and Keys
    "player_id": "INTEGER PRIMARY KEY",
    "game_key": "VARCHAR(20) PRIMARY KEY", 
    "team": "VARCHAR(10)",
    
    # Names and Text
    "player_name": "VARCHAR(100)",
    "position": "VARCHAR(20)",
    "injury_status": "VARCHAR(50)",
    
    # Numbers
    "season": "INTEGER",
    "week": "INTEGER", 
    "yards": "INTEGER",
    "attempts": "INTEGER",
    
    # Decimals  
    "rating": "FLOAT",
    "percentage": "FLOAT",
    "fantasy_points": "FLOAT",
    
    # Booleans
    "active": "BOOLEAN",
    "home_game": "BOOLEAN", 
    "injured": "BOOLEAN",
    
    # JSON Data
    "additional_stats": "JSONB",
    "game_details": "JSONB",
    
    # Dates/Times
    "game_date": "DATE",
    "updated_at": "TIMESTAMP"
}
```

## 🔍 Troubleshooting

### Connection Issues

```python
seeder = NFLDataSeeder()
if not seeder.test_connection():
    print("Check your DATABASE_URL in Poke-Project/.env")
```

### API Rate Limiting

The seeder automatically includes your SportsDataIO API key. If you hit rate limits:

1. Check your SportsDataIO dashboard for usage
2. Add delays between requests if needed
3. Consider caching results locally

### Data Processing Errors

```python
def safe_processor(raw_record):
    try:
        return process_my_data(raw_record)
    except Exception as e:
        print(f"Skipping record due to: {e}")
        return None  # Returning None skips the record
```

## 🚀 Performance Tips

1. **Batch Processing**: The seeder commits every 100 records for optimal performance
2. **Primary Keys**: Choose efficient primary keys (integers > strings)
3. **JSONB Storage**: Use JSONB for flexible/nested data structures
4. **Indexing**: Add indexes after seeding large datasets

```sql
CREATE INDEX idx_player_stats_team ON nfl_player_stats_2024(team);
CREATE INDEX idx_schedule_week ON nfl_schedule_2025(week);
```

## 📈 Monitoring & Maintenance

### Check Table Sizes

```sql
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size
FROM pg_tables 
WHERE tablename LIKE 'nfl_%'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;
```

### Update Data Regularly

```python
# Daily updates during season
seeder.seed_data_from_api(
    api_url="https://api.sportsdata.io/v3/nfl/scores/json/ScoresByDate/2024-11-10",
    table_name="daily_scores",
    columns=columns,
    processor=process_scores,
    primary_key="game_id"
)
```

## 🤝 Contributing

To add new NFL data types:

1. Create a new example in `/examples/`
2. Define the processor function
3. Test with small data set first
4. Document any special handling needed

## 📝 License

This framework is designed for your personal NFL data projects and uses the SportsDataIO API with your existing subscription.