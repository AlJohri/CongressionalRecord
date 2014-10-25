import httplib2
from datetime import datetime
from sunburnt import SolrInterface
from sunburnt import RawString
from sunburnt.search import SolrSearch
from dateutil import parser

local = True

if local == True:
  solr_url = "http://localhost:8983/solr/"
else:
  solr_url = "http://politicalframing.com:8983/solr"

h = httplib2.Http(cache="/var/tmp/solr_cache")
si = SolrInterface(url = solr_url, http_connection = h)

class Speech(object):

  def __init__(self, *args, **kwargs):
    self.id = kwargs.get('id')
    self.bills = kwargs.get('bills')
    self.biouguide = kwargs.get('biouguide')
    self.capitolwords_url = kwargs.get('capitolwords_url')
    self.chamber = kwargs.get('chamber')
    self.congress = kwargs.get('congress')
    self.date = kwargs.get('date')
    self.number = kwargs.get('number')
    self.order = kwargs.get('order')
    self.origin_url = kwargs.get('origin_url')
    self.pages = kwargs.get('pages')
    self.session = kwargs.get('session')
    self.speaker_first = kwargs.get('speaker_firstname')
    self.speaker_last = kwargs.get('speaker_lastname')
    self.speaker_party = kwargs.get('speaker_party')
    self.speaker_raw = kwargs.get('speaker_raw')
    self.speaker_state = kwargs.get('speaker_state')
    self.speaking = kwargs.get('speaking')
    self.title = kwargs.get('title')
    self.volume = kwargs.get('volume')

  @staticmethod
  def build_sunburnt_query(**kwargs):

    compulsory_params = {}
    optional_params = {}

    if kwargs.get('id'):
      compulsory_params['id'] = kwargs['id']
      solr_query = si.Q(**compulsory_params)
    elif kwargs.get('ids') and kwargs.get('phrase'):
      solr_query = si.Q()
      solr_query &= reduce(operator.or_, [si.Q(id=_id) for _id in kwargs['ids']])
    else:
    # elif kwargs.get('phrase'):
      compulsory_params['speaking'] = kwargs['phrase']

      kwargs['start_date'] = parser.parse(kwargs['start_date']) if kwargs.get('start_date') else datetime(1994,1,1)
      kwargs['end_date'] = parser.parse(kwargs['end_date']) if kwargs.get('end_date') else datetime.now()

      if kwargs.get('states'):
        kwargs['states'] = kwargs.get('states').split(',')
        optional_params['speaker_state'] = si.query()
        optional_params['speaker_state'] = reduce(operator.or_, [si.Q(speaker_state=state) for state in kwargs['states']])

      if kwargs.get('speaker_party'):
        compulsory_params['speaker_party'] = kwargs['speaker_party']

      if kwargs.get('congress'):
        compulsory_params['congress'] = kwargs['congress']

      compulsory_params['date__range'] = (kwargs['start_date'], kwargs['end_date'])
      compulsory_params['speaker_party__range'] = ("*", "*")

      solr_query = si.Q(**compulsory_params)

      if optional_params.get('speaker_state'):
        solr_query &= optional_params['speaker_state']

    solr_query = si.query(solr_query)
    solr_query = solr_query.exclude(speaker_party=None)

    return solr_query

  @staticmethod
  def get(rows, start, **kwargs):
    solr_query = Speech.build_sunburnt_query(**kwargs).paginate(rows=rows, start=start)
    response = solr_query.execute()
    speeches = response.result.docs
    current_count = response.result.numFound
    current_start = response.result.start
    speeches_dict = {
      'count': current_count,
      'start': current_start,
      'speeches': speeches
    }
    return speeches_dict
