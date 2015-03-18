import datetime
import json
from io import BytesIO
from uuid import uuid4
import os
import zipfile

from flask import Blueprint, render_template, request, abort

scrapbook = Blueprint(
    'scrapbook', __name__, template_folder='templates/scrapbook/'
)

def random_id():
    return uuid4().hex[-8:]

@scrapbook.route('/')
def index():
    return render_template('index.html')

@scrapbook.route('/submit', methods=['GET', 'POST'])
def submit():
    submission_id = random_id()
    div = request.form['division']
    if div == 'F':
        reprname = 'Ramji Venkataramanan'
    else:
        abort(400, 'Unknown division: {0}'.format(div))

    date = datetime.datetime.utcnow().strftime('%Y/%m/%d')
    _, image1ext = os.path.splitext(request.files['image1'].filename)
    image1fn = '{0}_image1{1}'.format(
        submission_id, image1ext if image1ext != '' else '.bin')
    _, image2ext = os.path.splitext(request.files['image2'].filename)
    image2fn = '{0}_image2{1}'.format(
        submission_id, image2ext if image2ext != '' else '.bin')

    image1contents = request.files['image1'].read()
    image2contents = request.files['image2'].read()

    csv_data = dict(
        reprname=reprname, date=date,
        image1fn=image1fn if len(image1contents) > 0 else None,
        image2fn=image2fn if len(image2contents) > 0 else None
    )
    csv_data.update(request.form)
    csv = render_template( # pylint: disable=star-args
        'scrapbookentry.csv', form=request.form, **csv_data
    )

    zf_buf = BytesIO()
    with zipfile.ZipFile(zf_buf, 'w') as zf:
        zf.writestr('{0}_entry.json'.format(submission_id), json.dumps(csv_data))
        zf.writestr('{0}_entry.csv'.format(submission_id), csv)
        if len(image1contents) > 0:
            zf.writestr(image1fn, image1contents)
        if len(image2contents) > 0:
            zf.writestr(image2fn, image2contents)

    return zf_buf.getvalue(), 200, {
        'Content-Type': 'application/zip',
        'Content-Disposition': 'attachment; ' \
            'filename="{0}_scrapbook_for_{1}.zip"'.format(
                submission_id, reprname.lower().replace(' ', '_'))
    }


