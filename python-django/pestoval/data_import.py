from pestoval import models

import datetime
from lxml import html
import requests
import tinycss

level_of_color = {
    '#d9ead3': 1,
    '#fff2cc': 2,
    '#ead1dc': 3,
    '#ea9999': 4,
    }

def get_docs_table():
    url = 'https://docs.google.com/document/d/e/2PACX-1vTO3SDVG04EY5Mp8uWjJZawxedIK80o1VGRHeJOyUqJnS65Kuqel7A6B5k6vm_2quoo2wAwmxiZFV-g/pub'
    page = requests.get(url).text
    tree = html.fromstring(page)
    stylesheet = tinycss.make_parser().parse_stylesheet(tree.xpath('//style')[1].text)
    class_colors = {}
    for rule in stylesheet.rules:
        selector = rule.selector.as_css()
        if not selector.startswith('.'):
            continue
        for decl in rule.declarations:
            if decl.name != 'background-color':
                continue
            class_colors[selector[1:]] = decl.value[0].value
    all_rows = tree.xpath('//tr')
    headers = [x.text_content() for x in all_rows[1]]
    classes = []
    for row in all_rows[2:]:
        if len(row) == 1:
            [day_name, month_name, day_of_month, times] = row.text_content().split(None, 3)
            [start, stop] = times.replace('–', '-').split('-')
            [start_hour, start_min] = map(int, start.split(':'))
            [stop_hour, stop_min] = map(int, stop.split(':'))
            assert month_name == 'April'
            common = {
                'start': datetime.datetime(2018, 4, int(day_of_month), start_hour, start_min),
                'stop': datetime.datetime(2018, 4, int(day_of_month), stop_hour, stop_min),
            }
            continue
        cur = common.copy()
        for style_class in row[0].classes:
            color = class_colors.get(style_class)
            if color and color in level_of_color:
                cur['level'] = level_of_color[color]
                break
        else:
            cur['level'] = None
        for header, val in zip(headers, [x.text_content() for x in row]):
            cur[header] = val
        classes.append(cur)
    return classes

def teachers_from_classes(classes):
    teachers = set()
    for x in classes:
        for teacher in x['Teachers'].split(' & '):
            teachers.add(teacher)
    return teachers

def timeslots_from_classes(classes):
    timeslots = set()
    for x in classes:
        timeslots.add((x['start'], x['stop']))
    return timeslots

def add_teacher(name):
    models.Teacher.objects.get_or_create(name=name)

def add_timeslot(desc):
    (start, stop) = desc
    models.TimeSlot.objects.get_or_create(start=start, stop=stop)

def add_class(desc):
    when = models.TimeSlot.objects.get(start=desc['start'], stop=desc['stop'])
    where = models.Location.objects.get(name=desc['Location'])
    who = [models.Teacher.objects.get(name=x) for x in desc['Teachers'].split(' & ')]
    try:
        x = models.Session.objects.get(when = when, location = where)
    except models.Session.DoesNotExist:
        x = models.Session(when = when, location = where, name = desc['Class'])
        x.save()
        for teacher in who:
            x.teachers.add(teacher)
    else:
        print('Class at time and place already exists: %s' % x)
        prev_teacher_names = set(t['name'] for t in x.teachers.values())
        assert set(t.name for t in who) >= prev_teacher_names
        for teacher in who:
            if teacher.name not in prev_teacher_names:
                print('Adding teacher %s' % teacher)
                x.teachers.add(teacher)

    x.description = desc['Description']
    x.prereqs = desc['Prereqs']
    x.level = models.Level.objects.get(as_number = desc['level']) if desc['level'] else None
    x.save()

def update_classes():
    classes = get_docs_table()
    for x in classes:
        add_class(x)
