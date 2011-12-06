# Deploy to live
import CsConfiguration, db
from dbModel import DbDeployScript
import subprocess, os
from subprocess import Popen, PIPE
from sqlalchemy import func

# Get root directory from live config
c_live =  CsConfiguration.CsConfiguration('/home/jonstjohn/climbspotter/live/code')
root_dir = c_live.settings['configuration']['root_dir']


# Remove code from live
cmd = ['rm', '-Rf', "{root_dir}/code/*".format(root_dir = root_dir)]
print("Removing live code directory: {0}".format(" ".join(cmd)))
print("-- output --")
print(subprocess.check_output(cmd))
print("-- end output --")


# Export code to live
cmd = "git archive master | tar -x -C {root_dir}/code".format(root_dir = root_dir)
c1, c2 = cmd.split(' | ')
p1 = Popen(c1.split(' '), stdout = PIPE)
p2 = Popen(c2.split(' '), stdin = p1.stdout, stdout = PIPE)
p1.stdout.close()
print("Exporting code to live: {0}".format(cmd))
print("-- output --")
print(p2.communicate()[0])
print("-- end output --")


# Run deploy scripts
deploy_script_dir = os.path.join(root_dir, 'code/script/deploy')

for root, subfolder, files in os.walk(deploy_script_dir):

    relative_dir = root
    relative_dir = relative_dir.replace(deploy_script_dir, '')
    mysql_root_password = c_live.settings['database']['root_password']
    database = c_live.settings['database']['database']

    session = db.session()

    for file in files:
        if file[-4:] == '.sql':

            relative_path = os.path.join(relative_dir, file)
            absolute_path = os.path.join(root, file)

            if session.query(DbDeployScript).filter(DbDeployScript.path == relative_path).count() == 0:

                cmd = "mysql -u root -p{0} {1} < {2}".format(mysql_root_password, database, absolute_path)
                print("Running deploy script '{0}' ({1})".format(absolute_path, cmd))
                print(subprocess.check_output(cmd, shell=True))

                script = DbDeployScript()
                script.path = relative_path
                script.start = func.now()
                session.add(script)

                script.end = func.now()
                session.commit()

# Reload apache
print('Reloading apache')
print('-- output --')
print(subprocess.check_output('sudo /etc/init.d/apache2 reload', shell = True))
print('-- end output --')

print("Done")
