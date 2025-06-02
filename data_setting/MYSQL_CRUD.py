import mysql.connector
import os

class MySQLDatabase:
    def __init__(self):
        self.host=os.environ.get("MYSQL_HOST")
        self.port=os.environ.get("MYSQL_PORT")
        self.user=os.environ.get("MYSQL_USER")
        self.password=os.environ.get("MYSQL_PASSWORD")
        self.database=os.environ.get("MYSQL_DATABASE")
        
        self.connection = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def insert(self, table_name, data_dict):
        columns = ", ".join(data_dict.keys())
        placeholders = ", ".join(["%s"] * len(data_dict))
        values = tuple(data_dict.values())

        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, values)
        self.connection.commit()

    def select_many(self, table_name, columns=None, conditions=None):
        if columns is None:
            columns = "*"
        query = f"SELECT {columns} FROM {table_name}"
        print("conntection 정보:",self.host,self.port,self.user,self.password,self.database)
        if conditions:
            condition_statements = []
            condition_values = []
            for key, value in conditions.items():
                condition_statements.append(f"{key} = %s")
                condition_values.append(value)

            condition_string = " AND ".join(condition_statements)
            query += f" WHERE {condition_string}"
            self.cursor.execute(query, tuple(condition_values))
        else:
            self.cursor.execute(query)

        return self.cursor.fetchall()

    def select_one(self, table_name, columns=None, conditions=None):
        if columns is None:
            columns = "*"

        query = f"SELECT {columns} FROM {table_name}"

        if conditions:
            condition_statements = []
            condition_values = []
            for key, value in conditions.items():
                condition_statements.append(f"{key} = %s")
                condition_values.append(value)

            condition_string = " AND ".join(condition_statements)
            query += f" WHERE {condition_string}"
            self.cursor.execute(query, tuple(condition_values))
        else:
            self.cursor.execute(query)
        selected_data = self.cursor.fetchone()
        return selected_data

    def update(self, table_name, data_dict, conditions):
        set_statements = ", ".join([f"{key} = %s" for key in data_dict.keys()])
        set_values = list(data_dict.values())

        condition_statements = " AND ".join([f"{key} = %s" for key in conditions.keys()])
        condition_values = list(conditions.values())

        query = f"UPDATE {table_name} SET {set_statements} WHERE {condition_statements}"
        self.cursor.execute(query, set_values + condition_values)
        self.connection.commit()

    def delete(self, table_name):
        query = f"DELETE FROM {table_name}"
        self.cursor.execute(query)
        self.connection.commit()

    def close(self):
        self.cursor.close()
        self.connection.close()
