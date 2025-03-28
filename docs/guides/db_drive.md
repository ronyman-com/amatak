from amatak.database.drivers import PostgresDriver

# Example usage
driver = PostgresDriver()
driver.connect({
    'host': 'localhost',
    'dbname': 'test',
    'user': 'postgres',
    'password': 'password'
})