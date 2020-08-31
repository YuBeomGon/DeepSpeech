import re
slist = ['S', ' ', 'po', ' ', 'po', ' ', 'hae', ' ', 'S', ' ']
print(slist)

print("".join(slist))

a = " hi my name 은 범곤 1"
b = " hi my name 은 범"

result = re.findall("\d+", a)
print(result)
print(re.findall("\d+", b))


if not (re.findall("\d+", b)):
    print("hi")
