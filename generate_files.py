#!/usr/bin/env python3
"""
Generates titles.lua, sites.xml, interwiki.sql from masterSites.csv.
"""

import csv
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom 

CSV_FILE = 'masterSites.csv'
GENERATED_DIR = 'generated'
OUTPUTS = {
    'lua': f'{GENERATED_DIR}/luaArray.lua',
    'xml': f'{GENERATED_DIR}/sitelinkSites.xml',
    'sql': f'{GENERATED_DIR}/interwiki.sql'
}

def generate_lua_titles():
    titles = {}
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            prefix = row.get('globalid / iw_prefix', '').strip()
            desc = row.get('Descrizione', '').strip()
            if prefix and desc:
                titles[prefix] = desc
    
    with open(OUTPUTS['lua'], 'w', encoding='utf-8') as f:
        f.write("local Titles = {\n")
        for prefix, desc in titles.items():
            f.write(f"\t{prefix} = {desc!r},\n")
        f.write("}\n")

def generate_sites_xml():
    sites = ET.Element('sites', version='1.0', xmlns='http://www.mediawiki.org/xml/sitelist-1.0/')
    
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            site = ET.SubElement(sites, 'site', type='mediawiki')
            ET.SubElement(site, 'globalid').text = row['globalid / iw_prefix'].strip()
            ET.SubElement(site, 'group').text = row['group'].strip()
            ET.SubElement(site, 'languagecode').text = row['languagecode'].strip()
            ET.SubElement(site, 'path', type='file_path').text = row['file_path'].strip()
            ET.SubElement(site, 'path', type='page_path').text = row['page_path / iw_url'].strip()
    
    rough = ET.tostring(sites, encoding='unicode')
    reparsed = minidom.parseString(rough)
    pretty = reparsed.toprettyxml(indent='  ')
    
    with open(OUTPUTS['xml'], 'w', encoding='utf-8') as f:
        f.write(pretty)

def generate_sql_inserts():
    with open(CSV_FILE, 'r', encoding='utf-8') as f, open(OUTPUTS['sql'], 'w', encoding='utf-8') as out:
        reader = csv.DictReader(f)
        for row in reader:
            prefix = row['globalid / iw_prefix'].strip().replace("'", "''")
            url = row['page_path / iw_url'].strip().replace("'", "''")
            api = row['iw_api'].strip().replace("'", "''")
            
            sql = f"""INSERT INTO interwiki (iw_prefix, iw_url, iw_api, iw_wikiid, iw_local, iw_trans) VALUES ('{prefix}', '{url}', '{api}', '', 0, 0);"""
            out.write(sql + '\n')

if __name__ == '__main__':
    # Ensure dir exists (add to functions or main)
    os.makedirs(GENERATED_DIR, exist_ok=True)
    generate_lua_titles()
    generate_sites_xml()
    generate_sql_inserts()
    print("Generated:", ', '.join(OUTPUTS.values()))
