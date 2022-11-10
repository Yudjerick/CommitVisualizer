import os
import zlib

def decode_commit(path):
    compressed_content = open(path, 'rb').read()
    decompressed_content = zlib.decompress(compressed_content).decode()
    return decompressed_content.replace('\x00', '\n')

def decode_tree(path):
    compressed_content = open(path, 'rb').read()
    decompressed_content = zlib.decompress(compressed_content)
    for i in range(len(decompressed_content)):
        if decompressed_content[i] == 0:
            decompressed_content = decompressed_content[i+1:]
            break
    result = ''
    mode = 'text'
    for i in decompressed_content:
        if i == 0:
            mode = 'hex'
            c = 20
            result+=' '
            continue
        
        if mode == 'text':
            result += i.to_bytes(1,'little').decode()
        else:
            result += i.to_bytes(1,'little').hex()
            c-=1
            if c == 0:
                mode = 'text'
                result+='\n'
    return result

def parse_commit(hashcode):
    path = '.git/objects/' + hashcode[:2] + '/' + hashcode[2:]
    content = decode_commit(path)
    return content

def parse_tree(hashcode):
    path = '.git/objects/' + hashcode[:2] + '/' + hashcode[2:]
    content = decode_tree(path)
    return content

def get_diff(commithash1,commithash2):
    commit1 = parse_commit(commithash1)
    commit_lines1 = commit1.split('\n')
    commit2 = parse_commit(commithash2)
    commit_lines2 = commit2.split('\n')
    tree1 = parse_tree(commit_lines1[1].split()[1])
    tree2 = parse_tree(commit_lines2[1].split()[1])
    tree_lines1 = tree1.split('\n')
    tree_lines2 = tree2.split('\n')
    if '' in tree_lines1:
        tree_lines1.remove('')
    if '' in tree_lines2:
        tree_lines2.remove('')

    filenames1 = []
    hashes1 = []
    for i in tree_lines1:
        filenames1.append(i.split()[1])
        hashes1.append(i.split()[2])
    filenames2 = []
    hashes2 = []
    for i in tree_lines2:
        filenames2.append(i.split()[1])
        hashes2.append(i.split()[2])
    result = ''
    for i in filenames2:
        if i not in filenames1:
            result+='+'+i+' '
    for i in filenames1:
        if i not in filenames2:
            result+='-'+i+' '
    for i in range(len(filenames2)):
        if filenames2[i] in filenames1:
            if(hashes2[i]!=hashes1[filenames1.index(filenames2[i])]):
                result+='*'+filenames2[i]+' '

    return result

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
            result += '\tcommit_' + (path.split('/')[-2] + path.split('/')[-1])[:6]  + ' -> ' + 'commit_' +(lines[2].split()[1])[:6] 
            try:
                result += ' [label="' + get_diff(lines[1].split()[1], path.split('/')[-2] + path.split('/')[-1]) +'"];\n'
            except Exception as e:
                #print(str(e))
                result += ';\n'
        if(lines[1].split()[0] == 'parent'):
            result += '\tcommit_' + (path.split('/')[-2] + path.split('/')[-1])[:6]  + ' -> ' + 'commit_' +(lines[1].split()[1])[:6]
            try:
                result += ' [label="' + get_diff(lines[1].split()[1], path.split('/')[-2] + path.split('/')[-1]) +'"];\n'
            except Exception as e:
                print(str(e))
                print(lines[1].split()[1])
                print(path.split('/')[-2] + path.split('/')[-1])
                result += ';\n'

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

end = input()