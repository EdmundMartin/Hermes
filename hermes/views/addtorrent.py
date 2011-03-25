#coding=utf-8
from pyramid.view import view_config
from wtforms import Form, FileField, TextField, validators
from hermes.lib import save_torrent
import logging 
import os
import bencode
import hashlib
import datetime
from hermes.model import DBSession
from hermes.model.db import Torrent
log = logging.getLogger(__name__)

class AddTorrentForm(Form):
    name = TextField('Torrent name', [validators.Required()])
    torrent_file = FileField('File')
    def validate_torrent_file(form,field):
        if not getattr(field.data, 'filename', None):
            raise validators.ValidationError('You need to supply a torrentfile')
@view_config(route_name='addtorrent', renderer='/addtorrent.mako')
def addtorrent(context, request):
    if request.method=="POST":
        form = AddTorrentForm(request.params)
        if form.validate():
            filename = save_torrent(form.torrent_file.data, request)
            abs_filename = os.path.join(request.registry.settings['torrent_dir'], filename)
            info = bencode.bencode(bencode.bdecode(open(abs_filename).read())['info'])
            info_hash = hashlib.sha1(info).hexdigest()
            torrent = Torrent()
            torrent.info_hash = info_hash
            torrent.name = form.name.data
            torrent.info = {}
            torrent.uploaded_time = datetime.datetime.now()
            torrent.torrent_file = filename
            DBSession.add(torrent)
            DBSession.commit()
            log.error(filename)
        return {'form': form}
    else:
        form = AddTorrentForm()
        return {'form': form}
