# Copyright (C) 2016 Catalyst IT Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations

import logging
import os
import shutil
import tempfile
import virtualenv_tools

from giftwrap.builders import PackageBuilder


LOG = logging.getLogger(__name__)


class PackageVenvBuilder(PackageBuilder):
    def __init__(self, spec):
        sc = super(PackageVenvBuilder, self)
        self._temp_venv_dir = None
        self._temp_install_path = None
        sc.__init__(spec)

    def _make_temp_dir(self, prefix='giftwrap'):
        sc = super(PackageVenvBuilder, self)
        # also create our venv temp dir here
        self._temp_venv_dir = tempfile.mkdtemp(prefix)
        return sc._make_temp_dir(prefix='giftwrap')

    def _prepare_project_build(self, project):
        sc = super(PackageVenvBuilder, self)
        # replace install_path with our own temporary dir
        self._temp_install_path = project.install_path
        project._install_path = os.path.join(self._temp_venv_dir, project.name)

        sc._prepare_project_build(project)

    def _finalize_project_build(self, project):
        sc = super(PackageVenvBuilder, self)

        # update paths in virtualenv to point at our target
        # Note: binary tools of update_paths do not support unicode strings
        new_path = self._temp_install_path.encode('utf8')
        success = virtualenv_tools.update_paths(
            base=project.install_path,
            new_path=new_path)
        if not success:
            LOG.warning("Virtualenv-tools did not finish correctly, the venv "
                        "within the package may not be usable.")

        # build the package
        sc._finalize_project_build(project)

    def _cleanup_build(self):
        sc = super(PackageVenvBuilder, self)
        shutil.rmtree(self._temp_venv_dir)
        sc._cleanup_build()
