import os
import zlib

path_template = '.git/objects'
pathes = []
for i in os.listdir(path_template):
    for j in os.listdir(path_template + '/' + i):
        pathes.append(path_template + '/' + i + '/' + j)

log_heads = []
path_logs = '.git/logs/refs/heads'
for i in os.listdir(path_logs):
    log_heads.append(path_logs + '/' + i)
log_heads.remove('.git/logs/refs/heads/master')
log_heads.insert(0,'.git/logs/refs/heads/master')

result = 'digraph GitTree{\n'

def print_commits(path):
    global result
    compressed_contents = open(path, 'rb').read()
    try:
        decompressed_contents = zlib.decompress(compressed_contents).decode(errors='ignore')
    except:
        return
    lines = decompressed_contents.split('\n')
    
    if(lines[0].split()[0] == 'commit'):
        #result+='\tcommit_' + (path.split('/')[-2] + path.split('/')[-1])[:6] + '[comment="' + lines[-2] + '"];\n'
        if(lines[2].split()[0] == 'parent'):
            result += '\tcommit_' + (path.split('/')[-2] + path.split('/')[-1])[:6]  + ' -> ' + 'commit_' +(lines[2].split()[1])[:6] + ';\n'
        if(lines[1].split()[0] == 'parent'):
            result += '\tcommit_' + (path.split('/')[-2] + path.split('/')[-1])[:6]  + ' -> ' + 'commit_' +(lines[1].split()[1])[:6] + ';\n'

for i in pathes:
    print_commits(i)

def print_branches(path):
    global result
    content = open(path).read()
    lines = content.split('\n')
    branch_name = path.split('/')[-1]
    result += '\tsubgraph cluster_' + branch_name + '{\n'
    result += '\t\tlabel = ' + branch_name + '\n'
    for i in lines:
        if len(i.split()) > 1:
            result += '\t\tcommit_' + i.split()[1][:6] + ';\n'
    result += '\t}\n'

for i in log_heads:
    print_branches(i)

result+='}'
print(result)