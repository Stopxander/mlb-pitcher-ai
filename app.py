def get_sharp_index():

    # Simulación basada en movimiento de línea
    # (hasta conectar odds reales)

    import random

    public_pct = random.randint(45,75)
    line_move = random.uniform(-1.5,1.5)

    sharp_score = 50

    if public_pct > 60 and line_move < 0:
        sharp_score += 25

    elif public_pct < 40 and line_move > 0:
        sharp_score += 20

    sharp_score += abs(line_move)*10

    return min(int(sharp_score),100)
