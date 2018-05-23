import os
import copy
from collections import defaultdict

from bokeh.io import curdoc
from bokeh.layouts import widgetbox
from bokeh.models.widgets import Div
from bokeh.layouts import column, row
from bokeh.models.widgets import Select, TextInput

import file_handling as fh

# run like: bokeh serve --show browse_entities.py

colors = [
    '#922B21',
    '#76448A',
    '#1F618D',
    '#148F77',
    '#1E8449',
    '#B7950B',
    '#AF601A',
    '#717D7E',
    '#B03A2E',
    '#6C3483',
    '#2874A6',
    '#117A65',
    '#239B56',
    '#B9770E',
    '#A04000',
    '#616A6B'
]

data = fh.read_jsonlist(os.path.join('data', 'msa', 'all.parsed.jsonlist'))


doc_select = Select(title="Document", value=str(0), options=[str(i) for i in range(len(data))])
#ner_select = Select(title="Entity type", value='', options=[''])
entity_select = Select(title="Entity", value='', options=[''])
#entity_types = defaultdict(set)
selected_entity = 0

div = Div(text="", width=600, height=200)

box = widgetbox(div)

layout = column(row(doc_select, entity_select), widgetbox(div))

curdoc().add_root(layout)


def update_div(selected_entity):
    doc_index = doc_select.value
    doc = data[int(doc_index)]
    sentences = copy.deepcopy(doc['sentences'])
    coref = doc['coref']

    color = '#3498DB'
    entity = coref[int(selected_entity)]
    print(selected_entity)
    print(entity)
    for mention in entity:
        sent = mention['sent']
        start = mention['start']
        end = mention['end']
        sentences[sent][start] = '<font color=' + color + '>[' + sentences[sent][start]
        sentences[sent][end-1] = sentences[sent][end-1] + ']<sub>' + str(selected_entity) + '</sub></font>'

    sentences = [' '.join(words) for words in sentences]
    print(sentences)
    text = '\n\n'.join(['<p>' + sent + '</p>' for sent in sentences])
    div.update(text=text)
    print(doc['sentences'])


def update_selected_document(attrname, old, new):
    print(new)
    update_entity_list(int(new))


"""
def update_entity_type_list(doc_index):
    doc = data[doc_index]
    coref = doc['coref']
    #entity_types = defaultdict(list)
    keys = list(entity_types.keys())
    for k in keys:
        entity_types.pop(k)
    for e_i, entity in enumerate(coref):
        for mention in entity:
            ner = mention['ner']
            if ner != '':
                entity_types[ner].add(e_i)
    keys = list(entity_types.keys())
    keys.sort()
    ner_select.options = keys
    ner_select.value = keys[0]


def update_selected_entity_type(attrname, old, new):
    print(new)
    update_entity_list(new)
"""

def update_entity_list(doc_index):
    print('in update_entity_list')
    #entity_indices = list(entity_types[entity_type])
    #entity_indices.sort()
    #print(entity_indices)
    #doc_index = doc_select.value
    #print('doc_index:', doc_index)
    doc = data[int(doc_index)]
    coref = doc['coref']
    entities = {}
    for e_i, entity in enumerate(coref):
        print(e_i)
        for m_i, mention in enumerate(entity):
            print('\t', mention)
            if m_i == 0:
                entities[e_i] = mention['text']
            if mention['isRepresentative']:
                entities[e_i] = mention['text']
    print(entities)
    entities = [str(k) + ': ' + v for k, v in entities.items()]
    entity_select.options = entities
    selected_entity = 0
    entity_select.value = entities[selected_entity]


def update_selected_entity(attrname, old, new):
    print(new)
    div.update(text="")
    parts = new.split(':')
    index = parts[0]
    #entity_type = ' '.join(parts[1:])
    selected_entity = int(index)
    update_div(selected_entity)


doc_select.on_change('value', update_selected_document)
#ner_select.on_change('value', update_selected_entity_type)
entity_select.on_change('value', update_selected_entity)

doc_select.value = '0'