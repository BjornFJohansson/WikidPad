# -*- coding: latin-1 -*-
def split_table_to_list(rawtable):

    from sys import exit
    import re
    import itertools
    import textwrap

    table = textwrap.dedent(rawtable.expandtabs(4)).strip()

    max_row_length = max([len(row.strip()) for row in table.splitlines()])

    rows = [row.ljust(max_row_length) for row in table.splitlines()]

    table = "\n".join(rows)

    number_of_rows = len(rows)

    transposed_table = "\n".join(["".join(c) for c in zip(*rows)])

    empty_column = "(?:\n? {%s}\n)+" % (number_of_rows)

    cols = re.split(empty_column,transposed_table)

    tttable = []

    for col in cols:
        columnlist = ["".join(c).strip() for c in zip(*[a for a in col.splitlines() if a])]
        maxlen = max([len(c) for c in columnlist])
        columnlist = [c.ljust(maxlen) for c in columnlist]
        tttable.append(columnlist)

    formattedtable = "\n".join([" ".join(c) for c in zip(*tttable)])
    '''
    print formattedtable == table

    print table
    print len(table)
    print formattedtable
    print len(formattedtable)
    '''

    if not formattedtable == table:
        return formattedtable

    columnsplit = "\n|||\n".join(["\n".join(["".join(c) for c in zip(*col.strip("\n").splitlines())]) for col in cols])

    #rowsplit =  "\n---\n".join(["\n".join(a).strip() for a in zip(*tttable)])

    content =  columnsplit

    return content

def join_list_to_table(rawlist):

    import sys
    import re
    import itertools
    from sys import exit

    if "|||\n" in rawlist:
        raw_columns=rawlist.split("|||\n")
        cols = [col.splitlines() for col in raw_columns]
        if "" in [item for sublist in cols for item in sublist]:
            cols = [col.split("\n\n") for col in raw_columns]

    elif "---\n" in rawlist:
        rawrows=rawlist.split("---\n")
        rows = [row.splitlines() for row in rawrows]
        cols = list(itertools.zip_longest(*rows,fillvalue=''))
    else:
        return

    number_of_rows = max([len(col) for col in cols])
    formatted_cols = []

    for col in cols:
        #print col
        rows = [row.strip() for row in col]
        width = max([len(row) for row in rows])

        rows = [row.ljust(width) for row in rows]
        rows+= [' '*width]*(number_of_rows-len(rows))
        formatted_cols.append(rows)

    rows=list(zip(*formatted_cols))

    combinedlist = []

    for row in rows:
        combinedlist.append(" ".join(row))

    new_text='\n'.join(combinedlist)

    return new_text

if __name__=="__main__":



    rawtable    =[

    '''

    #   mm      temp  Descr   vect
    r1   30.0   0.00  CES201  NFPacpRBL         a1
    r2    30.0   0.00  CES201      NFPacpRBL    a2
    r3   30.0   0.00  CES201  NFPacpRBL         a3x


    ''',

    '''

    1  Xs
        Xx

    2  Y
       Y

    ''',

    '''

1    Vale de Lamaçães Lugar de Bretas 4701 Braga tel. +351 253 240 080 fax. +351 253
    240 086Horário de Abertura: Seg. a Dom. 09h - 22h

2    Vale de Lamaçães Lugar de Bretas 4702 Braga tel. +351 253 240 080 fax. +351 253
    240 086Horário de Abertura: Seg. a Dom. 09h - 22h

3    Vale de Lamaçães Lugar de Bretas 4703 Braga tel. +351 253 240 080 fax. +351 253
    240 086Horário de Abertura: Seg. a Dom. 09h - 22h''']



    print()
    print()
    print()
    print()
    print()
    for rt in rawtable:
        print("~raw~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(rt)
        print("~formatted~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        a = split_table_to_list(rt)
        print(a)
        print("~split~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        b = split_table_to_list(a)
        print(b)
        print("~joined~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        c = join_list_to_table(b)
        print(c)
        print()
        print()
        print()
        print()
        print()
