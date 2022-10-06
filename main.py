import json
import re
from flask import Flask, render_template, request, jsonify, redirect, make_response, abort
from weasyprint import HTML
import uuid
import datetime

app = Flask(__name__, static_url_path='', static_folder='resource/public', template_folder='resource/view')

master_db = dict()


@app.route('/')
def index():
    try:
        key = uuid.uuid4().hex
    except:
        abort(500)
    else:
        return render_template('index.html')

@app.route('/resume/basic')
def resume_basic():
    try:
        key = uuid.uuid4().hex
    except:
        abort(500)
    else:
        return redirect("/resume/basic/{}".format(key), code=302)

@app.route('/resume/basic/<string:key>')
def build_resume(key: str):
    try:
        user_data = master_db.get(key)
    except Exception as ex:
        abort(500)
    else:
        return render_template("resume_basic_form.html", title='Resume Builder', key=key, data=user_data)


@app.route('/resume/genarate/<string:key>', methods=['POST'])
def generate_resume(key: str):
    try:
        data = request.form
        cpy_data = dict(data)
        cpy_data['skills'] = data['skills'].split(",")
        cpy_data['experts'] = data['experts'].split(",")
        cpy_data['work_experiance'] = []
        cpy_data['education_qualification'] = []
        work_experiance = json.loads(data['work_experiance'])

        for experiance in work_experiance:
            if experiance['designation'] != '' or experiance['company'] != '' or experiance['start_with'] != '':
                cpy_data['work_experiance'].append(experiance)

        education_qualification = json.loads(data['education_qualification'])
        for qualification in education_qualification:
            if qualification['stream'] != '' or qualification['institute']:
                cpy_data['education_qualification'].append(qualification)

        master_db[key] = dict(cpy_data)
    except Exception as ex:
        response = {'success': False, 'message': 'unhandled error'}
        return jsonify(response)

    else:
        response = {'success': True, 'message': 'successfully generated your resume',
                    'preview': f'/resume/preview/{key}'}
        return jsonify(response)


@app.route('/resume/preview/<string:key>')
def preview_resume(key: str):
    try:
        data = master_db.get(key)
    except:
        abort(500)
    else:
        return render_template('preview01.html', data=data, key=key)


@app.route('/resume/convert/pdf/<string:key>')
def convert_pdf(key: str):
    try:
        filename = f"Resume_{master_db.get(key)['lname']}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}.pdf"
        html_render = render_template('preview01.html', data=master_db.get(key), key=key)
        pdf = HTML(string=html_render, base_url='').write_pdf()
        res = make_response(pdf)
        res.headers['Content-Type'] = 'application/pdf'
        # res.headers['Content-Disposition'] = 'inline; filename={}'.format(filename)
        res.headers['Content-Disposition'] = 'attachment; filename={}'.format(filename)

    except Exception as ex:
        abort(500)
    else:
        return res


if __name__ == "__main__":
    app.run(debug=True, use_debugger=True, use_reloader=True)
