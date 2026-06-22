import csv
import getpass
import pg8000

def download_data():
    print("Export Quiz Results from Database")
    print("---------------------------------")
    
    # Securely ask for the database password
    password = getpass.getpass("Enter Database Password: ")
    
    # Connection parameters based on docker-compose.yml configuration
    host = "127.0.0.1"
    port = 5433
    database = "sentence_db"
    user = "postgres"
    
    conn = None
    try:
        print(f"Connecting to database '{database}' on {host}:{port}...")
        # Establish connection using pg8000
        conn = pg8000.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        cursor = conn.cursor()
        
        # Execute query to fetch all columns from quiz_results
        print("Fetching quiz results...")
        cursor.execute("SELECT id, email, score, total_questions, level, created_at FROM quiz_results ORDER BY id ASC;")
        rows = cursor.fetchall()
        
        # Write to CSV
        output_file = "quiz_results.csv"
        print(f"Writing data to {output_file}...")
        
        with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            # Write header
            writer.writerow(['ID', 'Email Hash (SHA-256)', 'Score', 'Total Questions', 'Level', 'Created At'])
            # Write rows
            writer.writerows(rows)
            
        print("Success! Data downloaded successfully.")
        
    except pg8000.exceptions.Error as db_err:
        print(f"\nDatabase Error: {db_err}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    download_data()
