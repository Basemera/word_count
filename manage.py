import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app, db

app = create_app()
app.config.from_object('config')

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    db.init_app(app)
    with app.app_context():
        db.create_all()

    manager.run()