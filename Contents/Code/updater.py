# -*- coding: utf-8 -*-
#
# Plex Plugin Updater
# $Id$
#
# Universal plugin updater module for Plex Server Channels that
# implement automatic plugins updates from remote config.
# Support Github API by default
#
# https://github.com/kolsys/plex-channel-updater
#
# Copyright (c) 2014, KOL
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

KEY_PLIST_VERSION = 'CFBundleVersion'
KEY_PLIST_URL = 'PlexPluginVersionUrl'

KEY_DATA_VERSION = 'tag_name'
KEY_DATA_DESC = 'body'
KEY_DATA_ZIPBALL = 'zipball_url'

CHECK_INTERVAL = CACHE_1HOUR


from utils import L, F
import messages


class Updater:
    info = None
    update = None

    def __init__(self, prefix, oc):

        if self.InitBundleInfo() and self.IsUpdateAvailable():
            Route.Connect(prefix, self.DoUpdate)
            oc.add(DirectoryObject(key=Callback(self.DoUpdate), title=F('MAIN_UPDATER', self.update['version']),
                                   summary=u'%s' % self.update['info'], thumb=R('icon_updater.png')))

    def NormalizeVersion(self, version):
        if version[:1] == 'v':
            version = version[1:]
        return version

    def ParseVersion(self, version):

        try:
            return tuple(map(int, (version.split('.'))))
        except:
            # String comparison by default
            return version

    def IsUpdateAvailable(self):
        try:
            info = JSON.ObjectFromURL(
                self.info['url'],
                cacheTime=CACHE_1HOUR,
                timeout=5
            )
            # version = self.NormalizeVersion(info[KEY_DATA_VERSION])  # TODO: change before release
            version = info['commit']['sha']
            # dist_url = info[KEY_DATA_ZIPBALL]  # TODO: change before release
            dist_url = 'https://api.github.com/repos/dein0s/seasonvar_ru.bundle/zipball/develop'

        except:
            return False

        if self.info['version'] != version:
            self.update = {
                'version': version,
                'url': dist_url,
                'info': info['commit']['commit']['message'],
            }
        # TODO: change before release
        # if self.ParseVersion(version) > self.ParseVersion(
        #     self.info['version']
        # ):
        #     self.update = {
        #         'version': version,
        #         'url': dist_url,
        #         'info': info[KEY_DATA_DESC] if KEY_DATA_DESC in info else '',
        #     }

        return bool(self.update)

    def InitBundleInfo(self):
        try:
            dev_version = Core.storage.load(
                Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents','.dev-version')))
            # TODO: change before release
            # plist = Plist.ObjectFromString(Core.storage.load(
            #     Core.storage.abs_path(
            #         Core.storage.join_path(
            #             Core.bundle_path,
            #             'Contents',
            #             'Info.plist'
            #         )
            #     )
            # ))
            self.info = {
                # 'version': plist[KEY_PLIST_VERSION],  # TODO: change before release
                'version': dev_version,
                # 'url': plist[KEY_PLIST_URL],  # TODO: change before release
                'url': 'http://api.github.com/repos/dein0s/seasonvar_ru.bundle/branches/develop',
            }
        except:
            pass

        return bool(self.info)

    def DoUpdate(self):
        try:
            zip_data = Archive.ZipFromURL(self.update['url'])
            bundle_path = Core.storage.abs_path(Core.bundle_path)

            for name in zip_data.Names():
                data = zip_data[name]
                parts = name.split('/')
                shifted = Core.storage.join_path(*parts[1:])
                full = Core.storage.join_path(bundle_path, shifted)

                if '/.' in name:
                    continue

                if name.endswith('/'):
                    Core.storage.ensure_dirs(full)
                else:
                    Core.storage.save(full, data)
            del zip_data

            dev_version = Core.storage.save(
                Core.storage.abs_path(Core.storage.join_path(Core.bundle_path, 'Contents','.dev-version')),
                self.update['version'])
            return ObjectContainer(header=messages.INFO.HEADER, message=F(messages.INFO.UPDATER_SUCCESS,
                                                                          self.update['version']))
        except Exception as e:
            return ObjectContainer(header=messages.ERROR.HEADER, message=u'%s' % e)
