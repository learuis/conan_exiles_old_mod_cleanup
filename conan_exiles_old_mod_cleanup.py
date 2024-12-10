from flask import Flask, render_template, request
import regex as re


app = Flask(__name__, template_folder='/home/learuis/templates/')

@app.route('/', methods=['GET', 'POST'])
def index():
    outputstring = ''
    if request.method == 'POST':
        file = request.files['myfile']
        if file:
            filedata = file.read().decode('utf-8')
            result_org = re.findall(r'\[\d+.\d+.\d+-\d+.\d+.\d+.\d+\].* NameToLoad: '
                                    r'(.*)\n.*\n\[\d+.\d+.\d+-\d+.\d+.\d+.\d+\].* String asset reference '
                                    r'\"None\".*slow.', filedata)

            for x in result_org:
                print(f'{x}')
                outputstring += (f'DELETE FROM buildable_health WHERE object_id IN('
                                 f'SELECT DISTINCT object_id FROM buildings WHERE object_id IN ('
                                 f'SELECT DISTINCT object_id FROM properties WHERE object_id IN ('
                                 f'SELECT id FROM (SELECT id, trim(substr(class, INSTR(class, \')/BP\'), '
                                 f'length(class)), \'/\') AS name FROM actor_position '
                                 f'WHERE class LIKE \'{x.strip()}%\'))));\n')
                outputstring += '--'
                outputstring += (f'DELETE FROM buildings WHERE object_id IN('
                                 f'SELECT DISTINCT object_id FROM properties WHERE object_id IN ('
                                 f'SELECT id FROM (SELECT id, trim(substr(class, INSTR(class, \'/BP\'), '
                                 f'length(class)), \'/\') AS name FROM actor_position '
                                 f'WHERE class LIKE \'{x.strip()}%\')));\n')
                outputstring += '--'
                outputstring += (f'DELETE FROM properties WHERE object_id IN('
                                 f'SELECT id FROM (SELECT id, trim(substr(class, INSTR(class, \'/BP\'), '
                                 f'length(class)), \'/\') AS name FROM actor_position '
                                 f'WHERE class LIKE \'{x.strip()}%\'));\n')
                outputstring += '--'
                outputstring += f'DELETE FROM actor_position WHERE class LIKE \'{x.strip()}%\';\n'

            outputstring += '--  // Separator between matches\n'
            outputstring += 'VACUUM;\n'
            outputstring += 'REINDEX;\n'
            outputstring += 'ANALYZE;\n'
            outputstring += 'PRAGMA integrity_check;'

            return render_template('output.html', filename='GeneratedSQL.sql', filedata=outputstring,
                                   badentries=f'{len(result_org)} actors from old mods were found.')
        else:
            return "No file selected."

    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
