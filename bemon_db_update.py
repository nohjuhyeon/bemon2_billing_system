from data_setting.mysql_user_data_setting import BillingDatabaseUpdater
from data_setting.MYSQL_CRUD import MySQLDatabase
from datetime import datetime

db = MySQLDatabase()

database_updater = BillingDatabaseUpdater()
database_updater.update_database()
print(f"CSP Billing Data Updated: {datetime.now()}")
