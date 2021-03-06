import getpass
import secrets
import shlex
import string
import subprocess
import sys


"""
CRS secret获取、更新工具Linux版本
"""


def check_oracle_client():
    try:
        p = subprocess.Popen(
            shlex.split("sqlplus -V"), stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception:
        print("缺少sqlplus!")
        sys.exit(1)
    else:
        p.communicate()


class Crs_db:
    def __init__(self, username, password, service, ip="localhost", port="3306"):
        self.username = username
        self.password = password
        self.ip = ip
        self.port = port
        self.service = service

    def _oracle_sql(self, sql):
        sql_login_command = f"""sqlplus -S { self.username }/{ self.password }@{ self.ip }:{ self.port }/{ self.service }"""
        p = subprocess.Popen(
            shlex.split(sql_login_command),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        p.stdin.write(sql.encode())
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise ValueError(stderr.decode())
        else:
            return stdout.decode().strip().split('\n')[-1]

    def get_secret(self):
        sql = '''SELECT "app_secret" FROM AUTH WHERE "app_key" = 'admin';'''
        stdout = self._oracle_sql(sql)
        return stdout

    def update_secret(self):
        alphabet = string.ascii_letters + string.digits
        secret = "".join(secrets.choice(alphabet) for i in range(32))
        sql = f"""UPDATE "AUTH" SET "app_secret" = '{ secret }' WHERE "app_key" = 'admin';"""
        self._oracle_sql(sql)
        return secret


if __name__ == "__main__":
    check_oracle_client()

    print("""1. 获取secret\n2. 重置secret""")
    action = input("请输入:").strip()
    if action not in ("1", "2"):
        print("输入错误！")
        sys.exit(1)
    ip = input("请输入数据库IP[localhost]:") or "localhost"
    port = input("请输入数据库port[1521]:") or 1521
    service = input("请输入数据库service:")
    username = input("请输入数据库用户名[root]:") or "root"
    password = getpass.getpass("请输入数据库密码:")
    db = Crs_db(username, password, service, ip, port)

    try:
        if action == "1":
            print(f"secret: {db.get_secret() }")
        else:
            print(f"secret: { db.update_secret() }")
    except ValueError as e:
        print(e)
        print("输入信息错误!")
        sys.exit(1)