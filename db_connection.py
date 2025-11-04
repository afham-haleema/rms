from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error


class DatabaseConnection:
    def __init__(self):
        """Initialize the database connection manager"""
        self.connection = None
        self._load_environment()
    
    def _load_environment(self):
        """Load and validate environment variables"""
        load_dotenv()  # This line was missing the import
       
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        print(f"✅ Environment variables loaded: DB_HOST={os.getenv('DB_HOST')}, DB_NAME={os.getenv('DB_NAME')}")
    
    def connect(self):
        """
        Establish a connection to the MySQL database
        """
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv("DB_HOST"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_NAME"),
                port=int(os.getenv("DB_PORT", 3306)),
                autocommit=True
            )
            
            if self.connection.is_connected():
                print("✅ Database connection established successfully")
                return True
                
        except Error as e:
            print(f"❌ Database connection error: {e}")
            print(f"❌ Connection details: host={os.getenv('DB_HOST')}, db={os.getenv('DB_NAME')}, user={os.getenv('DB_USER')}")
            return False
    
    def disconnect(self):
        """Close the database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔒 Database connection closed")
    
    def execute_query(self, query, params=None):
        """
        Execute a SQL query and return results
        """
        cursor = None
        try:
            # Ensure we have a valid connection
            if not self.connection or not self.connection.is_connected():
                print("🔄 Reconnecting to database...")
                if not self.connect():
                    print("❌ Failed to reconnect to database")
                    return None
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            
            return result
            
        except Error as e:
            print(f"❌ Query execution error: {e}")
            print(f"❌ Failed query: {query}")
            return None
        finally:
            if cursor:
                cursor.close()
    
    def get_database_info(self):
        """
        Get comprehensive database information
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()[0]
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            cursor.close()
            
            return {
                'version': version,
                'database_name': db_name,
                'table_count': len(tables)
            }
            
        except Error as e:
            print(f"❌ Error getting database info: {e}")
            return None


# Create a global database instance
db = DatabaseConnection()


def create_connection():
    """
    Legacy function for backward compatibility
    Creates a direct MySQL connection
    """
    load_dotenv()
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", 3306))
        )
        print("✅ Direct connection created")
        return conn
    except Error as e:
        print(f"❌ Direct connection error: {e}")
        return None


def initialize_database():
    """
    Initialize the database connection for the application
    """
    print("🔄 Initializing database connection...")
    if db.connect():
        info = db.get_database_info()
        if info:
            print(f"📊 Connected to: {info['database_name']}")
            print(f"🔧 MySQL Version: {info['version']}")
            print(f"📋 Tables found: {info['table_count']}")
            return True
    return False


if __name__ == "__main__":
    print("🔍 Database Connection Test")
    print("=" * 40)
    
    if initialize_database():
        print("\n✅ Database is ready for use!")
    else:
        print("\n❌ Database initialization failed!")
    
    db.disconnect()