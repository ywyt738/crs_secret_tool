import getpass
import secrets
import shlex
import string
import subprocess


"""
CRS secret获取、更新工具
"""


class Crs_db:
    def __init__(
        self, username, password, db_type="mysql", ip="localhost", port="3306"
    ):
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port

    def _execute_sql(self, command):
        command_seq = shlex.split(command)
        p = subprocess.Popen(
            command_seq,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = p.communicate()
        return stdout, stderr

    def _mysql_sql(self, sql):
        sql_command = f'mysql -u{ self.username } -p{ self.password } -h { self.ip } -P {self.port } -N -s -e "{ sql }"'
        return self._execute_sql(sql_command)

    def get_secret(self):
        sql = "select app_secret from authcenter.auth where app_key='admin'"
        stdout, stderr = self._mysql_sql(sql)
        return stdout.decode()

    def update_secret(self):
        alphabet = string.ascii_letters + string.digits
        secret = ''.join(secrets.choice(alphabet) for i in range(32))
        sql = f"update authcenter.auth set app_secret='{secret}' where app_key='admin'"
        stdout, stderr = self._mysql_sql(sql)
        return secret


if __name__ == "__main__":
    print("""1. 获取secret\n2. 重置secret""")
    action = input("请输入:").strip()
    if action not in ("1", "2"):
        print("输入错误！")
        exit(1)
    username = input("请输入数据库用户名:")
    password = getpass.getpass("请输入数据库密码:")
    db = Crs_db(username, password)

    if action == "1":
        print(db.get_secret())
    else:
        print(db.update_secret())
