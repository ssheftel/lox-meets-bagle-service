#! python
# -*- coding: utf-8 -*-
"""
  managment script
"""

# Set the path
import os
import sys
import json
import shutil
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)

#Add interactive shell
def make_shell_context():
    return dict(app=app, db=db, User=User)
manager.add_command("shell", Shell(make_context=make_shell_context))

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
  use_debugger = True,
  use_reloader = True,
  host = '0.0.0.0')
)

def my_setup_fn_01():
    """test by going to http://0.0.0.0:5000/api/v1.0/test"""
    for user in User.objects():
        user.delete()
    User.id.set_next_value(100)
    with open(os.path.join(os.path.dirname(__file__), 'dev-data', 'test-users.json'), 'r') as f:
        data = json.load(f)
        for user in data:
            User(**user).save()

def remove_lines(file, bad_lines):
    with open(file, 'r') as f:
        lines = f.readlines()
    with open(file, 'w') as f:
        for line in lines:

            if line not in bad_lines:
                f.write(line)
            else:
                print('removing line:{}'.format(line))
    print('done removing lines')


def copy_frountend():
    fe_dir = '/Users/sam/GoogleDrive/CodeAndDev/lox-meets-bagel-web/www'
    dest_dir = '/Users/sam/GoogleDrive/CodeAndDev/lox-meets-bagel-service/app/static_content_1_0/app'
    index_file = os.path.join(dest_dir, 'index.html')
    delete_lines = ['    <script src="http://localhost:8001/target/target-script-min.js"></script>\n','    <script src="cordova.js"></script>\n']
    try:
        shutil.rmtree(dest_dir)
    except Exception, e:
        print('no app dir to delete')
    print('copying fe')
    shutil.copytree(fe_dir, dest_dir)
    print('content copyed')
    remove_lines(index_file, delete_lines)
    print('done')


    #User.id.set_next_value(User.objects.order_by('-id').only('id').first().id + 1)
manager.add_command('mysettup1', Command(my_setup_fn_01))
manager.add_command('copyfe', Command(copy_frountend))

if __name__ == "__main__":
  manager.run()