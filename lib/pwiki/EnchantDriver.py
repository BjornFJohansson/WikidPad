# pyenchant
#
# Copyright (C) 2004-2005, Ryan Kelly
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.
#
# In addition, as a special exception, you are
# given permission to link the code of this program with
# non-LGPL Spelling Provider libraries (eg: a MSFT Office
# spell checker backend) and distribute linked combinations including
# the two.  You must obey the GNU Lesser General Public License in all
# respects for all of the code used other than said providers.  If you modify
# this file, you may extend this exception to your version of the
# file, but you are not obligated to do so.  If you do not wish to
# do so, delete this exception statement from your version.
# 
# 
# 
# Modified to work with WikidPad and to reduce dependencies
#    2006 by Michael Butscher
"""
    enchant:  Access to the enchant spellchecking library

    This module provides several classes for performing spell checking
    via the Enchant spellchecking library.  For more details on Enchant,
    visit the project website:

        http://www.abisource.com/enchant/

    Spellchecking is performed using 'Dict' objects, which represent
    a language dictionary.  Their use is best demonstrated by a quick
    example:

        >>> import enchant
        >>> d = enchant.Dict("en_US")   # create dictionary for US English
        >>> d.check("enchant")
        True
        >>> d.check("enchnt")
        False
        >>> d.suggest("enchnt")
        ['enchant', 'enchants', 'enchanter', 'penchant', 'incant', 'enchain', 'enchanted']

    Languages are identified by standard string tags such as "en" (English)
    and "fr" (French).  Specific language dialects can be specified by
    including an additional code - for example, "en_AU" refers to Australian
    English.  The later form is preferred as it is more widely supported.

    To check whether a dictionary exists for a given language, the function
    'dict_exists' is available.  Dictionaries may also be created using the
    function 'request_dict'.

    A finer degree of control over the dictionaries and how they are created
    can be obtained using one or more 'Broker' objects.  These objects are
    responsible for locating dictionaries for a specific language.
    
    Unicode strings are supported transparently, as they are throughout
    Python - if a unicode string is given as an argument, the result will
    be a unicode string.  Note that Enchant works in UTF-8 internally,
    so passing an ASCII string to a dictionary for a language requiring
    Unicode may result in UTF-8 strings being returned.

    Errors that occur in this module are reported by raising 'Error'.

"""

# Make version info available
__ver_major__ = 1
__ver_minor__ = 1
__ver_patch__ = 5
__ver_sub__ = ""
__version__ = "%d.%d.%d%s" % (__ver_major__,__ver_minor__,
                              __ver_patch__,__ver_sub__)

import enchant._enchant as _e

import os
import sys
import warnings

class Error(Exception):
    """Base exception class for the enchant module."""
    pass

class DictNotFoundError(Error):
    """Exception raised when a requested dictionary could not be found."""
    pass

class ProviderDesc(object):
    """Simple class describing an Enchant provider.
    Each provider has the following information associated with it:

        * name:        Internal provider name (e.g. "aspell")
        * desc:        Human-readable description (e.g. "Aspell Provider")
        * file:        Location of the library containing the provider

    """

    def __init__(self,name,desc,file):
        self.name = name
        self.desc = desc
        self.file = file

    def __str__(self):
        return "<Enchant: %s>" % self.desc

    def __repr__(self):
        return str(self)

    def __eq__(self,pd):
        """Equality operator on ProviderDesc objects."""
        return (self.name == pd.name and \
                self.desc == pd.desc and \
                self.file == pd.file)
                
    def __hash__(self):
        """Hash operator on ProviderDesc objects."""
        return hash(self.name + self.desc + self.file)


class _EnchantObject(object):
    """Base class for enchant objects.
    
    This class implements some general functionality for interfacing with
    the '_enchant' C-library in a consistent way.  All public objects
    from the 'enchant' module are subclasses of this class.
    
    All enchant objects have an attribute '_this' which contains the
    pointer to the underlying C-library object.  The method '_check_this'
    can be called to ensure that this point is not None, raising an
    exception if it is.
    """
    
    def __init__(self):
        """_EnchantObject constructor."""
        self._this = None
        
    def _check_this(self,msg=None):
         """Check that self._this is set to a pointer, rather than None."""
         if msg is None:
            msg = "%s unusable: the underlying C-library object has been freed."
            msg = msg % (self.__class__.__name__,)
         if self._this is None:
            raise Error(msg)
             
    def _raise_error(self,default="Unspecified Error",eclass=Error):
         """Raise an exception based on available error messages.
         This method causes an Error to be raised.  Subclasses should
         override it to retreive an error indication from the underlying
         API if possible.  If such a message cannot be retreived, the
         argument value <default> is used.  The class of the exception
         can be specified using the argument <eclass>
         """
         raise eclass(default)



class Broker(_EnchantObject):
    """Broker object for the Enchant spellchecker.

    Broker objects are responsible for locating and managing dictionaries.
    Unless custom functionality is required, there is no need to use Broker
    objects directly. The 'enchant' module provides a default broker object
    so that 'Dict' objects can be created directly.

    The most important methods of this class include:

        * dict_exists:   check existence of a specific language dictionary
        * request_dict:  obtain a dictionary for specific language
        * set_ordering:  specify which dictionaries to try for for a
                         given language.

    """

    # Because of the way the underlying enchant library caches dictionary
    # objects, it's dangerous to free dictionaries when more than one has
    # been created for the same language.  To work around this transparently,
    # keep track of how many Dicts have been created for each language.
    # Only call the underlying dict_free when this reaches zero.  This is
    # done in the __live_dicts attribute.

    def __init__(self):
        """Broker object constructor.
        
        This method is the constructor for the 'Broker' object.  No
        arguments are required.
        """
        _EnchantObject.__init__(self)
        self._this = _e.enchant_broker_init()
        if not self._this:
            raise Error("Could not initialise an enchant broker.")
        self.__live_dicts = {}

    def __del__(self):
        """Broker object destructor."""
        # Calling _free() might fail if python is shutting down
        try:
            self._free()
        except AttributeError:
            pass
            
    def _raise_error(self,default="Unspecified Error",eclass=Error):
        """Overrides _EnchantObject._raise_error to check broker errors."""
        err = _e.enchant_broker_get_error(self._this)
        if err == "" or err is None:
            raise eclass(default)
        raise eclass(err)

    def _free(self):
        """Free system resource associated with a Broker object.
        
        This method can be called to free the underlying system resources
        associated with a Broker object.  It is called automatically when
        the object is garbage collected.  If called explicitly, the
        Broker and any associated Dict objects must no longer be used.
        """
        if self._this is not None:
            _e.enchant_broker_free(self._this)
            self._this = None
            self.__live_dicts.clear()
            
    def __inc_live_dicts(self,tag):
        """Increment the count of live Dict objects for the given tag.
        Returns the new count of live Dicts.
        """
        try:
            self.__live_dicts[tag] += 1
        except KeyError:
            self.__live_dicts[tag] = 1
        assert(self.__live_dicts[tag] > 0)
        return self.__live_dicts[tag]

    def __dec_live_dicts(self,tag):
        """Decrement the count of live Dict objects for the given tag.
        Returns the new count of live Dicts.
        """
        try:
            self.__live_dicts[tag] -= 1
        except KeyError:
            self.__live_dicts[tag] = 0
        assert(self.__live_dicts[tag] >= 0)
        return self.__live_dicts[tag]
        
    def request_dict(self,tag=None):
        """Request a Dict object for the language specified by <tag>.
        
        This method constructs and returns a Dict object for the
        requested language.  'tag' should be a string of the appropriate
        form for specifying a language, such as "fr" (French) or "en_AU"
        (Australian English).  The existence of a specific language can
        be tested using the 'dict_exists' method.
        
        If <tag> is not given or is None, an attempt is made to determine
        the current language in use.  If this cannot be determined, Error
        is raised.
        
        NOTE:  this method is functionally equivalent to calling the Dict()
               constructor and passing in the <broker> argument.
               
        """
        return Dict(tag,self)

    def _request_dict_data(self,tag):
        """Request raw C-object data for a dictionary.
        This method call passes on the call to the C library, and does
        some internal bookkeeping.
        """
        self._check_this()
        new_dict = _e.enchant_broker_request_dict(self._this,tag)
        if new_dict is None:
            eStr = "Dictionary for language '%s' could not be found"
            self._raise_error(eStr % (tag,),DictNotFoundError)
        # Determine normalized tag, for live count
        key = self.__describe_dict(new_dict)[0]
        self.__inc_live_dicts(key)
        return new_dict

    def request_pwl_dict(self,pwl):
        """Request a Dict object for a personal word list.
        
        This method behaves as 'request_dict' but rather than returning
        a dictionary for a specific language, it returns a dictionary
        referencing a personal word list.  A personal word list is a file
        of custom dictionary entries, one word per line.
        """
        self._check_this()
        new_dict = _e.enchant_broker_request_pwl_dict(self._this,pwl)
        if new_dict is None:
            eStr = "Personal Word List file '%s' could not be loaded"
            self._raise_error(eStr % (pwl,))
        # Find normalized filename, use as key
        key = self.__describe_dict(new_dict)[3]
        self.__inc_live_dicts(key)
        d = Dict(False)
        d._switch_this(new_dict,self)
        return d

    def _free_dict(self,dict):
        """Free memory associated with a dictionary.
        
        This method frees system resources associated with a Dict object.
        It is equivalent to calling the object's 'free' method.  Once this
        method has been called on a dictionary, it must not be used again.
        """
        self._check_this()
        # Lookup key differs if it's a PWL or not
        if dict.tag.lower() == "personal wordlist":
            key = dict.provider.file
        else:
            key = dict.tag
        if self.__dec_live_dicts(key) == 0:
            _e.enchant_broker_free_dict(self._this,dict._this)
        dict._this = None
        dict._broker = None

    def dict_exists(self,tag):
        """Check availability of a dictionary.
        
        This method checks whether there is a dictionary available for
        the language specified by 'tag'.  It returns True if a dictionary
        is available, and False otherwise.
        """
        self._check_this()
        val = _e.enchant_broker_dict_exists(self._this,tag)
        return bool(val)

    def set_ordering(self,tag,ordering):
        """Set dictionary preferences for a language.
        
        The Enchant library supports the use of multiple dictionary programs
        and multiple languages.  This method specifies which dictionaries
        the broker should prefer when dealing with a given language.  'tag'
        must be an appropriate language specification and 'ordering' is a
        string listing the dictionaries in order of preference.  For example
        a valid ordering might be "aspell,myspell,ispell".
        The value of 'tag' can also be set to "*" to set a default ordering
        for all languages for which one has not been set explicitly.
        """
        self._check_this()
        if type(ordering) == unicode:
            ordering = ordering.encode("utf-8")
        _e.enchant_broker_set_ordering(self._this,tag,ordering)

    def describe(self):
        """Return list of provider descriptions.
        
        This method returns a list of descriptions of each of the
        dictionary providers available.  Each entry in the list is a 
        ProviderDesc object.
        """
        self._check_this()
        self.__describe_result = []
        _e.enchant_broker_describe_py(self._this,self.__describe_callback)
        return [ ProviderDesc(*r) for r in self.__describe_result]

    def __describe_callback(self,name,desc,file):
        """Collector callback for dictionary description.
        
        This method is used as a callback into the _enchant function
        'enchant_broker_describe_py'.  It collects the given arguments in
        a tuple and appends them to the list '__describe_result'.
        """
        name = name.decode("utf-8")
        desc = desc.decode("utf-8")
        file = file.decode("utf-8")
        self.__describe_result.append((name,desc,file))
        
    def list_dicts(self):
        """Return list of available dictionaries.
        
        This method returns a list of dictionaries available to the
        broker.  Each entry in the list is a two-tuple of the form:
            
            (tag,provider)
        
        where <tag> is the language lag for the dictionary and
        <provider> is a ProviderDesc object describing the provider
        through which that dictionary can be obtained.
        """
        self._check_this()
        self.__list_dicts_result = []
        _e.enchant_broker_list_dicts_py(self._this,self.__list_dicts_callback)
        return [ (r[0],ProviderDesc(*r[1])) for r in self.__list_dicts_result]
    
    def __list_dicts_callback(self,tag,name,desc,file):
        """Collector callback for listing dictionaries.
        
        This method is used as a callback into the _enchant function
        'enchant_broker_list_dicts_py'.  It collects the given arguments into
        an appropriate tuple and appends them to '__list_dicts_result'.
        """
        name = name.decode("utf-8")
        desc = desc.decode("utf-8")
        file = file.decode("utf-8")
        self.__list_dicts_result.append((tag,(name,desc,file)))
 
    def list_languages(self):
        """List languages for which dictionaries are available.
        
        This function returns a list of language tags for which a
        dictionary is available.
        """
        langs = []
        for (tag,prov) in self.list_dicts():
            if tag not in langs:
                langs.append(tag)
        return langs
        
    def __describe_dict(self,dict_data):
        """Get the description tuple for a dict data object.
        <dict_data> must be a C-library pointer to an enchant dictionary.
        The return value is a tuple of the form:
                (<tag>,<name>,<desc>,<file>)
        """
        # Define local callback function
        cb_result = []
        def cb_func(tag,name,desc,file):
            name = name.decode("utf-8")
            desc = desc.decode("utf-8")
            file = file.decode("utf-8")
            cb_result.append((tag,name,desc,file))
        # Actual call describer function
        _e.enchant_dict_describe_py(dict_data,cb_func)
        return cb_result[0]
        

class Dict(_EnchantObject):
    """Dictionary object for the Enchant spellchecker.

    Dictionary objects are responsible for checking the spelling of words
    and suggesting possible corrections.  Each dictionary is owned by a
    Broker object, but unless a new Broker has explicitly been created
    then this will be the 'enchant' module default Broker and is of little
    interest.

    The important methods of this class include:

        * check():              check whether a word id spelled correctly
        * suggest():            suggest correct spellings for a word
        * add_to_session():     add a word to the current spellcheck session
        * add_to_pwl():         add a word to the personal dictionary
        * store_replacement():  indicate a replacement for a given word

    Information about the dictionary is available using the following
    attributes:

        * tag:        the language tag of the dictionary
        * provider:   a ProviderDesc object for the dictionary provider
    
    """

    def __init__(self,tag=None,broker=None):
        """Dict object constructor.
        
        A dictionary belongs to a specific language, identified by the
        string <tag>.  If the tag is not given or is None, an attempt to
        determine the language currently in use is made using the 'locale'
        module.  If the current language cannot be determined, Error is raised.

        If <tag> is instead given the value of False, a 'dead' Dict object
        is created without any reference to a language.  This is typically
        only useful within PyEnchant itself.  Any other non-string value
        for <tag> raises Error.
        
        Each dictionary must also have an associated Broker object which
        obtains the dictionary information from the underlying system. This
        may be specified using <broker>.  If not given, the default broker
        is used.
        """
        # Superclass initialisation
        _EnchantObject.__init__(self)
        # Initialise object attributes to None
        self._broker = None
        self.tag = None
        self.provider = None
        # Create dead object if False was given
        if tag is False:
            self._this = None
        else:
            if tag is None:
                err = "No tag specified"
                raise Error(err)
            # Use module-level broker if none given
            if broker is None:
                broker = _broker
            # Use the broker to get C-library pointer data
            self._switch_this(broker._request_dict_data(tag),broker)

    def __del__(self):
        """Dict object desstructor."""
        # Calling free() might fail if python is shutting down
        try:
            self._free()
        except AttributeError:
            pass
            
    def _switch_this(self,this,broker):
        """Switch the underlying C-library pointer for this object.
        
        As all useful state for a Dict is stored by the underlying C-library
        pointer, it is very convenient to allow this to be switched at
        run-time.  Pass a new dict data object into this method to affect
        the necessary changes.  The creating Broker object (at the Python
        level) must also be provided.
                
        This should *never* *ever* be used by application code.  It's
        a convenience for developers only, replacing the clunkier <data>
        parameter to __init__ from earlier versions.
        """
        # Free old dict data
        Dict._free(self)
        # Hook in the new stuff
        self._this = this
        self._broker = broker
        # Update object properties
        desc = self.__describe(check_this=False)
        self.tag = desc[0]
        self.provider = ProviderDesc(*desc[1:])
            
    def _check_this(self,msg=None):
        """Extend _EnchantObject._check_this() to check Broker validity.
        
        It is possible for the managing Broker object to be freed without
        freeing the Dict.  Thus validity checking must take into account
        self._broker._this as well as self._this.
        """
        if self._broker is None or self._broker._this is None:
            self._this = None
        _EnchantObject._check_this(self,msg)

    def _raise_error(self,default="Unspecified Error",eclass=Error):
        """Overrides _EnchantObject._raise_error to check dict errors."""
        err = _e.enchant_dict_get_error(self._this)
        if err == "" or err is None:
            raise eclass(default)
        raise eclass(err)

    def _free(self):
        """Free the system resources associated with a Dict object.
        
        This method frees underlying system resources for a Dict object.
        Once it has been called, the Dict object must no longer be used.
        It is called automatically when the object is garbage collected.
        """
        if self._broker is not None:
            self._broker._free_dict(self)

    def check(self,word):
        """Check spelling of a word.
        
        This method takes a word in the dictionary language and returns
        True if it is correctly spelled, and false otherwise.
        """
        self._check_this()
        if type(word) == unicode:
            inWord = word.encode("utf-8")
        else:
            inWord = word
        val = _e.enchant_dict_check(self._this,inWord,len(inWord))
        if val == 0:
            return True
        if val > 0:
            return False
        self._raise_error()

    def suggest(self,word):
        """Suggest possible spellings for a word.
        
        This method tries to guess the correct spelling for a given
        word, returning the possibilities in a list.
        """
        self._check_this()
        if type(word) == unicode:
            inWord = word.encode("utf-8")
        else:
            inWord = word
        suggs = _e.enchant_dict_suggest_py(self._this,inWord,len(inWord))
        if type(word) == unicode:
            uSuggs = [w.decode("utf-8") for w in suggs]
            return uSuggs
        return suggs

    def add_to_personal(self,word):
        """Add a word to the user's personal dictionary.
        
        NOTE: this method is being deprecated in favour of
        add_to_pwl.  Please change code using add_to_personal
        to use add_to_pwl instead.  This change mirrors a
        change in the Enchant C API.
        
        """
        warnings.warn("add_to_personal is deprecated, please use add_to_pwl",
                      DeprecationWarning)
        self.add_to_pwl(word)

    def add_to_pwl(self,word):
        """Add a word to the user's personal dictionary."""
        self._check_this()
        if type(word) == unicode:
            inWord = word.encode("utf-8")
        else:
            inWord = word
        _e.enchant_dict_add_to_pwl(self._this,inWord,len(inWord))

    def add_to_session(self,word):
        """Add a word to the session list."""
        self._check_this()
        if type(word) == unicode:
            inWord = word.encode("utf-8")
        else:
            inWord = word
        _e.enchant_dict_add_to_session(self._this,inWord,len(inWord))

    def is_in_session(self,word):
        """Check whether a word is in the session list."""
        self._check_this()
        if type(word) == unicode:
            inWord = word.encode("utf-8")
        else:
            inWord = word
        return _e.enchant_dict_is_in_session(self._this,inWord,len(inWord))

    def store_replacement(self,mis,cor):
        """Store a replacement spelling for a miss-spelled word.
        
        This method makes a suggestion to the spellchecking engine that the 
        miss-spelled word <mis> is in fact correctly spelled as <cor>.  Such
        a suggestion will typically mean that <cor> appears early in the
        list of suggested spellings offered for later instances of <mis>.
        """
        self._check_this()
        if type(mis) == unicode:
            inMis = mis.encode("utf-8")
        else:
            inMis = mis
        if type(cor) == unicode:
            inCor = cor.encode("utf-8")
        else:
            inCor = cor
        _e.enchant_dict_store_replacement(self._this,inMis,len(inMis),inCor,len(inCor))

    def __describe(self,check_this=True):
        """Return a tuple describing the dictionary.
        
        This method returns a four-element tuple describing the underlying
        spellchecker system providing the dictionary.  It will contain the
        following strings:
            * language tag
            * name of dictionary provider
            * description of dictionary provider
            * dictionary file
        Direct use of this method is not recommended - instead, access this
        information through the 'tag' and 'provider' attributes.
        """
        if check_this:
            self._check_this()
        _e.enchant_dict_describe_py(self._this,self.__describe_callback)
        return self.__describe_result

    def __describe_callback(self,tag,name,desc,file):
        """Collector callback for dictionary description.
        
        This method is used as a callback into the _enchant function
        'enchant_dict_describe_py'.  It collects the given arguments in
        a tuple and stores them in the attribute '__describe_result'.
        """
        name = name.decode("utf-8")
        desc = desc.decode("utf-8")
        file = file.decode("utf-8")
        self.__describe_result = (tag,name,desc,file)



##  Create a module-level default broker object, and make its important
##  methods available at the module level.
_broker = Broker()
request_dict = _broker.request_dict
request_pwl_dict = _broker.request_pwl_dict
dict_exists = _broker.dict_exists
list_dicts = _broker.list_dicts
list_languages = _broker.list_languages

