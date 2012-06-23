import logging
from urllib2 import urlopen, quote
import simplejson
from errbot.botplugin import BotPlugin
from errbot.jabberbot import botcmd

class BeerBot(BotPlugin):
    min_err_version = '1.3.0' # it needs the configuration feature

    def get_configuration_template(self):
        return {'BREWERY_DB_TOKEN' : '00112233445566778899aabbccddeeff'}

    def configure(self, configuration):
        if configuration:
            logging.info('config type %s' % type(configuration))
            if type(configuration) != dict:
                super(BeerBot, self).configure(None)
                raise Exception('Wrong configuration type')

            if not configuration.has_key('BREWERY_DB_TOKEN'):
                super(BeerBot, self).configure(None)
                raise Exception('Wrong configuration type, it should contain BREWERY_DB_TOKEN')
            if len(configuration) > 1:
                raise Exception('What else did you try to insert in my config ?')
        super(BeerBot, self).configure(configuration)

    BREWERY_DB_URL_SEARCH = 'http://api.brewerydb.com/v2/search?key=%s'

    @botcmd
    def beer(self, mess, args):
        """
        Find back a beer from the Brewery DB
        """
        if not args:
            return 'What beer do you want me to search for ?'
        if not self.config:
            return 'This plugin needs to be configured... run !config BeerBot'

        token = self.config.get('BREWERY_DB_TOKEN', None)
        if token is None:
            return 'Invalid configuration'

        content = urlopen(self.BREWERY_DB_URL_SEARCH%token + '&q=' + quote(args.strip()) + '&type=beer' )
        results = simplejson.load(content)
        for beer_data in results.get('data', []):
            name = beer_data.get('name', None)
            description = beer_data.get('description', '')
            labels = beer_data.get('labels', None)
            label_icon = labels.get('icon') if labels else None
            label_medium = labels.get('medium') if labels else None
            label_large = labels.get('large') if labels else None
            choosen_label = label_medium if label_medium else label_large if label_large else label_icon if label_icon else None
            style = beer_data.get('style', None)
            style_name = style.get('name', '') if style else None
            style_description = style.get('description', None) if style else None
            if choosen_label:
                self.send(mess.getFrom(), choosen_label, message_type=mess.getType())
            if name:
                shortdesc = name + '\n' + description
                self.send(mess.getFrom(), shortdesc, message_type=mess.getType())
            #if style_name:
            #    styledesc = style_name + '\n' + '-' * len(style_name) + '\n' + style_description
            #    self.send(mess.getFrom(), styledesc, message_type=mess.getType())
        return '/me is looking for your beer'