import mysql.connector
import csv
import os

def export_tables_to_csv(output_folder='./csv_exports'):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='add the password here',
        database='Data base name here '
    )
    
    cursor = connection.cursor()
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    
    for table in tables:
        output_path = os.path.join(output_folder, f"{table}.csv")
        print(f"Exporting {table} to {output_path}...")
        
        cursor.execute(f"SELECT * FROM {table}")
        data = cursor.fetchall()
        
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        columns = [column[0] for column in cursor.fetchall()]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(data)
    
    cursor.close()
    connection.close()
    print(f"✅ All tables exported to {output_folder}")

# Usage - files will go in a 'csv_exports' subfolder
export_tables_to_csv()
