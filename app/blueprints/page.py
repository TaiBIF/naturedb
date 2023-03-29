
from flask import (
    Blueprint,
    render_template,
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

page = Blueprint('page', __name__)

@page.route('/zh/people')
@page.route('/en/people')
@page.route('/people')
def people():
    return render_template('page-people.html')

@page.route('/zh/visiting')
@page.route('/en/visiting')
@page.route('/visiting')
def visiting():
    return render_template('page-visiting.html')

@page.route('/zh/make-specimen')
@page.route('/en/make-specimen')
@page.route('/making-specimen')
def making_specimen():
    return render_template('page-making-specimen.html')

@page.route('/zh/about')
@page.route('/en/about')
@page.route('/about')
def about_page():
    return render_template('page-about.html')

@page.route('/zh/typp_specimens')
@page.route('/en/type_specimens')
@page.route('/type_specimens')
def type_specimens():

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

@page.route('/zh/related_links')
@page.route('/en/related_links')
@page.route('/related_links')
def related_links():
    org = session.get(Organization, 1)
    return render_template('related_links.html', organization=org)

@page.route('/articles/<article_id>')
def article_detail(article_id):
    article = Article.query.get(article_id)
    article.content_html = markdown.markdown(article.content)
    return render_template('article-detail.html', article=article)
