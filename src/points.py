logo = """
          ..                  ....   
          ..                  ....   
          ..                  ....   
          ..                  ....   
          ..                  ....   
 ...........  ..........  ............  .......... 
............ ............ ............ ............
....    .... ....    ....     ....       ......
....    .... ....    ....     ....         ......
............ ............     ....     ............
 ..........   ..........      ....      ..........
"""[1:-1]

points = []

logo = logo.split('\n')
for row in range(len(logo)):
    for char in range(len(logo[row])):
        if logo[row][char] == '.':
            points.append((char, row))