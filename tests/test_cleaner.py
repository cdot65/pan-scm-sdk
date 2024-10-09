# tests/test_cleaner.py

from device_certificate_report.utilities.cleaner import clean_html_tags, clean_csv
import csv
import io

def test_clean_html_tags():
    text = '<p>"Some;Text";</p>'
    cleaned = clean_html_tags(text)
    assert cleaned == '"Some;Text";'

def test_clean_csv(tmp_path):
    input_content = '''"Column1","Column2"
"<p>Data1</p>","<p>Data2</p>"
"Data;3","Data;4"
'''
    input_file = tmp_path / "input.csv"
    output_file = tmp_path / "output.csv"
    input_file.write_text(input_content)

    clean_csv(str(input_file), str(output_file))

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert rows[0] == ['Column1', 'Column2']
        assert rows[1] == ['Data1', 'Data2']
        assert rows[2] == ['Data;3', 'Data;4']