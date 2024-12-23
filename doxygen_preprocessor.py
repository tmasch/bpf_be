import re



def remove_optional(content):
    # match .assert "macroName(x)", macroName(1), lda #0
    # on single line without curly braces
    if re.search(r"BaseModel",content):
        content = re.sub(r"BaseModel", r"", content)

    if re.search(r":",content):
        tt=content.split(":")
        d=tt[0]
        print(d)
        print(tt[1])
        if re.search(r"=",tt[1]):
            t=tt[1].split("=")
            print(t[0])
            print(t[1])
            if re.search(r"Optional",t[0]):
                print("found optional")
                print(t[0])
                t[0] = re.sub(r"Optional", r"", t[0])
                print(t[0])
            if re.search("list",t[0]):
                print("found list")
                print(t[0])
                t[0] = re.sub(r"list", r"", t[0])
                print(t[0])
                list="list"
            if re.search("List",t[0]):
                print("found List")
                print(t[0])
                t[0] = re.sub(r"List", r"", t[0])
                print(t[0])
                list="list"
            if re.search("Link",t[0]):
                print("found link")
                t[0] = re.sub(r"Link", r"", t[0])
            t[0] = re.sub(r"\[","",t[0])
            t[0] = re.sub(r"\]","",t[0])

            t[1] = re.sub(r"\[","\"",t[1])
            t[1] = re.sub(r"\]","\"",t[1])
            t[1] = re.sub(r"None",'""',t[1])
            content=d+":"+t[0]+"="+t[1]
    return content
    #content = re.sub(r"\]?<==", r"", content)

#    # match .assert "macroName(x)", { macroName(1) }, { lda #0 }
#    # on single or multiple line with curly braces
#    content = re.sub(r".assert [^\}]+\}[^\}]+\}", r"", content)

    return content


def main():
    filename="classes.py"
    print(filename)
    x=""
    with open(filename) as infile:
        for line in infile:
            print("")
            print(line)
            l=line.rstrip()
            l=remove_optional(l)
            print(l)
            x=x+l+"\n"
#            outfile.write(l)
    outfile=open("classes1.py","w")
    outfile.write(x)
    outfile.close()


if __name__ == "__main__":
    main()

