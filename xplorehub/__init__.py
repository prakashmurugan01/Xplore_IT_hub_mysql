import os

# If you prefer PyMySQL (pure-Python) instead of mysqlclient, enable the
# shim by setting `DB_PYMYSQL=1` in the environment. This makes PyMySQL act
# as MySQLdb so Django can connect without native extensions.
if os.environ.get("DB_PYMYSQL", "1") == "1":
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except Exception:
        # If PyMySQL isn't installed, let the import error surface later.
        pass
