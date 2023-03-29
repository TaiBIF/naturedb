
from flask import (
    Blueprint,
    render_template,
    g,
    request,
)
from sqlalchemy import (
    select,
)
import markdown

from app.database import session
from app.models.site import (
    Organization,
    Article,
)
from app.models.collection import (
    Record,
    Unit,
    Taxon,
)
from app.utils import(
    get_cache,
    set_cache,
)
from flask_babel import get_translations

page = Blueprint('page', __name__)

@page.before_request
def set_locale():
    if 'en/' in request.path:
        setattr(g, 'LOCALE', 'en')
    elif 'zh/' in request.path:
        setattr(g, 'LOCALE', 'zh')

@page.route('/<lang>/people')
@page.route('/people')
def people(lang=''):
    return render_template('page-people.html')

@page.route('/<lang>/visiting')
@page.route('/visiting')
def visiting(lang=''):
    return render_template('page-visiting.html')

@page.route('/<lang>/make-specimen')
@page.route('/making-specimen')
def making_specimen(lang=''):
    return render_template('page-making-specimen.html')

@page.route('/<lang>/about')
@page.route('/about')
def about_page(lang=''):
    return render_template('page-about.html')

@page.route('/<lang>/type_specimens')
@page.route('/type_specimens')
def type_specimens(lang=''):

    CACHE_KEY = 'type-stat'
    CACHE_EXPIRE = 86400 # 1 day: 60 * 60 * 24
    unit_stats = None

    if x := get_cache(CACHE_KEY):
        unit_stats = x
    else:
        rows = Unit.query.filter(Unit.type_status != '', Unit.pub_status=='P', Unit.type_is_published==True).all()
        stats = { x[0]: 0 for x in Unit.TYPE_STATUS_CHOICES }
        units = []
        for u in rows:
            if u.type_status and u.type_status in stats:
                stats[u.type_status] += 1

            # prevent lazy loading
            units.append({
                'family': u.record.taxon_family.full_scientific_name if u.record.taxon_family else '',
                'scientific_name': u.record.proxy_taxon_scientific_name,
                'common_name': u.record.proxy_taxon_common_name,
                'type_reference_link': u.type_reference_link,
                'type_reference': u.type_reference,
                'specimen_url': u.specimen_url,
                'accession_number': u.accession_number,
                'type_status': u.type_status
            })
        units = sorted(units, key=lambda x: (x['family'], x['scientific_name']))
        unit_stats = {'units': units, 'stats': stats}
        set_cache(CACHE_KEY, unit_stats, CACHE_EXPIRE)

    return render_template('page-type-specimens.html', unit_stats=unit_stats)

@page.route('/<lang>/related_links')
@page.route('/related_links')
def related_links(lang=''):
    org = session.get(Organization, 1)
    return render_template('related_links.html', organization=org)

@page.route('/articles/<article_id>')
def article_detail(article_id):
    article = Article.query.get(article_id)
    article.content_html = markdown.markdown(article.content)
    return render_template('article-detail.html', article=article)
