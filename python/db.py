import pymysql


class mysql:
    def __init__(self, host, id, pw, db_name):
        self.db = pymysql.connect(host=host, user=id, password=pw,
                                  db=db_name, charset='utf8')
        self.cursor = self.db.cursor()

    def get_results(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def query(self, sql):
        self.cursor.execute(sql)
        self.db.commit()

    def rows(self):
        return self.cursor.rowcount

    def close(self):
        self.db.close()
