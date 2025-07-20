import argparse

# ICAO (NATO) phonetic alphabet - International (English)
icao_int = {
    'A': 'Alpha',   'B': 'Bravo',   'C': 'Charlie', 'D': 'Delta',
    'E': 'Echo',    'F': 'Foxtrot', 'G': 'Golf',    'H': 'Hotel',
    'I': 'India',   'J': 'Juliett', 'K': 'Kilo',    'L': 'Lima',
    'M': 'Mike',    'N': 'November','O': 'Oscar',   'P': 'Papa',
    'Q': 'Quebec',  'R': 'Romeo',   'S': 'Sierra',  'T': 'Tango',
    'U': 'Uniform', 'V': 'Victor',  'W': 'Whiskey', 'X': 'X-ray',
    'Y': 'Yankee',  'Z': 'Zulu',
    '0': 'Zero',    '1': 'One',     '2': 'Two',     '3': 'Three',
    '4': 'Four',    '5': 'Five',    '6': 'Six',     '7': 'Seven',
    '8': 'Eight',   '9': 'Nine'
}

# ICAO phonetic alphabet - German equivalent
icao_de = {
    'A': 'Anton',   'B': 'Berta',   'C': 'Cäsar',    'D': 'Dora',
    'E': 'Emil',    'F': 'Friedrich','G': 'Gustav', 'H': 'Heinrich',
    'I': 'Ida',     'J': 'Julius',  'K': 'Kaufmann', 'L': 'Ludwig',
    'M': 'Marie',   'N': 'Nordpol', 'O': 'Otto',    'P': 'Paula',
    'Q': 'Quelle',  'R': 'Richard', 'S': 'Samuel',  'T': 'Theodor',
    'U': 'Ulrich',  'V': 'Viktor',  'W': 'Wilhelm', 'X': 'Xanthippe',
    'Y': 'Ypsilon', 'Z': 'Zacharias',
    '0': 'Null',    '1': 'Eins',    '2': 'Zwei',     '3': 'Drei',
    '4': 'Vier',    '5': 'Fünf',    '6': 'Sechs',    '7': 'Sieben',
    '8': 'Acht',    '9': 'Neun'
}

def to_icao(text, lang='int'):
    dictionary = icao_int if lang == 'int' else icao_de
    result = []

    for char in text.upper():
        if char in dictionary:
            result.append(dictionary[char])
        elif char == ' ':
            result.append('(space)')
        else:
            result.append(f'[{char}]')  # Unknown character
    return ' '.join(result)

def main():
    parser = argparse.ArgumentParser(description='Translate text into ICAO phonetic alphabet.')
    parser.add_argument('text', type=str, help='Text to translate')
    parser.add_argument('-t', '--type', choices=['int', 'de'], default='int',
                        help='Phonetic alphabet type: "int" for International (default), "de" for German')
    args = parser.parse_args()

    translation = to_icao(args.text, lang=args.type)
    print("\nICAO Translation:")
    print(translation)

if __name__ == "__main__":
    main()
