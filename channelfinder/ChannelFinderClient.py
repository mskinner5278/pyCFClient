'''
Created on Feb 15, 2011

@author: shroffk
'''
from lib.restful_lib import Connection
from copy import copy
try: 
    from json import JSONDecoder, JSONEncoder
except ImportError: 
    from simplejson import JSONDecoder, JSONEncoder
from Channel import Channel, Property, Tag
try: 
    from collections import OrderedDict
except :
    from lib.myCollections import OrderedDict

    


class ChannelFinderClient(object):
    '''
    classdocs
    '''

    connection = None
    __jsonheader = {'content-type':'application/json', 'accept':'application/json'}    
    __channelsResource = 'resources/channels'
    __propertiesResource = 'resources/properties'
    __tagsResource = 'resources/tags'
 
    def __init__(self, BaseURL=None, username=None, password=None):
        '''
        Constructor
        '''
        try:
            
            self.__baseURL = BaseURL
            self.__userName = username
            self.__password = password
            self.connection = Connection(self.__baseURL, username=self.__userName, password=self.__password)
            resp = self.connection.request_get('/resources/tags', headers=copy(self.__jsonheader))
            if resp[u'headers']['status'] != '200':
                print 'error status' + resp[u'headers']['status']
                raise
#                raise Exception
#        raise exception detail instead of bypassing it
        except:
            raise
#        except Exception:
#            Exception.message
#            raise Exception
    
    def getAllChannels(self):
        if self.connection:
            resp = self.connection.request_get('/resources/channels', headers=copy(self.__jsonheader))
            if (resp[u'headers']['status'] != '404'):
                j = JSONDecoder().decode(resp[u'body'])
                return self.decodeChannels(j)
#        return a None if fail
        return None

    def add(self, **kwds):
        '''
        method to allow various types of add operations to add one or many channels, tags or properties\
        channel = single Channel obj
        channels = list of Channel obj
        tag = single Tag obj
        tags = list of Tag obj
        property = single Property obj
        properties = list of Property obj
        
        *** IMP NOTE: Following operation are destructive ***
        tag = Tag obj + channelName = channelName 
        will create and add the specified Tag to the channel with the name = channelName
        tag = Tag ogj + channelNames = list of channelName 
        will create and add the specified Tag to the channels with the names specified in channelNames
        and remove it from all other channels
        property = Property obj + channelName = channelName
        will create and add the specified Tag to the channel with the name = channelName
        property = Property obj + channelNames = list of channelName 
        will create and add the specified Tag to the channels with the names specified in channelNames
        and remove it from all other channels
        
        '''
        if not self.connection:
            raise Exception, 'Connection not created'
        if len(kwds) == 1:
            self.__hadleSingleAddParameter(**kwds)
        elif len(kwds) == 2:
            self.__handleMultipleAddParameters(**kwds)
        pass
    
    def __hadleSingleAddParameter(self, **kwds):
        if 'channel' in kwds :
            ch = kwds['channel']
#            print JSONEncoder().encode(self.encodeChannel(ch))
#            print self.__channelsResource + '/' + ch.Name
#            b = '{"channels": {"channel": {"@name": "pyChannelName", "@owner": "pyChannelOwner"}}}'
#            response = self.connection.request_put(self.__channelsResource + '/' + ch.Name, body=JSONEncoder().encode(self.encodeChannels([ch])), headers=copy(self.__jsonheader))
            response = self.connection.request_put(self.__channelsResource + '/' + ch.Name, \
                                                   body=JSONEncoder().encode(self.encodeChannel(ch)), \
                                                   headers=copy(self.__jsonheader))
#            print response
            self.__checkResponseState(response)
        elif 'channels' in kwds :
#            print JSONEncoder().encode(self.encodeChannels(kwds['channels']))
            response = self.connection.request_post(self.__channelsResource, \
                                                   body=JSONEncoder().encode(self.encodeChannels(kwds['channels'])), \
                                                   headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'tag' in kwds:
#            print self.__tagsResource + '/' + kwds['tag'].Name
#            print JSONEncoder().encode(self.encodeTag(kwds['tag']))
            response = self.connection.request_put(self.__tagsResource + '/' + kwds['tag'].Name, \
                                                   body=JSONEncoder().encode(self.encodeTag(kwds['tag'])), \
                                                   headers=copy(self.__jsonheader))
#            print response
            self.__checkResponseState(response)
        elif 'tags' in kwds:
#            print JSONEncoder().encode({'tags':{'tag':self.encodeTags(kwds['tags'])}})
            response = self.connection.request_post(self.__tagsResource, \
                                                    body=JSONEncoder().encode({'tags':{'tag':self.encodeTags(kwds['tags'])}}), \
                                                    headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'property' in kwds:
            response = self.connection.request_put(self.__propertiesResource + '/' + kwds['property'].Name, \
                                                   body=JSONEncoder().encode(self.encodeProperty(kwds['property'])) , \
                                                   headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'properties' in kwds:
            response = self.connection.request_post(self.__propertiesResource, \
                                                    body=JSONEncoder().encode({'properties':\
                                                                               {'property':\
                                                                                self.encodeProperties(kwds['properties'])}}) , \
                                                    headers=copy(self.__jsonheader))
            self.__checkResponseState(response)                                
        else:
            raise Exception, 'Incorrect Usage: unknown key'   
    
    def __handleMultipleAddParameters(self, **kwds):
        # add a tag to a channel
        if 'tag' in kwds and 'channelName' in kwds:
            channels = [Channel(kwds['channelName'], self.__userName, tags=[kwds['tag']])]
            response = self.connection.request_put(self.__tagsResource + '/' + kwds['tag'].Name, \
                                                    body=JSONEncoder().encode(self.encodeTag(kwds['tag'], withChannels=channels)), \
                                                    headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'tag' in kwds and 'channelNames' in kwds:
            channels = []
            for eachChannel in kwds['channelNames']:
                channels.append(Channel(eachChannel, self.__userName, tags=[kwds['tag']]))
            response = self.connection.request_put(self.__tagsResource + '/' + kwds['tag'].Name, \
                                                    body=JSONEncoder().encode(self.encodeTag(kwds['tag'], withChannels=channels)), \
                                                    headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'property' in kwds and 'channelName' in kwds:
            channels = [Channel(kwds['channelName'], self.__userName, properties=[kwds['property']])]
            response = self.connection.request_put(self.__propertiesResource + '/' + kwds['property'].Name, \
                                                   body=JSONEncoder().encode(self.encodeProperty(kwds['property'], withChannels=channels)), \
                                                   headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'property' in kwds and 'channelNames' in kwds:
            channels = []
            for eachChannel in kwds['channelNames']:
                channels.append(Channel(eachChannel, self.__userName, properties=[kwds['property']]))
            try:
                response = self.connection.request_put(self.__propertiesResource + '/' + kwds['property'].Name, \
                                                       body=JSONEncoder().encode(self.encodeProperty(kwds['property'], withChannels=channels)), \
                                                       headers=copy(self.__jsonheader))
            except Exception:
                print Exception
            self.__checkResponseState(response)
        else:
            raise Exception, 'Incorrect Usage: unknown keys'
    
    def __checkResponseState(self, r):
        '''
        simply checks the return status of the http response
        '''
        if not int(r[u'headers']['status']) <= 206:
                raise Exception, 'HTTP Error status: ' + r[u'headers']['status'] + r[u'body']
        return r
    
    def find(self, **kwds):
        '''
        Method allows you to query for a channel/s based on name, properties, tags
        name = channelNamePattern
        tagName = tagNamePattern                
        property = [(propertyName,propertyValuePattern)]
        
        returns a _list_ of matching Channels
        special pattern matching char 
        * for multiple char
        ? for single char
        
        To query for the existance of a tag or property use findTag and findProperty.
                
        TODO figure out how python/json will handle the multivalue maps
        to specify multiple patterns simple pass a ????        
        '''
        if not self.connection:
            raise Exception, 'Connection not created'
        if not len(kwds) > 0:
            raise Exception, 'Incorrect usage: atleast one parameter must be specified'
        url = self.__channelsResource
        args = {}
        if 'name' in kwds:
            args['~name'] = kwds['name']
        if 'tagName' in kwds:
            args['~tag'] = kwds['tagName']
        if 'property' in kwds:
            for prop in kwds['property']:
                args[prop[0]] = prop[1]
#        url = self.__channelsResource + self.createQueryURL(kwds)
        r = self.connection.request_get(url, args=args, headers=copy(self.__jsonheader))
        if self.__checkResponseState(r):
            return self.decodeChannels(JSONDecoder().decode(r[u'body']))
    
    @classmethod
    def createQueryURL(cls, parameters):
        url = []
        for parameterKey in parameters.keys():            
            if parameterKey == 'name':
                url.append('~name=' + str(parameters['name']))
            elif parameterKey == 'tagName':
                url.append('~tag=' + str(parameters['tagName']))
            elif parameterKey == 'property':
                if isinstance(parameters['property'], list):
                    for prop in parameters['property']:                        
                        if len(prop) == 1:
                            url.append(str(prop[0] + '=*'))
                        else:
                            url.append(str(prop[0] + '=' + prop[1]))
                else:
                    raise Exception, 'Incorrect usage: property=[("propName","propValPattern"),("propName","propValPatter")]'                    
            else:
                raise Exception, 'Incorrect usage: unknow key ' + parameterKey
        return '?' + '&'.join(url)
            
    def findTag(self, tagName):
        '''
        Searches for the _exact_ tagName and returns a single Tag object if found
        '''
        url = self.__tagsResource + '/' + tagName
        r = self.connection.request_get(url, headers=copy(self.__jsonheader))
#        JSONDecoder().decode(r[u'body'])
#        print r
        if r[u'headers']['status'] == '404':
            return None
        elif self.__checkResponseState(r):
            return self.decodeTag(JSONDecoder().decode(r[u'body']))
        else:
            return None
               
    
    def findProperty(self, propertyName):
        '''
        Searches for the _exact_ propertyName and return a single Property object if found
        '''
        url = self.__propertiesResource + '/' + propertyName
        r = self.connection.request_get(url, headers=copy(self.__jsonheader))
        if r[u'headers']['status'] == '404':
            return None
        elif self.__checkResponseState(r):
            return self.decodeProperty(JSONDecoder().decode(r[u'body']))
        else:
            return None
        
    def getAllTags(self):
        '''
        return a list of all the Tags present - even the ones not associated w/t any channel
        '''
        url = self.__tagsResource
        r = self.connection.request_get(url, headers=copy(self.__jsonheader))       
        if self.__checkResponseState(r):
            return self.decodeTags(JSONDecoder().decode(r[u'body']))
    
    def getAllProperties(self):
        '''
        return a list of all the Properties present - even the ones not associated w/t any channel
        '''
        url = self.__propertiesResource
        r = self.connection.request_get(url, headers=copy(self.__jsonheader))
        if self.__checkResponseState(r):
            return self.decodeProperties(JSONDecoder().decode(r[u'body']))
        
    def remove(self, **kwds):
        '''
        Method to delete a channel, property, tag
        channelName = name of channel to be removed
        tagName = tag name of the tag to be removed from all channels
        propertyName = property name of property to be removed from all channels
        
        tag = Tag obj + channelName = channelName 
        -remove the tag from the specified channel
        tag = Tag ogj + channelNames = list of channelName 
        - remove the tag from all the channels specified in the channelNames list
        property = Property obj + channelName = channelName
        - remove the property from the specified channel
        roperty = Property obj + channelNames = list of channelName 
        - remove the property from all the channels in the channelNames list
        '''
        if not self.connection:
            raise Exception, 'Connection not created'
        if len(kwds) == 1:
            self.__handleSingleRemoveParameter(**kwds)
        elif len(kwds) == 2:
            self.__handleMultipleRemoveParameters(**kwds)
        else:
            raise Exception, 'incorrect usage: Delete a single Channel/tag/property'
    
    def __handleSingleRemoveParameter(self, **kwds):
        if 'channelName' in kwds:
            url = self.__channelsResource + '/' + kwds['channelName']
            response = self.connection.request_delete(url, headers=copy(self.__jsonheader))   
            self.__checkResponseState(response)
            pass
        elif 'tagName' in kwds:
            url = self.__tagsResource + '/' + kwds['tagName']
            response = self.connection.request_delete(url, headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
            pass
        elif 'propertyName' in kwds:
            url = self.__propertiesResource + '/' + kwds['propertyName']
            response = self.connection.request_delete(url, headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
            pass
        else:
            raise Exception, ' unkown key use channelName, tagName or proprtyName'
    
    def __handleMultipleRemoveParameters(self, **kwds):
        if 'tag' in kwds and 'channelName' in kwds:
            response = self.connection.request_delete(self.__tagsResource + '/' + kwds['tag'].Name + '/' + kwds['channelName'], \
                                                     headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'tag' in kwds and 'channelNames' in kwds:
            # find channels with the tag
            channelsWithTag = self.find(tagName=kwds['tag'].Name)
            # remove channels from which tag is to be removed
            channelNames = [channel.Name for channel in channelsWithTag if channel.Name not in  kwds['channelNames']]
            self.add(tag=kwds['tag'], channelNames=channelNames)
        elif 'property' in kwds and 'channelName' in kwds:
            response = self.connection.request_delete(self.__propertiesResource + '/' + kwds['property'].Name + '/' + kwds['channelName'], \
                                                      headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        elif 'property' in kwds and 'channelNames' in kwds:
            channelsWithProp = self.find(property=[(kwds['property'].Name, '*')])
            channelNames = [channel.Name for channel in channelsWithProp if channel.Name not in kwds['channelNames']]
            self.add(property=kwds['property'], channelNames=channelNames)        
        else:
            raise Exception, ' unkown keys'

#===============================================================================
# Update methods
#===============================================================================
    def update(self, **kwds):
        '''
        channel = the new channel obj
        originalChannelName = the original name of the channel to be updated
        if not specified the name is extracted from the channel obj
        
        property = the new property obj
        originalPropertyName = the original name of the property to be updated
        if not specified the name is extracted from the property obj
        '''
        if len(kwds) != 2:
            raise Exception, 'incorrect usage'
        if 'channel' in kwds:
            ch = kwds['channel']
            channelName = ch.Name
            if 'originalChannelName' in kwds:
                channelName = kwds['originalChannelName']
            url = self.__channelsResource + '/' + channelName
            try:
                response = self.connection.request_post(url, \
                                                        body=JSONEncoder().encode(self.encodeChannel(ch)) , \
                                                        headers=copy(self.__jsonheader))                
            except Exception:
                print Exception
            self.__checkResponseState(response)
        elif 'property' in kwds:
            prop = kwds['property']
            propName = prop.Name
            if 'originalPropertyName' in kwds:
                propName = kwds['originalPropertyName']
                print JSONEncoder().encode(self.encodeProperty(prop))
            url = self.__propertiesResource + '/' + propName
            response = self.connection.request_post(url, \
                                                    body=JSONEncoder().encode(self.encodeProperty(prop)), \
                                                    headers=copy(self.__jsonheader))
            self.__checkResponseState(response)
        else:
            raise Exception, ' unkown keys'

#===============================================================================
# Methods for encoding decoding will be make private
#===============================================================================
    @classmethod
    def decodeChannels(cls, body):
        '''
        '''
        if not body[u'channels']:
            return None
        channels = []
        # if List then Multiplce channels are present in the body
        if isinstance(body[u'channels']['channel'], list):
            for channel in body['channels']['channel']:
                channels.append(cls.decodeChannel(channel))
        # if Dict the single channel present in the body
        elif isinstance(body[u'channels']['channel'], dict):
            channels.append(cls.decodeChannel(body[u'channels']['channel']))
        return channels

    @classmethod
    def decodeChannel(self, body):
        return Channel(body[u'@name'], body[u'@owner'], properties=self.decodeProperties(body), tags=self.decodeTags(body))
    
    @classmethod
    def decodeProperties(cls, body):
        ## TODO handle the case where there is a single property dict
        if body[u'properties'] and body[u'properties']['property']:
            properties = []
            if isinstance(body[u'properties']['property'], list):                
                for validProperty in [ property for property in body[u'properties']['property'] if '@name' in property and '@owner' in property]:
                        properties.append(cls.decodeProperty(validProperty))
            elif isinstance(body[u'properties']['property'], dict):
                properties.append(cls.decodeProperty(body[u'properties']['property']))
            return properties
        else:
            return None
        
    @classmethod
    def decodeProperty(cls, propertyBody):
        if '@value' in propertyBody:
            return Property(propertyBody['@name'], propertyBody['@owner'], propertyBody['@value'])
        else:
            return Property(propertyBody['@name'], propertyBody['@owner'])
    
    @classmethod
    def decodeTags(cls, body):
        ## TODO handle the case where there is a single tag dict
        if body[u'tags'] and body[u'tags']['tag']:
            tags = []
            if isinstance(body[u'tags']['tag'], list):
                for validTag in [ tag for tag in body[u'tags']['tag'] if '@name' in tag and '@owner' in tag]:
                    tags.append(cls.decodeTag(validTag))
            elif isinstance(body[u'tags']['tag'], dict):
                tags.append(cls.decodeTag(body[u'tags']['tag']))
            return tags
        else:
            return None    
    
    @classmethod
    def decodeTag(cls, tagBody):
        return Tag(tagBody['@name'], tagBody['@owner'])
    
    @classmethod    
    def encodeChannels(cls, channels):
        '''
        encodes a list of Channel
        '''
        ret = {u'channels':{}}
        if len(channels) == 1:
            ret[u'channels'] = {u'channel':cls.encodeChannel(channels[0])}
        elif len (channels) > 1:
            ret[u'channels'] = {u'channel':[]}
            for channel in channels:
                if issubclass(channel.__class__, Channel):                
                    ret[u'channels'][u'channel'].append(cls.encodeChannel(channel))
        return ret

    @classmethod
    def encodeChannel(cls, channel):
        d = {}
        d['@name'] = channel.Name
        d['@owner'] = channel.Owner
        if channel.Properties:
            d['properties'] = {'property':cls.encodeProperties(channel.Properties)}            
        if channel.Tags:
            d['tags'] = {'tag':cls.encodeTags(channel.Tags)}
        return d
    
    @classmethod
    def encodeProperties(cls, properties):
        d = []
        for validProperty in [ property for property in properties if issubclass(property.__class__, Property)]:
                d.append(cls.encodeProperty(validProperty))
        return d
    
    @classmethod
    def encodeProperty(cls, property, withChannels=None):
        if not withChannels:
            if property.Value:
                return {'@name':str(property.Name), '@value':property.Value, '@owner':property.Owner}
            else:
                return {'@name':str(property.Name), '@owner':property.Owner}
        else:
            d = OrderedDict([('@name', str(property.Name)), ('@value', property.Value), ('@owner', property.Owner)])
            d.update(cls.encodeChannels(withChannels))
            return d
    
    @classmethod
    def encodeTags(cls, tags):
        d = []
        for validTag in [ tag for tag in tags if issubclass(tag.__class__, Tag)]:
            d.append(cls.encodeTag(validTag))
        return d
        
    @classmethod
    def encodeTag(cls, tag, withChannels=None):
        if not withChannels:
            return {'@name':tag.Name, '@owner':tag.Owner}
        else:
            d = OrderedDict([('@name', tag.Name), ('@owner', tag.Owner)])
            d.update(cls.encodeChannels(withChannels))
            return d
        


        