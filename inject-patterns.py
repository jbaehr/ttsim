#!/bin/env python3
import argparse
import xml.etree.ElementTree as ET

ns = {
  "svg": "http://www.w3.org/2000/svg",
  "dc": "http://purl.org/dc/elements/1.1/",
  "cc": "http://creativecommons.org/ns#",
  "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  "xlink": "http://www.w3.org/1999/xlink",
  "sodipodi": "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
  "inkscape": "http://www.inkscape.org/namespaces/inkscape",
  "ttt": "http://tttool.entropia.de"}
for prefix, uri in ns.items():
  ET.register_namespace(prefix, uri)
def uname(qname):
  """makes an etree "universal name", cf. http://effbot.org/zone/element-namespaces.htm"""
  prefix, local_name = qname.split(':')
  return "{%s}%s" % (ns[prefix], local_name)

def transfer_patterns(pattern_file, target_file):
    pattern_tree = ET.parse(pattern_file)
    patterns = pattern_tree.findall('./svg:defs/svg:pattern', ns)
    pattern_ids = [p.attrib['id'] for p in patterns]
    print(f"Found patterns in {pattern_file}: {pattern_ids}")
    target_tree = ET.parse(target_file)
    target_defs = target_tree.find("./svg:defs", ns)
    if target_defs is None:
      print("Creating new <defs>-element")
      target_defs = ET.SubElement(target_tree.getroot(), uname("svg:defs"))
    else:
       for p in target_defs.findall('./svg:pattern[@ttt:oid]', ns):
         target_defs.remove(p)
    for p in patterns:
      script, oid = p.attrib['id'].rsplit('-')
      p.attrib[uname("ttt:oid")] = oid
      p.attrib[uname("ttt:script")] = script
      for path in p.findall('./svg:path[@id]', ns):
        # just to avoid id-clashes with existing content
        path.attrib['id'] = path.attrib['id'] + 'oid'
      target_defs.append(p)
    print(f"Writing updated {target_file}")
    target_tree.write(target_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pattern_file",
      help="Path and filename of the SVG file containing the patterns (the oid-table).")
    parser.add_argument("target_file",
      help="Path and filename of the SVG file into which the patterns are injected.")
    args = parser.parse_args()

    print(f"Injecting patterns from '{args.pattern_file}' into '{args.target_file}' ...")
    transfer_patterns(args.pattern_file, args.target_file)
