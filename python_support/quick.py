import os
import re
for i in os.listdir("../RWHDERS_Inputs/midrar_files"):
    g = re.match(r"DER(\d+)_Bus([^.]+)\.csv",i)
    if g:
        g1 = g.group(1)
        print(g1)
        g2 = g.group(2)
        print(g2)