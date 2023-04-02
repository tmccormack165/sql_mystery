import sqlite3
import pandas as pd

def get_metadata(cur):
    metadata = {}

    # reading all table names
    table_list = [a[0] for a in cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    # here is you table list

    for i in range(len(table_list)):
        column_query = f"PRAGMA table_info({table_list[i]})"
        cur.execute(column_query)
        r = cur.fetchall()
        column_list = [x[1] for x in r]
        metadata[table_list[i]] = column_list
        
    return metadata

def run_query(cur, query):
    cur.execute(query)
    r = cur.fetchall()
    return r

def reverse_str(s):
  return s[::-1]

def apply_alias(s, alias_lookup):
    for k, v in alias_lookup.items():
        s = s.replace(f'{k}.', f'{v}.')
    return s

def search_alias(cnames, query, verbose):
    # get aliases
    aliases = []
    for i in range(len(cnames)):
        alias_start = 0
        alias_end = cnames[i].find('.')
        alias = cnames[i][alias_start:alias_end]
        if(alias not in aliases):
            aliases.append(alias)

    alias_lookup = {}
    for i in range(len(aliases)):
        alias_start = query.find(f' {aliases[i]} ')
        if(alias_start == -1):
            alias_start = query.find(f' {aliases[i]}\n')
        subset = query[:alias_start]
        offset = -1
        nextchar = subset[offset]
        full_alias = ''
        while(nextchar.isalpha() or nextchar == '_'):
            full_alias += nextchar
            offset -= 1
            nextchar = subset[offset]
        reverse_str(full_alias)
        full_alias = reverse_str(full_alias)
        alias_lookup[aliases[i]] = full_alias
    
    if(verbose == True):
        print(f'ALIAS LOOKUP: {alias_lookup}')
    
    column_names = [apply_alias(x, alias_lookup) for x in cnames]
    return column_names

def format_output(metadata, r, query, verbose=False):
    if('*' in query):
        tab_start = query.find('FROM') + len('FROM') + 1
        tab_end = query.find('WHERE')
        table_name = query[tab_start:tab_end].strip(' ')
        column_names = metadata[table_name]
        column_names = search_alias(column_names, query, verbose)
        
    else:
        # get the column names preceeding FROM
        cnames_start = query.find('SELECT') + len('SELECT') + 1
        cnames_end = query.find('FROM')

        cnames = query[cnames_start:cnames_end].split(',')
        cnames = [x.strip(' ') for x in cnames]
        cnames = [x.strip('\n') for x in cnames]
        if(verbose == True):
            print(f'CNAMES: {cnames}')
            column_names = search_alias(cnames, query, verbose)
            print(f'CNAMES: {cnames}')
        else:
            column_names = search_alias(cnames, query, verbose)

        

    output_records = []
    for i in range(len(r)):
        record = {}
        for j in range(len(r[i])):
            key = column_names[j]
            value = r[i][j]
            record[key] = value
        output_records.append(record)

    output_df = pd.DataFrame(output_records)

    return output_df

