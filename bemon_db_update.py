from data_setting.mysql_user_data_setting import BillingDatabaseUpdater
from data_setting.MYSQL_CRUD import MySQLDatabase

db = MySQLDatabase()

database_updater = BillingDatabaseUpdater()
database_updater.update_database()