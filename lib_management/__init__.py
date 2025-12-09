# This allows the app to run on Render (where pymysql is missing)
# AND on your laptop (where pymysql is present).

try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass