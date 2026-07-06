import sys

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

head_part = content.split("<<<<<<< HEAD\n")[1].split("=======\n")[0]
main_part = content.split("=======\n")[1].split(">>>>>>> origin/main")[0]

merged = main_part + "\n\n---\n\n" + head_part

with open("README.md", "w", encoding="utf-8") as f:
    f.write(merged)
