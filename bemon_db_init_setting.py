from data_setting.mysql_user_data_setting import BillingDatabaseUpdater
from data_setting.MYSQL_CRUD import MySQLDatabase

db = MySQLDatabase()

database_updater = BillingDatabaseUpdater()
database_updater.create_database_from_sql()
db.delete("ITEM_CHARGE_LIST")
db.delete("TYPE_CHARGE_LIST")
db.delete("CHARGE_CLOUD_SERVICE_LIST")
db.delete("CHARGE_THIRD_PARTY_LIST")
db.delete("CHARGE_MANAGED_SERVICE_LIST")
db.delete("CHARGE_OTHER_SERVICE_LIST")
db.delete("CHARGE_CLOUD_SERVICE_LIST")
db.delete("TOTAL_CLOUD_CHARGE_LIST")
db.delete("TOTAL_CHARGE_THIRD_PARTY_LIST")
db.delete("TOTAL_CHARGE_MANAGED_SERVICE_LIST")
db.delete("TOTAL_CHARGE_OTHER_SERVICE_LIST")
db.delete("TOTAL_CHARGE_LIST")
db.delete("SERVICE_LIST")
db.delete("THIRD_PARTY_LIST")
db.delete("MANAGED_SERVICE_LIST")
db.delete("OTHER_SERVICE_LIST")
db.delete("CLOUD_LIST")
db.delete("USER_LIST")

database_updater.user_list_insert()
database_updater.update_database()