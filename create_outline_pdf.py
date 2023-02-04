# Created by OpossumDaemon, released for public domain
# edited by Grant Dersom
#!/usr/bin/env python

import locale
import subprocess
from sys import argv, exit
from os import system, remove
import re
from random import randint

import ghostscript

def read_index(path):
    base = 0     # By default the page base is 0
    
    r_entry = r"^(\s*)(-?\d+)\s+(.*?)\s*$"          # Outline entry regex 
    r_base =  r"^\s*base\s+(-?\d+)\s*$"        # Page base Increasing/decreasing regex
    r_empty = r"^\s*$"                                 # Empty line regex
    
    try:
        f = open(path)
    except:
        print('The file cannot be opened')
        exit(-1)
    l = f.readlines()
    l2 = []
    
    # Parse all the files
    for i in range(len(l)):
        l[i] = l[i].replace('\n', '').replace('\r', '')   # Remove new line and carriage return characters
        try:
            # Outline entry
            tabs, pag, name = re.match(r_entry, l[i]).groups()
            tabs = len(tabs)
            pag = int(pag) + base - 1
            l2.append([tabs, pag, name, i+1])
        except:
            try:
                #  Base change
                base = int(re.match(r_base, l[i]).groups()[0])
            except:
                # Empty line
                if re.match(r_empty, l[i]) == None:
                    # Line not recognized
                    print('Error while reading the line %d' % (i+1))
                    exit(-1)

    f.close()

    count_list =  []
    level = 0
    for i in range(0,len(l2)-1):
        count = 0
        dif = l2[i+1][0] - l2[i][0]
        if dif == 1:
            level = level + 1
            for j in range(i+1, len(l2)):
                if(l2[j][0] < level):
                    break
                if(l2[j][0] == level):
                    count = count + 1
        elif dif > 1:
            print('Error at line %d: the difference between the next subsection level and this one must not be bigger than one.' % l2[i][3])
            exit(-1)
        else:
            level = l2[i+1][0]
        count_list.append(count)
    count_list.append(0)
    
    # Generate a new file containing the instructions to add the outline for the Ghostscript program
    out = []
    for i in range(len(count_list)):
        page = l2[i][1]
        name = l2[i][2]
        if count_list[i] == 0:
            count = ''
        else:
            count = '/Count %d' % count_list[i]
        s = '[/Page %d %s/View [/XYZ null null null] /Title (%s) /OUT pdfmark\n' % (page, count, name)
        out.append(s)
        
    # Save the file
    tmp_filename = '.tmp_%x.info' % (randint(0,2**64))
    print(tmp_filename)
    f = open(tmp_filename, 'w')
    f.writelines(out)
    f.close()
    return tmp_filename
        
    

def main():
    if len(argv) != 4:
        print('Arguments: input_pdf_file outline_file output_pdf_file')
        exit(-1)
    tmp_filename = read_index(argv[2])
    args = [
        "C:\\Program Files\\gs\\gs9.54.0\\bin\\gswin64.exe",
        "-sDEVICE=pdfwrite",
        "-q",
        "-dBATCH",
        "-dNOPAUSE",
        f"-sOutputFile={argv[3]}",
        f"{tmp_filename}",
        "-f",
        f"{argv[1]}"
    ]
    print(args)
    gs_execute(args)
    remove(tmp_filename)
    
def gs_execute(commands):
    encoding = locale.getpreferredencoding()
    args = [a.encode(encoding) for a in commands]
    result = ""
    ghostscript.Ghostscript(*args, stdout=result)
    return result

main()
