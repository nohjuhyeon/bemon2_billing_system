from data_setting.mysql_user_data_setting import BillingDatabaseUpdater
from data_setting.MYSQL_CRUD import MySQLDatabase
from datetime import datetime

db = MySQLDatabase()
try:
    database_updater = BillingDatabaseUpdater()
    database_updater.update_database()
    print(f"CSP Billing data updated successfully at: {datetime.now()}")
except Exception as e:
    print(f"Failed to update CSP Billing data at: {datetime.now()} - Error: {e}")
