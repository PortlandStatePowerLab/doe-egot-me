input_names = {
    "DER": 8,
    "EDM": 11,
    "GO": 7,
    "MC": 11
}

def create_file(filename):
    fp = open(filename + '.py', 'w')
    fp.write('from behave import *')
    fp.close()

for name, max in input_names.items():
    for i in range(max):
        pr_num = i+1
        if pr_num < 10:
            print(name + "0" + str(pr_num))
            create_file(name + "0" + str(pr_num))
        else:
            print(name + str(pr_num))
            create_file(name + str(pr_num))

