import csv
import xml.etree.ElementTree as ET

def generate_lua_titles(csv_file='data.csv', output_file='titles.lua'):
    titles = {}
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)  # Comma delimiter, auto-detects headers
        for row in reader:
            prefix = row.get('globalid / iw_prefix', '').strip()
            desc = row.get('Descrizione', '').strip()
            if prefix and desc:
                titles[prefix] = desc  # Overwrites dups like 'dema'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("local Titles = {\n")
        for prefix, desc in titles.items():
            f.write(f"\t{prefix} = {desc!r},\n")
        f.write("}\n")



def generate_sites_xml(csv_file='data.csv', output_file='sites.xml'):
    sites = ET.Element('sites', version='1.0', xmlns='http://www.mediawiki.org/xml/sitelist-1.0/')
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            site = ET.SubElement(sites, 'site', type='mediawiki')
            ET.SubElement(site, 'globalid').text = row['globalid / iw_prefix'].strip()
            ET.SubElement(site, 'group').text = row['group'].strip()
            ET.SubElement(site, 'languagecode').text = row['languagecode'].strip()
            ET.SubElement(site, 'path', type='file_path').text = row['file_path'].strip()
            ET.SubElement(site, 'path', type='page_path').text = row['page_path / iw_url'].strip()
    
    tree = ET.ElementTree(sites)
    with open(output_file, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)

def generate_sql_inserts(csv_file='data.csv', output_file='interwiki.sql'):
    with open(csv_file, 'r', encoding='utf-8') as f, open(output_file, 'w', encoding='utf-8') as out:
        reader = csv.DictReader(f)
        for row in reader:
            prefix = row['globalid / iw_prefix'].strip().replace("'", "''")  # SQL escape
            url = row['page_path / iw_url'].strip().replace("'", "''")
            api = row['iw_api'].strip().replace("'", "''")
            
            sql = f"""INSERT INTO interwiki (iw_prefix, iw_url, iw_api, iw_wikiid, iw_local, iw_trans) VALUES ('{prefix}', '{url}', '{api}', '', 0, 0);"""
            out.write(sql + '\n')
