def clean_and_convert_to_number(value):
    try:
        value = value.strip()
        if "," in value:
            value = value.replace(",", "")
        number = float(value)
        if number.is_integer():
            return int(number)
        return number
    except ValueError:
        return 0


def test_clean_and_convert_to_number():
    # Cas séparateurs de milliers
    assert clean_and_convert_to_number("2,000") == 2000
    assert clean_and_convert_to_number("1,000,000") == 1000000
    assert clean_and_convert_to_number("10,000") == 10000

    # Cas séparateur décimal
    assert clean_and_convert_to_number("0.200") == 0.2
    assert clean_and_convert_to_number("10.50") == 10.5
    assert clean_and_convert_to_number("0.05") == 0.05

    # Cas des virgules et des points
    assert clean_and_convert_to_number("1,851.8518") == 1851.8518
    assert clean_and_convert_to_number("2,000.500") == 2000.5

    # Cas de valeurs entières
    assert clean_and_convert_to_number("10") == 10
    assert clean_and_convert_to_number("1000") == 1000

    # Cas de valeurs flottantes valides
    assert clean_and_convert_to_number("10.5") == 10.5
    assert clean_and_convert_to_number("0.50") == 0.5

    # Cas de valeurs invalides
    assert clean_and_convert_to_number("abc") == 0
    assert clean_and_convert_to_number("100a") == 0
    assert clean_and_convert_to_number("100.abc") == 0

    print("Tous les tests ont réussi !")
