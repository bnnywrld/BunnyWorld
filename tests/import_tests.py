"""Parser and current geographic-map verification."""
from pathlib import Path
import sys,runpy
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools'))
from import_md import parse,Block,at_start
text='owner = OLD # comment\n 1999.1.1 = { owner = NEW } 2001.1.1 = { owner = LATE } name = "A # B"'
b=Block(at_start(parse(text)))
assert b.get('owner')=='NEW' and b.get('name')=='A # B'
assert parse('values = { 1 2 3 }').get('values').scalars()==['1','2','3']
runpy.run_path(str(root/'tests/refinement_022r2_tests.py'))
print('IMPORT_TESTS_PASS: dated history, tokenization and current HD cartography')
