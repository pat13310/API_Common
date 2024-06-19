old_dict = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}

new_dict = {v: k for k, v in old_dict.items()}

print(new_dict)



