#!/usr/bin/env python3
"""
Reusable NFL Data Seeder Framework
Easily seed any NFL data to NeonDB with minimal configuration

Usage:
    from nfl_data_seeder import NFLDataSeeder
    
    seeder = NFLDataSeeder()
    seeder.seed_data_from_api("https://api.example.com/nfl/data", "my_table", columns_config)
    seeder.seed_data_from_dict(my_data, "my_table", columns_config)
"""

import psycopg2
import requests
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import sys

class NFLDataSeeder:
    """Reusable seeder for any NFL data to NeonDB"""
    
    def __init__(self, database_url: str = None):
        """Initialize seeder with database connection"""
        self.database_url = database_url or "postgresql://neondb_owner:npg_uVB7qbaKAOJ0@ep-plain-brook-ae30a98o-pooler.c-2.us-east-2.aws.neon.tech/neondb?sslmode=require"
        self.api_key = "3e9687eaec604f83af8b14709ea95172"
        
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            conn.close()
            print(f"✅ Connected to database: {db_name}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {str(e)}")
            return False
    
    def create_table(self, table_name: str, columns: Dict[str, str]) -> bool:
        """
        Create table with specified columns
        
        Args:
            table_name: Name of the table to create
            columns: Dict of column_name: column_type pairs
            
        Example:
            columns = {
                "player_id": "INTEGER PRIMARY KEY",
                "name": "VARCHAR(100)",
                "team": "VARCHAR(10)",
                "position": "VARCHAR(20)",
                "stats": "JSONB"
            }
        """
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            columns_sql = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
            
            cursor.execute(create_query)
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ Table '{table_name}' ready")
            return True
            
        except Exception as e:
            print(f"❌ Failed to create table: {str(e)}")
            return False
    
    def fetch_data_from_api(self, url: str, params: Dict = None) -> Optional[List[Dict]]:
        """Fetch data from API endpoint"""
        try:
            if params and self.api_key:
                params['key'] = self.api_key
                
            print(f"📡 Fetching data from: {url}")
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Fetched {len(data)} records")
                return data
            else:
                print(f"❌ API request failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching data: {str(e)}")
            return None
    
    def process_data(self, raw_data: List[Dict], processor: Callable[[Dict], Dict]) -> List[Dict]:
        """
        Process raw data using custom processor function
        
        Args:
            raw_data: Raw data from API
            processor: Function that takes a raw record and returns processed record
            
        Example:
            def my_processor(raw_record):
                return {
                    "player_id": int(raw_record['PlayerID']),
                    "name": raw_record['Name'],
                    "team": raw_record['Team'],
                    "stats": json.dumps(raw_record.get('Stats', {}))
                }
        """
        processed = []
        skipped = 0
        
        print(f"🔄 Processing {len(raw_data)} records...")
        
        for record in raw_data:
            try:
                processed_record = processor(record)
                if processed_record:  # Allow processor to return None to skip records
                    processed.append(processed_record)
                else:
                    skipped += 1
            except Exception as e:
                print(f"  ⚠️ Skipped record due to error: {str(e)}")
                skipped += 1
        
        print(f"📊 {len(processed)} records ready, {skipped} skipped")
        return processed
    
    def upsert_data(self, table_name: str, data: List[Dict], primary_key: str) -> tuple:
        """
        Insert or update data in the database
        
        Args:
            table_name: Target table name
            data: List of records to insert/update
            primary_key: Column name to use for conflict detection
            
        Returns:
            tuple: (inserted_count, updated_count, error_count)
        """
        if not data:
            print("⚠️ No data to insert")
            return (0, 0, 0)
            
        conn = psycopg2.connect(self.database_url)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        errors = 0
        
        # Get column names from first record
        columns = list(data[0].keys())
        placeholders = ", ".join(["%s"] * len(columns))
        
        print(f"💾 Upserting {len(data)} records to '{table_name}'...")
        
        for i, record in enumerate(data):
            try:
                if i % 100 == 0 and i > 0:
                    print(f"  Progress: {i}/{len(data)} records...")
                
                # Check if record exists
                cursor.execute(f'SELECT 1 FROM {table_name} WHERE {primary_key} = %s', (record[primary_key],))
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    set_clause = ", ".join([f"{col} = %s" for col in columns if col != primary_key])
                    update_values = [record[col] for col in columns if col != primary_key]
                    update_values.append(record[primary_key])
                    
                    update_query = f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = %s"
                    cursor.execute(update_query, update_values)
                    updated += 1
                else:
                    # Insert
                    columns_str = ", ".join(columns)
                    insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                    insert_values = [record[col] for col in columns]
                    
                    cursor.execute(insert_query, insert_values)
                    inserted += 1
                
                # Commit periodically
                if i % 100 == 0:
                    conn.commit()
                    
            except Exception as e:
                print(f"  ❌ Error with record {record.get(primary_key, 'unknown')}: {str(e)}")
                errors += 1
                conn.rollback()
        
        # Final commit
        conn.commit()
        cursor.close()
        conn.close()
        
        return (inserted, updated, errors)
    
    def seed_data_from_api(self, api_url: str, table_name: str, columns: Dict[str, str], 
                          processor: Callable, primary_key: str, params: Dict = None) -> bool:
        """
        Complete workflow: fetch from API, process, and seed to database
        
        Args:
            api_url: URL to fetch data from
            table_name: Target table name
            columns: Table column definitions
            processor: Function to process raw API data
            primary_key: Primary key column name
            params: Additional API parameters
        """
        print(f"🚀 Starting NFL data seeding workflow")
        print(f"   API: {api_url}")
        print(f"   Table: {table_name}")
        print("=" * 60)
        
        # Test connection
        if not self.test_connection():
            return False
        
        # Create table
        if not self.create_table(table_name, columns):
            return False
        
        # Fetch data
        raw_data = self.fetch_data_from_api(api_url, params)
        if not raw_data:
            return False
        
        # Process data
        processed_data = self.process_data(raw_data, processor)
        if not processed_data:
            print("❌ No data to seed after processing")
            return False
        
        # Seed to database
        inserted, updated, errors = self.upsert_data(table_name, processed_data, primary_key)
        
        # Results
        print("\n" + "=" * 60)
        print("🎉 Seeding Complete!")
        print(f"  ✅ Inserted: {inserted}")
        print(f"  🔄 Updated: {updated}")
        if errors > 0:
            print(f"  ❌ Errors: {errors}")
        print(f"  📊 Total: {inserted + updated} records in '{table_name}'")
        
        return errors == 0
    
    def seed_data_from_dict(self, data: List[Dict], table_name: str, columns: Dict[str, str], 
                           processor: Callable, primary_key: str) -> bool:
        """
        Seed data from existing dictionary/list data
        
        Args:
            data: List of dictionaries containing the data
            table_name: Target table name
            columns: Table column definitions
            processor: Function to process raw data
            primary_key: Primary key column name
        """
        print(f"🚀 Starting NFL data seeding from dictionary")
        print(f"   Records: {len(data)}")
        print(f"   Table: {table_name}")
        print("=" * 60)
        
        # Test connection
        if not self.test_connection():
            return False
        
        # Create table
        if not self.create_table(table_name, columns):
            return False
        
        # Process data
        processed_data = self.process_data(data, processor)
        if not processed_data:
            print("❌ No data to seed after processing")
            return False
        
        # Seed to database
        inserted, updated, errors = self.upsert_data(table_name, processed_data, primary_key)
        
        # Results
        print("\n" + "=" * 60)
        print("🎉 Seeding Complete!")
        print(f"  ✅ Inserted: {inserted}")
        print(f"  🔄 Updated: {updated}")
        if errors > 0:
            print(f"  ❌ Errors: {errors}")
        print(f"  📊 Total: {inserted + updated} records in '{table_name}'")
        
        return errors == 0

# Helper functions for common data types
class NFLDataHelpers:
    """Helper functions for common NFL data processing tasks"""
    
    @staticmethod
    def safe_int(value):
        """Safely convert value to integer"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def safe_float(value):
        """Safely convert value to float"""
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    @staticmethod
    def safe_bool(value):
        """Safely convert value to boolean"""
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    @staticmethod
    def json_field(value):
        """Convert value to JSON string for JSONB storage"""
        if value is None:
            return None
        return json.dumps(value)

if __name__ == "__main__":
    # Quick test
    seeder = NFLDataSeeder()
    seeder.test_connection()