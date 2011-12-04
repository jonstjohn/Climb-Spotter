# Deploy to live
import CsConfiguration
import subprocess
from subprocess import Popen, PIPE

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

print("Done")
