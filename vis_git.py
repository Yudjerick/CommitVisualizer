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
        if i == 0 and mode == 'text':
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
            result+='+'+i+'\n'
    for i in filenames1:
        if i not in filenames2:
            result+='-'+i+'\n'
    for i in range(len(filenames2)):
        if filenames2[i] in filenames1:
            if(hashes2[i]!=hashes1[filenames1.index(filenames2[i])]):
                result+='*'+filenames2[i]+'\n'

    print(result)



get_diff('bc5f7784c0a04c7150754b535bd9dbd1d5e03285','bc1acce86b4897d3600e52c37cba38c168eed228')
#print(b'V\t \xf0~\xfc\x85B\x9au\x96K\xb6O&\xd3\xdbb\x01D'.hex())
#print(b'\xe3\x91e\xd3\xaco\\\xe9^\x0f@\xf8na\xae\xd0\x19\xee\xfb\x15'.hex())