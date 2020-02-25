def calculate(data, findall):
    matches = findall(r"([abc])([+-]?)=([abc])?([+-]?\d+)?")  # Если придумать хорошую регулярку, будет просто
    for v1, s, v2, n in matches:  # Если кортеж такой структуры: var1, [sign]=, [var2], [[+-]number]
        # Если бы могло быть только =, вообще одной строкой все считалось бы, вот так:
        right_part = data.get(v2, 0) + int(n or 0)
        if s == "+":
            data[v1] += right_part
        elif s == "-":
            data[v1] -= right_part
        else:
            data[v1] = right_part
    return data
