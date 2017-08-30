"""
learn flask
"""
# pylint: disable=invalid-name

from app import create_app, mydb
from app.models import User, Role
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, mydb)

def make_shell_context():
    """manager"""
    return dict(sapp=app, smydb=mydb, sUser=User, sRole=Role)#shell命令起名
manager.add_command("shell", Shell(make_context=make_shell_context))#不明白这句话
manager.add_command('sdb', MigrateCommand)

if __name__ == '__main__':
    manager.run()
