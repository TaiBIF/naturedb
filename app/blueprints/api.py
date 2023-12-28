import json
import time
import re
import logging
import math
from datetime import datetime

from flask import (
    Blueprint,
    request,
    abort,
    jsonify,
)
from flask.views import MethodView
from sqlalchemy import (
    select,
    func,
    text,
    desc,
    cast,
    between,
    Integer,
    LargeBinary,
    extract,
    or_,
    inspect,
    join,
)
from sqlalchemy.dialects.postgresql import ARRAY

from app.database import session

from app.models.collection import (
    Record,
    Person,
    NamedArea,
    AreaClass,
    Unit,
    Identification,
    Person,
    AssertionTypeOption,
    Collection,
    MultimediaObject,
    #LogEntry,
    #get_structed_list,
)
from app.models.taxon import (
    Taxon,
    TaxonRelation,
)
from app.models.site import (
    Favorite,
)

from app.helpers_query import (
    make_specimen_query,
)


api = Blueprint('api', __name__)

def make_query_response(query):
    start_time = time.time()

    rows = [x.to_dict() for x in query.all()]
    end_time = time.time()
    elapsed = end_time - start_time

    result = {
        'data': rows,
        'total': len(rows),
        'query': str(query),
        'elapsed': elapsed,
    }
    # print(result, flush=True)
    return result


#@api.route('/searchbar', methods=['GET'])
def get_searchbar():
    '''for searchbar
    '''
    q = request.args.get('q')
    data = []
    if q.isdigit():
        # Field Number (with Collector)
        rows = Record.query.filter(Record.field_number.ilike(f'{q}%')).limit(10).all()
        for r in rows:
            if r.collector_id:
                item = {
                    'field_number': r.field_number or '',
                    'collector': r.collector.to_dict(with_meta=True) if r.collector else {},
                }
                item['meta'] = {
                    'term': 'field_number_with_collector',
                    'label': '採集號',
                    'display': '{} {}'.format(r.collector.display_name if r.collector else '', r.field_number),
                    'part': {
                        'field_number': {
                            'term': 'field_number',
                            'label': '採集號',
                            'display': r.field_number,
                        },
                    },
                }
            else:
                item = {
                    'field_number': r.field_number or '',
                }
                item['meta'] = {
                    'term': 'field_number',
                    'label': '採集號',
                    'display': r.field_number,
                }
            data.append(item)

        # calalogNumber
        rows = Unit.query.filter(Unit.accession_number.ilike(f'{q}%')).limit(10).all()
        for r in rows:
            #unit = r.to_dict()
            unit = {
                'value': r.accession_number or '',
            }
            unit['meta'] = {
                'term': 'accession_number',
                'label': '館號',
                'display': r.accession_number
            }
            data.append(unit)
    elif '-' in q:
        # TODO
        m = re.search(r'([0-9]+)-([0-9]+)', q)
        if m:
            data.append({
                'field_number_range': q,
                'term': 'field_number_range',
            })
    else:
        # Collector
        rows = Person.query.filter(Person.full_name.ilike(f'%{q}%') | Person.full_name_en.ilike(f'%{q}%')).limit(10).all()
        for r in rows:
            collector = r.to_dict(with_meta=True)
            data.append(collector)

        # Taxon
        rows = Taxon.query.filter(Taxon.full_scientific_name.ilike(f'{q}%') | Taxon.common_name.ilike(f'%{q}%')).limit(10).all()
        for r in rows:
            taxon = r.to_dict(with_meta=True)
            data.append(taxon)

        # Location
        rows = NamedArea.query.filter(NamedArea.name.ilike(f'{q}%') | NamedArea.name_en.ilike(f'%{q}%')).limit(10).all()
        for r in rows:
            loc = r.to_dict(with_meta=True)
            data.append(loc)

    resp = jsonify({
        'data': data,
    })
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Methods', '*')
    return resp


#@api.route('/search', methods=['GET'])
def get_search():
    view = request.args.get('view', '')
    total = request.args.get('total', None)

    payload = {
        'filter': json.loads(request.args.get('filter')) if request.args.get('filter') else {},
        'sort': json.loads(request.args.get('sort')) if request.args.get('sort') else {},
        'range': json.loads(request.args.get('range')) if request.args.get('range') else [0, 20],
    }

    stmt = make_specimen_query(payload['filter'])
    #print(payload['filter'], '====', flush=True)
    print(stmt, flush=True)
    base_stmt = stmt

    #if view != 'checklist':
    start = int(payload['range'][0])
    end = int(payload['range'][1])
    if start == 0 and end == -1:
        pass # no limit
    else:
        limit = min((end-start), 1000) # TODO: max query range
        stmt = stmt.limit(limit)
        if start > 0:
            stmt = stmt.offset(start)


    # =======
    # results
    # =======
    begin_time = time.time()
    result = session.execute(stmt)
    elapsed = time.time() - begin_time

    # -----------
    # count total
    # -----------
    elapsed_count = None
    if total is None:
        begin_time = time.time()
        subquery = base_stmt.subquery()
        count_stmt = select(func.count()).select_from(subquery)
        total = session.execute(count_stmt).scalar()
        elapsed_count = time.time() - begin_time

    # --------------
    # result mapping
    # --------------
    data = []
    begin_time = time.time()
    elapsed_mapping = None

    rows = result.all()
    for r in rows:
        unit = r[0]
        if record := r[1]:
            t = None
            if taxon_id := record.proxy_taxon_id:
                t = session.get(Taxon, taxon_id)

            image_url = ''
            try:
                accession_number_int = int(unit.accession_number)
                instance_id = f'{accession_number_int:06}'
                first_3 = instance_id[0:3]
                image_url = f'https://brmas-pub.s3-ap-northeast-1.amazonaws.com/hast/{first_3}/S_{instance_id}_s.jpg'
            except:
                pass

            taxon_text = record.proxy_taxon_scientific_name
            if record.proxy_taxon_common_name:
                taxon_text = f'{record.proxy_taxon_scientific_name} ({record.proxy_taxon_common_name})'
            data.append({
                'unit_id': unit.id if unit else '',
                'collection_id': record.id,
                'record_key': f'u{unit.id}' if unit else f'c{record.id}',
                # 'accession_number': unit.accession_number if unit else '',
                'accession_number': unit.accession_number if unit else '',
                'image_url': image_url,
                'field_number': record.field_number,
                'collector': record.collector.to_dict() if record.collector else '',
                'collect_date': record.collect_date.strftime('%Y-%m-%d') if record.collect_date else '',
                'taxon_text': taxon_text,
                'taxon': t.to_dict() if t else {},
                'named_areas': [x.to_dict() for x in record.named_areas],
                'locality_text': record.locality_text,
                'altitude': record.altitude,
                'altitude2': record.altitude2,
                'longitude_decimal': record.longitude_decimal,
                'latitude_decimal': record.latitude_decimal,
                'type_status': unit.type_status if unit and (unit.type_status and unit.pub_status=='P' and unit.type_is_published is True) else '',
            })
    elapsed_mapping = time.time() - begin_time

    resp = jsonify({
        'data': data,
        #'is_truncated': is_truncated,
        #'filter_tokens': filter_tokens,
        'total': total,
        'elapsed': elapsed,
        'debug': {
            'query': str(stmt),
            'elapsed_count': elapsed_count,
            'elapsed_mapping': elapsed_mapping,
            #'payload': payload,
        }
    })
    resp.headers.add('Access-Control-Allow-Origin', '*')
    resp.headers.add('Access-Control-Allow-Methods', '*')
    return resp


#@api.route('/people/<int:id>', methods=['GET'])
def get_person_detail(id):
    obj = session.get(Person, id)
    return jsonify(obj.to_dict(with_meta=True))

#@api.route('/people', methods=['GET'])
def get_person_list():
    #query = Person.query.select_from(Collection).join(Collection.people)
    query = Person.query.select_from(Collection)
    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        collector_id = None
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            # query = query.filter(Person.full_name.ilike(like_key) | Person.atomized_name['en']['given_name'].astext.ilike(like_key) | Person.atomized_name['en']['inherited_name'].astext.ilike(like_key))
            #query = query.filter(Person.full_name.ilike(like_key) | Person.full_name_en.ilike(like_key))
            query = query.filter(Person.sorting_name.ilike(like_key))
        if is_collector := filter_dict.get('is_collector', ''):
            query = query.filter(Person.is_collector==True)
        if is_identifier := filter_dict.get('is_identifier', ''):
            query = query.filter(Person.is_identifier==True)

        #if x := filter_dict.get('collector_id', ''):
        #    collector_id = x
        if x := filter_dict.get('id', ''):
            query = query.filter(Person.id.in_(x))
        if collection_id := filter_dict.get('collection_id', ''):
            query = query.filter(Collection.id==collection_id)

    if sort_str := request.args.get('sort'):
        sort_dict = json.loads(sort_str)
        for i in sort_dict:
            if 'sorting_name' in i:
                if i['sorting_name'] == 'desc':
                    query = query.order_by(desc('sorting_name'))
                else:
                    query = query.order_by('sorting_name')

    #print(query, flush=True)
    return jsonify(make_query_response(query))


#@api.route('/named_areas/<int:id>', methods=['GET'])
def get_named_area_detail(id):
    if obj := session.get(NamedArea, id):
        na = obj.to_dict(with_meta=True)
        if children := request.args.get('children'):
            na['area_classes'] = [{
                'id': x.id,
                'name': x.name,
                'area_class_id': x.area_class_id,
                'area_class_name': x.area_class.name,
            } for x in obj.get_parents()]

            # parent options
            na['options'] = {}
            for i in na['area_classes']:
                na_list = NamedArea.query.filter(NamedArea.parent_id==i['id']).all()
                na['options'][i['area_class_id']] = [{'id': x.id, 'text': x.display_name} for x in na_list]

            na['options'][obj.area_class_id] = [{'id': x.id, 'text': x.display_name} for x in NamedArea.query.filter(NamedArea.parent_id==obj.id).all()]

    return jsonify(na)


#@api.route('/named_areas', methods=['GET'])
def get_named_area_list():
    query = NamedArea.query

    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            query = query.filter(NamedArea.name.ilike(like_key) | NamedArea.name_en.ilike(like_key))
        if ids := filter_dict.get('id', ''):
            query = query.filter(NamedArea.id.in_(ids))
        if area_class_id := filter_dict.get('area_class_id', ''):
            query = query.filter(NamedArea.area_class_id==area_class_id)
        if parent_id := filter_dict.get('parent_id'):
            query = query.filter(NamedArea.parent_id==parent_id)

    return jsonify(make_query_response(query))


#@api.route('/taxa/<int:id>', methods=['GET'])
def get_taxa_detail(id):
    if obj := session.get(Taxon, id):
        taxon = obj.to_dict(with_meta=True)
        if children := request.args.get('children'):
            taxon['higher_taxon'] = [{'id': x.id, 'rank': x.rank } for x in obj.get_higher_taxon()]
            if taxon['rank'] == 'species':
                genus = TaxonRelation.query.filter(TaxonRelation.parent_id==taxon['higher_taxon'][1]['id'], TaxonRelation.depth==1).all()
                species = TaxonRelation.query.filter(TaxonRelation.parent_id==taxon['id'], TaxonRelation.depth==0).all()
                taxon['genus'] = [{'id': x.child.id, 'display_name': x.child.display_name} for x in genus]
                taxon['species'] = [{'id': x.child.id, 'display_name': x.child.display_name} for x in species]
            elif taxon['rank'] == 'genus':
                genus = TaxonRelation.query.filter(TaxonRelation.parent_id==taxon['higher_taxon'][0]['id'], TaxonRelation.depth==1).all()
                species = TaxonRelation.query.filter(TaxonRelation.parent_id==taxon['id'], TaxonRelation.depth==1).all()
                taxon['genus'] = [{'id': x.child.id, 'display_name': x.child.display_name} for x in genus]
                taxon['species'] = [{'id': x.child.id, 'display_name': x.child.display_name} for x in species]

        return jsonify(taxon)
    else:
        abort(404)

#@api.route('/taxa', methods=['GET'])
def get_taxa_list():
    query = Taxon.query
    if filter_str := request.args.get('filter', ''):
        filter_dict = json.loads(filter_str)
        if keyword := filter_dict.get('q', ''):
            like_key = f'{keyword}%' if len(keyword) == 1 else f'%{keyword}%'
            query = query.filter(Taxon.full_scientific_name.ilike(like_key) | Taxon.common_name.ilike(like_key))
        if ids := filter_dict.get('id', ''):
            query = query.filter(Taxon.id.in_(ids))
        if rank := filter_dict.get('rank'):
            query = query.filter(Taxon.rank==rank)
        if pid := filter_dict.get('parent_id'):
            if parent := session.get(Taxon, pid):
                depth = Taxon.RANK_HIERARCHY.index(parent.rank)
                taxa_ids = [x.id for x in parent.get_children(depth)]
                query = query.filter(Taxon.id.in_(taxa_ids))

    if sort_str := request.args.get('sort'):
        sort_dict = json.loads(sort_str)
        for i in sort_dict:
            if 'full_scientific_name' in i:
                if i['full_scientific_name'] == 'desc':
                    query = query.order_by(desc('full_scientific_name'))
                else:
                    query = query.order_by('full_scientific_name')

    if range_str := request.args.get('range'):
        range_dict = json.loads(range_str)
        if range_dict[0] != -1 and range_dict[1] != -1:
            query = query.slice(range_dict[0], range_dict[1])

    #print(query, flush=True)
    return jsonify(make_query_response(query))

#@api.route('/occurrence', methods=['GET'])
def get_occurrence():
    # required
    startCreated = request.args.get('startCreated', '')
    endCreated = request.args.get('endCreated', '')
    startModified = request.args.get('startModified', '')
    endModified = request.args.get('endModified', '')
    selfProduced = request.args.get('selfProduced', '')
    limit = request.args.get('limit', 300)
    offset = request.args.get('offset', 0)

    limit = int(limit)
    offset = int(offset)

    # optional
    collectionId= request.args.get('collectionId')
    occurrenceId= request.args.get('occurrenceId')

    stmt = select(
        Unit.id,
        Unit.accession_number,
        Unit.type_status,
        Unit.created,
        Unit.updated,
        Record.field_number,
        Record.collect_date,
        Person.full_name,
        Person.full_name_en,
        Record.longitude_decimal,
        Record.latitude_decimal,
        Record,
        Record.locality_text,
        Record.locality_text_en,
        Unit.kind_of_unit,
        Collection.label,
        Taxon.full_scientific_name,
        Taxon.common_name,
        Taxon.rank,
        Unit.guid,
        #func.string_agg(NamedArea.name, ', ')
    ) \
    .join(Record, Unit.record_id==Record.id) \
    .join(Person, Record.collector_id==Person.id, isouter=True) \
    .join(Collection, Record.collection_id==Collection.id) \
    .join(Taxon, Record.proxy_taxon_id==Taxon.id)
    #.join(NamedArea, Record.named_areas) \
    #.group_by(Unit.id, Record.id, Person.id, Collection.id, Taxon.id)

    stmt = stmt.where(Unit.pub_status=='P')
    stmt = stmt.where(Unit.accession_number!='') # 有 unit, 但沒有館號
    stmt = stmt.where(Collection.organization_id==1) # only get HAST

    # join named_area cause slow query

    #print(stmt, flush=True)
    #stmt2 = select(Unit.id, Record.id, Record.field_number, func.string_agg(NamedArea.name, ' | ')).join(NamedArea, Record.named_areas).group_by(Unit.id, Record.id).limit(20)
    #print(stmt2, flush=True)
    #r2 = session.execute(stmt2)
    #print(r2.all(), flush=True)

    try:
        if startCreated:
            dt = datetime.strptime(startCreated, '%Y%m%d')
            stmt = stmt.where(Unit.created >= dt)
        if endCreated:
            dt = datetime.strptime(endCreated, '%Y%m%d')
            stmt = stmt.where(Unit.created <= dt)
        if startModified:
            dt = datetime.strptime(startModified, '%Y%m%d')
            stmt = stmt.where(Unit.updated >= dt)
        if endModified:
            dt = datetime.strptime(endModified, '%Y%m%d')
            stmt = stmt.where(Unit.updated <= dt)
    except:
        return abort(400)

    # count total
    subquery = stmt.subquery()
    count_stmt = select(func.count()).select_from(subquery)
    total = session.execute(count_stmt).scalar()

    stmt = stmt.order_by(desc(Unit.created)).limit(limit).offset(offset)
    #print(stmt, flush=True)
    results = session.execute(stmt)

    rows = []
    for r in results.all():
        #print(r[19], flush=True)

        collector = ''
        if r[7] and r[8]:
            collector = f'{r[8]} ({r[7]})'
        elif r[7] and not r[8]:
            collector = r[7]
        elif r[8] and not r[7]:
            collector = r[8]

        na_list = []
        if record := r[11]:
            if named_areas := record.get_sorted_named_area_list():
                na_list = [x.display_name for x in named_areas]
        if x:= record.locality_text:
            na_list.append(x)
        if x:= record.locality_text_en:
            na_list.append(x)

        kind_of_unit = ''
        if x := Unit.KIND_OF_UNIT_MAP.get(r[14]):
            kind_of_unit = x

        row = {
            'occurrenceID': r[0],
            'collectionID': r[1],
            'scientificName': r[16] or '',
            'isPreferredName': r[17] or '',
            'taxonRank': r[18] or '',
            'typeStatus': r[2] or '',
            'eventDate': r[6].strftime('%Y%m%d') if r[6] else '',
            'verbatimCoordinateSystem':'DecimalDegrees',
            'verbatimSRS': 'EPSG:4326',
            #'coordinateUncertaintyInMeters': '',
            'dataGeneralizations': False,
            #'coordinatePrecision':
            'locality': ', '.join(na_list),
            'organismQuantity': 1,
            'organismQuantityType': '份',
	    'recordedBy': collector,
            'recordNumber':r[5] or '',
            #'taxonID': '',
            #'scientificNameID''
            'preservation': kind_of_unit,
            'datasetName': r[15],
            'resourceContacts': '鍾國芳、劉翠雅',
            #'references': f'https://{request.host}/specimens/{r[15]}:{r[1]}' if r[1] else '',
            'references': r[19] or '',
            'license': 'CC BY NC 4.0+', #'https://creativecommons.org/licenses/by-nc/4.0/legalcode',
            'mediaLicense': 'CC BY NC 4.0+', #'https://creativecommons.org/licenses/by-nc/4.0/legalcode',
            #'sensitiveCategory':
            'created': r[3].strftime('%Y%m%d'), #unit.created.strftime('%Y%m%d') if unit.created else '',
            'modified': r[4].strftime('%Y%m%d'), #unit.updated.strftime('%Y%m%d') if unit.updated else '',
        }

        if x := r[1]:
            #accession_number_int = int(x)
            #instance_id = f'{accession_number_int:06}'
            #first_3 = instance_id[0:3]
            #img_url = f'http://brmas-pub.s3-ap-northeast-1.amazonaws.com/hast/{first_3}/S_{instance_id}_m.jpg'
            #row['associatedMedia'] = img_url
            if mo := MultimediaObject.query.filter(MultimediaObject.unit_id==r[0]).first():
                # TODO may have many images
                row['associatedMedia'] = mo.file_url

        if r[9]:
            row['verbatimLongitude'] = float(r[9])
        if r[10]:
            row['verbatimLatitude'] = float(r[10])

        rows.append(row)


    results = {
        'data': rows,
        'messages': [
            '經緯度可能會有誤差，也有可能不一定是 WGS84',
            '授權需確認',
            'resourceContacts 需確認',
        ],
        'meta': {
            'total': total,
        }
    }

    # pagination
    if offset < total:
        num_pages = math.ceil(total / limit)
        page = math.floor( offset / limit ) + 1
    else:
        num_pages = 0
        page = 0

    results['meta']['pagination'] = {
        'num_pages': num_pages,
        'page': page,
        'num_per_page': limit,
    }

    return jsonify(results)


# API url maps
api.add_url_rule('/searchbar', 'get-searchbar', get_searchbar, ('GET'))
api.add_url_rule('/search', 'get-search', get_search, ('GET'))
api.add_url_rule('/people', 'get-person-list', get_person_list, ('GET'))
api.add_url_rule('/people/<int:id>', 'get-person-detail', get_person_detail, ('GET'))
api.add_url_rule('/taxa', 'get-taxa-list', get_taxa_list, ('GET'))
api.add_url_rule('/taxa/<int:id>', 'get-taxa-detail', get_taxa_detail, ('GET'))
api.add_url_rule('/named-areas', 'get-named-area-list', get_named_area_list, ('GET'))
api.add_url_rule('/named-areas/<int:id>', 'get-named-area-detail', get_named_area_detail, ('GET'))
api.add_url_rule('/occurrence', 'get-occurrence', get_occurrence) # for TBIA
