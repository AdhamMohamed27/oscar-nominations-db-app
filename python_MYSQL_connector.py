import pymysql

# Replace with your db4free credentials
db_config = {
    "host": "sql.freedb.tech",
    "user": "freedb_adhamsmacbook",                # your actual db4free username
    "password": "$?%6HF9&a5k$#wz",   # your actual db4free password
    "database": "freedb_OscarNominations",         # your actual database name
    "port": 3306
}


try:
    connection = pymysql.connect(**db_config)
    print("Connection successful!")

    # Example query to test
    with connection.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        for row in cursor.fetchall():
            print(row)

except pymysql.MySQLError as e:
    print(f"❌ Error: {e}")

finally:
    if 'connection' in locals():
        connection.close()
