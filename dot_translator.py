import os
import zlib

path_template = '.git/objects'
pathes = []
for i in os.listdir(path_template):
    for j in os.listdir(path_template + '/' + i):
        pathes.append(path_template + '/' + i + '/' + j)

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
        #print(decompressed_contents)
        #print('-'*15)
        #print()
        result+='commit_' + (path.split('/')[-2] + path.split('/')[-1])[:6] + '[comment="' + lines[-2] + '"];\n'
        if(lines[2].split()[0] == 'parent'):
            result += 'commit_' + (path.split('/')[-2] + path.split('/')[-1])[:6]  + ' -> ' + 'commit_' +(lines[2].split()[1])[:6] + ';\n'
        if(lines[1].split()[0] == 'parent'):
            result += 'commit_' + (path.split('/')[-2] + path.split('/')[-1])[:6]  + ' -> ' + 'commit_' +(lines[1].split()[1])[:6] + ';\n'
        

for i in pathes:
    print_commits(i)

result+='}'
print(result)