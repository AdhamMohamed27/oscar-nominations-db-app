import csv
import mysql.connector
from mysql.connector import Error
from datetime import datetime

def debug_production_import():
    connection = None
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='MNaHB2004',
            database='OscarNominations',
            autocommit=False
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            print("✅ Successfully connected to MySQL")

            # First verify the file exists
            file_path = '/Users/adhammohamed65icloud.com/Desktop/Movie_PorductionCompany.csv'
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    # Debug: Print first 5 lines to verify content
                    print("\n=== FILE CONTENT SAMPLE ===")
                    for i, line in enumerate(file):
                        if i < 5:
                            print(f"Line {i}: {line.strip()}")
                        else:
                            break
                    
                    file.seek(0)  # Reset file pointer
                    
                    # Check if file has headers
                    sniffer = csv.Sniffer()
                    has_headers = sniffer.has_header(file.read(2048))
                    file.seek(0)
                    
                    print(f"\nFile has headers: {has_headers}")
                    
                    if has_headers:
                        reader = csv.DictReader(file)
                        print(f"Detected columns: {reader.fieldnames}")
                        
                        companies_imported = 0
                        for i, row in enumerate(reader):
                            try:
                                # Debug: Print raw row data
                                if i < 5:  # Print first 5 rows for verification
                                    print(f"\nRow {i} data: {row}")
                                
                                # Get values with fallbacks
                                company_name = row.get('Company Name (Wikipedia)', '').strip()
                                hq = row.get('Company HQ', 'Unknown').strip()
                                year = row.get('Company Founded Year', '').strip()
                                
                                # Skip if missing essential data
                                if not company_name or not year.isdigit():
                                    print(f"⚠️ Skipping row {i}: Missing data")
                                    continue
                                
                                # Convert year to date
                                foundation_date = datetime.strptime(year, '%Y').date()
                                
                                # Insert with debug output
                                cursor.execute(
                                    "INSERT INTO Production_Company (Company_Name, HQ, Foundation_Year) "
                                    "VALUES (%s, %s, %s) "
                                    "ON DUPLICATE KEY UPDATE HQ = VALUES(HQ), Foundation_Year = VALUES(Foundation_Year)",
                                    (company_name, hq, foundation_date)
                                )
                                
                                if cursor.rowcount == 1:
                                    companies_imported += 1
                                    print(f"✅ Inserted: {company_name}")
                                else:
                                    print(f"⏩ Updated: {company_name}")
                                    
                            except ValueError as e:
                                print(f"🛑 Row {i} value error: {e}")
                            except Exception as e:
                                print(f"🔴 Row {i} unexpected error: {e}")
                                raise
                        
                        connection.commit()
                        print(f"\n🎉 Successfully processed {companies_imported} companies")
                    
                    else:
                        print("🔴 Error: CSV file lacks proper headers")
                        
            except FileNotFoundError:
                print(f"🔴 File not found: {file_path}")
            except Exception as e:
                print(f"🔴 File reading error: {e}")

    except Error as e:
        print(f"🔴 MySQL Error: {e}")
        if connection:
            connection.rollback()
    except Exception as e:
        print(f"🔴 Critical Error: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 MySQL connection closed")

# Verification queries
def verify_import():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='MNaHB2004',
            database='OscarNominations'
        )
        cursor = conn.cursor()
        
        print("\n=== VERIFICATION ===")
        
        # Check table exists
        cursor.execute("SHOW TABLES LIKE 'Production_Company'")
        print(f"Table exists: {bool(cursor.fetchone())}")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM Production_Company")
        count = cursor.fetchone()[0]
        print(f"Total companies in table: {count}")
        
        # Show sample records
        if count > 0:
            cursor.execute("SELECT * FROM Production_Company LIMIT 5")
            print("\nSample records:")
            for row in cursor:
                print(row)
        
    except Error as e:
        print(f"Verification error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

# Run both functions
debug_production_import()
verify_import()