# -*- coding: utf-8 -*-


from TMScrape_helpers import *


tm_fields = [
    'Abandonment Date',
    'Affidavits',
    'Assignment Recorded',
    'Attorney of Record',
    'Basic Index',
    'Current Basis',
    'Coordinated Class',
    'Cancellation Date',
    'Change in Registration',
    'Design Search Code',
    'Design Description ',
    'Description of Mark',
    'Decimal Mark ',
    'Disclaimer',
    'Filing Date',
    'Full Mark',
    'Goods and Services',
    'International Class',
    'International Registration Number',
    'Live/Dead Indicator',
    'Mark Drawing Code',
    'Mark Index',
    'Mark Non-Punctuated',
    'Mark Punctuated/Word Mark',
    'Original Filing Basis',
    'Other Data',
    'Owner Name',
    'Owner',
    'Owner Name and Address',
    'Priority Date',
    'Physical Filing Date',
    'Published for Opposition',
    'Pseudo Mark',
    'Pseudo Mark Index',
    'Prior Registrations',
    'Registration Date',
    'Renewals',
    'Register',
    'Registrant',
    'Applicant',
    'Registration Number',
    'Section 44 Indicator',
    'Single Design Code',
    'Serial Number',
    'Serial - Other Formats',
    'Standard Characters Claimed',
    'Date Amended to Current Register',
    'Total Designs',
    'Distinctiveness Limitation Statement',
    'Translation Index',
    'Translation',
    'Type of Mark',
    'Update/Load Date',
    'US Class',
    'Word Mark',
    ]

unused_fields = [
    'REGISTRATION NUMBER',
    'COORDINATED CLASS',
    'BASIC INDEX',
    'TOTAL DESIGNS',
    'PSEUDO MARK INDEX',
    'AFFIDAVITS',
    'CANCELLATION DATE',
    'ABANDONMENT DATE',
    'REGISTRATION DATE',
    'DECIMAL MARK ',
    'UPDATE/LOAD DATE',
    'ASSIGNMENT RECORDED',
    'MARK NON-PUNCTUATED',
    'SECTION 44 INDICATOR',
    'SINGLE DESIGN CODE',
    'TRANSLATION INDEX',
    'PUBLISHED FOR OPPOSITION',
    'MARK PUNCTUATED/WORD MARK',
    'SERIAL - OTHER FORMATS',
    'STANDARD CHARACTERS CLAIMED',
    'OWNER NAME',
    'OWNER NAME AND ADDRESS',
    'INTERNATIONAL REGISTRATION NUMBER',
    'PSEUDO MARK',
    'RENEWALS',
    'CHANGE IN REGISTRATION',
    'DESIGN DESCRIPTION ',
    'DATE AMENDED TO CURRENT REGISTER',
    'PHYSICAL FILING DATE',
    'MARK INDEX',
    ]

tm_fields = [x for x in tm_fields if x.upper() not in unused_fields]

missing_field_counts = { x.upper():0 for x in tm_fields }

dirty_chars = [
    '</TD>',
    '<B>',
    '</B>',
    '<TR>',
    '</TR>',
    '<',
    '>',
    '/',
    'TD',
    ',',
    '\n',
    '\t',
    '\r',
    ')',
    '(',
    '<!wwwanswer token=t_tag info=po>'.upper(),
    ]


def cleanup(anystr):
    for dirt in dirty_chars:
        anystr = anystr.replace( dirt, "" )

    newstr = anystr.strip()

    return newstr


def interpet_codes(tm_data):
    # INTERPRET TM STATUS CODES

    codes = {
        '1A' : 'USE IN COMMERCE ',
        '1B' : 'INTENT TO USE ',
        '44D' : 'FOREIGN APPLICATION ',
        '44E' : 'FOREIGN REGISTRATION ',
        '66A' : 'MADRID PROTOCOL ',
        }

    if 'CURRENT BASIS' in tm_data.keys():
        for code, status in codes.items():
            tm_data['CURRENT BASIS'] = tm_data['CURRENT BASIS'].replace(code,status)

        if len(tm_data['CURRENT BASIS']) < 2:
            tm_data['CURRENT BASIS'] = 'N/A'

    else:
        pass

    if 'ORIGINAL FILING BASIS' in tm_data.keys():
        for code, status in codes.items():
            tm_data['ORIGINAL FILING BASIS'] = tm_data['ORIGINAL FILING BASIS'].replace(code,status)

        if len(tm_data['CURRENT BASIS']) < 2:
            tm_data['CURRENT BASIS'] = 'N/A'
    else:
        pass

    return tm_data


def parse_IC_field(tm_data):

    ic_codes = tm_data['GOODS AND SERVICES'].split('IC  ')

    ic_codes = [ic.split('.')[0] for ic in ic_codes]

    ic_codes = [ic for ic in ic_codes if len(ic) > 1]

    tm_data['IC CODE'] = ic_codes

    return tm_data


def parse_field(start, end, anystring):
    final = []
    stage = []

    start = start.upper()
    end = end.upper()

    try:
        segment = anystring.split( start )[1:][0]
    except:
        return 'N/A'

    field_value = segment.split( end )[0].strip()

    field_value = cleanup( field_value )

    if len( field_value ) > 0:
        return field_value

    else:
        return 'N/A'


def parse_html(html_str):

    tm_data = {}

    html_str = html_str.upper()

        # if len of word mark is < 2, is design mark - ignore
    is_word_mark = parse_field('WORD MARK','</tr>', html_str)

    if is_word_mark != 'N/A':

        # Parse fields
        for field in tm_fields:
            field = field.upper()
            tm_data[field] = parse_field(field,'</tr', html_str)

        tm_data = interpet_codes(tm_data)

        tm_data = parse_IC_field(tm_data)

        return tm_data

    else:
        return None


def repackHTML(html_filename, html_str):
    html = html_str.split('Internet Browser to return to TESS')[-1]
    html = html.split('<!--WWWAnswer Token=T_TOOLBICON Info=home-->')[0]

    html = html.replace(')</i></font></b>\n<br>', '')
    html = html.replace('\n\n\n', '')

    os.remove('tm_record_temp/' + html_filename)

    return html


def main():

    destination = mlab.get_collection('app_data','trademarks',True)

    existing_ids = destination.distinct('_id')
    existing_ids = {x:1 for x in existing_ids}

    path = 'tm_record_temp/'

    tm_files = os.listdir(path)

    joblen = len(tm_files)

    already_in_db = 0

    for count,tm_page in enumerate(tm_files):

        print_progress('TRADEMARKS',count,joblen)

        _id = tm_page.strip('.html')

        record_date = tm_page.split('_')[0]

        full_path = path + tm_page

        try:
            check = existing_ids[ _id ]
            # If check passes, record is already in db and can be removed
            os.remove( full_path )
        except:
            html_file = open( full_path )
            html = html_file.read()

            trademark_data = parse_html( html )

            if trademark_data:

                trademark_data['RECORD DATE'] = tm_page.split('_')[0]

                trademark_data['RECORD NUMBER'] = tm_page.split('_')[-1].strip('.html')

                trademark_data['_id'] = _id

                trademark_data['RAW HTML'] = repackHTML(tm_page,html)

                destination.insert( trademark_data )

            else:
                # TM is a design mark and can be removed
                os.remove( full_path )




while True:
    try:
        main()
    except:
        print traceback.format_exc()

    time.sleep(30)
