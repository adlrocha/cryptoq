from qkd import network3nodes
print("Running 3 nodes consensus round without cheating...")
print(network3nodes(False, [0,0,0]))
print("Running 3 nodes consensus round with cheating...")
print(network3nodes(True, [0,1,0]))
# print("Running 3 nodes consensus round with cheating...")
# print(network3nodes(True, [0,0,1]))
