"""
gymweb project package.

We prefer `mysqlclient` in production, but fall back to `PyMySQL`
(pure-Python) when it is not installed. This makes local setup easier
on systems without the MySQL C headers.
"""

try:  # pragma: no cover - import side effect
    import MySQLdb  # noqa: F401  (mysqlclient)
except ImportError:
    try:
        import pymysql

        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
