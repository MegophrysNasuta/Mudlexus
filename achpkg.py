#!/usr/bin/env python3
import os
import json
import re
import shutil
import sys
from xml.etree import ElementTree as ET


class PackageExtractor:
    NUMBERED_JSON_REGEX = re.compile(r'\.?[\d+]*\.json')

    def __init__(self, overwrite=False):
        self.overwrite = bool(overwrite)

    def _create_dirpath(self, dirpath):
        try:
            os.makedirs(dirpath, exist_ok=False)
        except FileExistsError:
            if not self.overwrite:
                raise
            shutil.rmtree(dirpath)
            os.makedirs(dirpath, exist_ok=True)

    def _get_next_available_filename(self, dirpath, filename):
        i = 1
        while os.path.exists(os.path.join(dirpath, filename)):
            filename = self.NUMBERED_JSON_REGEX.sub('.%i.json' % i,
                                                    filename)
            i += 1
        return filename


class MudletXMLPackageExtractor(PackageExtractor):
    PACKAGE_TAGS = tuple(('%sPackage' % tag for tag in
                         ('Alias', 'Key', 'Script', 'Timer', 'Trigger')))

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.matches_regex = re.compile('(multi)?matches\[?[\d+]?\]?\[(\d+)\]')

    def __call__(self, tree, dirpath):
        root = tree.getroot()

        if root.tag != 'MudletPackage':
            raise ValueError("Are you sure '%s' is a Mudlet Package?" % filepath)
        else:
            print("Parsing Mudlet Package (version: %s)" % root.attrib.get('version',
                                                                           'unknown'))

        self.paths_created = set()
        for pkg_tag in self.PACKAGE_TAGS:
            for section in root.find(pkg_tag) or ():
                self.extract_section(section, dirpath)

        if os.path.exists('./onLoad.js'):
            with open(os.path.join(dirpath, 'onLoad.json'), 'w') as file_:
                file_.write(json.dumps({
                    'type': 'function',
                    'name': 'onLoad',
                    'enabled': True,
                    'code': '',
                }, indent=4))
            shutil.copy('./onLoad.js', dirpath)

    def extract_section(self, root, dirpath):
        if dirpath not in self.paths_created:
            self._create_dirpath(dirpath)
            self.paths_created.add(dirpath)

        group_tag = root.tag.replace('Package', 'Group')
        node_tag = group_tag.replace('Group', '')

        if 'Group' in group_tag:
            for node in root.findall(node_tag):
                self.write_node(node, dirpath)
            for group_node in root.findall(group_tag):
                node_info = self.get_node_info(group_node)
                grouppath = os.path.join(dirpath, node_info['name'])
                self.extract_section(group_node, grouppath)
        else:
            self.write_node(root, dirpath)

    def get_matches(self, root):
        trigger_type = {'0': 'substring', '1': 'regexp', '2': 'substring',
                        '3': 'exact', '4': 'lua function',
                        '5': 'line spacer', '6': 'color trigger', '7': 'prompt'}
        return zip((tag.text for tag in root.find('regexCodeList')),
                    (trigger_type[tag.text]
                     for tag in root.find('regexCodePropertyList')))

    def get_node_info(self, node):
        self.unknowns = getattr(self, 'unknowns', 1)
        node_info = {'enabled': node.attrib.get('isActive') == 'yes',
                     'type': node.tag.lower()}

        for child in ('name', 'script', 'command', 'regex', 'keyCode',
                      'keyModifier', 'time'):
            child_node = node.find(child)
            if child_node is not None:
                if child == 'script':
                    node_info['actions'] = [{
                        'action': 'script',
                        'script': child_node.text,
                    }]
                else:
                    child_mappings = {
                        'regex': 'text',
                    }
                    child = child_mappings.get(child, child)
                    node_info[child] = child_node.text

        if node_info.get('name') is None:
            node_info['name'] = 'Unknown %s %i' % (node.tag, self.unknowns)
            self.unknowns += 1

        node_info['name'] = (node_info['name'].replace('/', 'Slash')
                                              .replace('\\', 'Backslash'))

        if node.tag == 'Trigger':
            matches = list(self.get_matches(node))
            regexes = [(t, m) for t, m in matches if m == 'regexp']
            if node.attrib.get('isMultiline') == 'yes':
                if len(regexes) > 1:
                    print('='*20)
                    print('MANUAL REWRITE NEEDED: Multiline, multi-regex trigger')
                    print(node_info['name'])
                    print('\n'.join(text for text, _ in regexes))
                    print('='*20)
                    return None
                try:
                    text, matching = regexes[0]
                except IndexError:
                    text, matching = matches[0]
                node_info.update({'text': text, 'matching': matching})
            else:
                # blow this up into multiple nodes
                node_list = list()
                for text, matching in matches:
                    next_node_info = node_info.copy()
                    next_node_info['text'] = text
                    next_node_info['matching'] = matching
                    node_list.append(next_node_info)
                return node_list

        return node_info

    def write_node(self, node, dirpath):
        all_node_info = self.get_node_info(node)
        if all_node_info is None:
            return
        elif type(all_node_info) == list:
            for node_info in all_node_info:
                self._write_node(node, dirpath, node_info)
        else:
            self._write_node(node, dirpath, all_node_info)

    def _write_node(self, node, dirpath, node_info):
        filename = '%s.json' % node_info['name']
        filename = self._get_next_available_filename(dirpath, filename)
        with open(os.path.join(dirpath, filename), 'w') as filestore:
            filestore.write(json.dumps(node_info, indent=4))
        if node_info.get('actions') and node_info['actions'][0].get('script'):
            script = 'lua.execute(`%s`)' % (
                self.matches_regex.sub(r'js.global.args[\2]',
                                       node_info['actions'][0]['script'])
            )
            with open(os.path.join(dirpath, filename[:-2]), 'w') as f:   # .js
                print('(function() {', file=f)
                print(script, file=f)
                print('})()', file=f)


class NexusNXSPackageExtractor(PackageExtractor):
    def __call__(self, data, dirpath):
        self._create_dirpath(dirpath)

        for item in data['items']:
            if item['type'] == 'group':
                grouppath = os.path.join(dirpath, item['name'])
                extractor = self.__class__(overwrite=self.overwrite)
                extractor(item, grouppath)
            else:
                if item['name']:
                    filename = '%s_%s.json' % (item['name'], item['type'])
                else:
                    filename = '%s%i.json' % (item['type'], item['id'])

                filename = self._get_next_available_filename(dirpath, filename)

                try:
                    code = item.get('code') or tuple((
                        action for action in item.get('actions', ())
                        if action.get('script')))[0]['script']
                except IndexError:
                    pass
                else:
                    # .js not .json
                    with open(os.path.join(dirpath, filename[:-2]), 'w') as f:
                        print('(function() {', file=f)
                        print(code, file=f)
                        print('})()', file=f)

                with open(os.path.join(dirpath, filename), 'w') as filestore:
                    filestore.write(json.dumps(item, indent=4))


class NexusNXSCompiler:
    def __init__(self, package_name):
        self.package_name = str(package_name)
        self.package_path = os.path.join(os.getcwd(), self.package_name)
        self.package = {
            'name': self.package_name,
            'id': 1,
            'enabled': True,
            'type': 'group',
            'items': list(),
        }
        self.generated_id = 2

    def _add_to_package(self, dirpath, filename):
        with open(os.path.join(dirpath, filename)) as filestore:
            data = json.loads(filestore.read())

        try:
            # look for a .js file with the same name as the .json
            with open(os.path.join(dirpath, filename[:-2])) as jsfile:
                update_data = '\n'.join(jsfile.read().splitlines()[1:-1])
        except (IOError, OSError):
            pass
        else:
            if 'code' in data:
                data['code'] = update_data
            else:
                for action in data.get('actions', ()):
                    if 'script' in action:
                        action['script'] = update_data
                        break

        items = self.package.setdefault('items', list())
        for key in os.path.normpath(dirpath.replace(os.getcwd(), '')).split('/'):
            if key and key != self.package_name:
                try:
                    items = [item for item in items
                             if item['name'] == key and
                                item['type'] == 'group'][0].setdefault('items',
                                                                       list())
                except IndexError:
                    items.append({
                        'type': 'group',
                        'enabled': True,
                        'id': self.generated_id,
                        'name': key,
                        'items': list(),
                        'actions': list(),
                    })
                    items = items[-1]['items']
                    self.generated_id += 1

        if 'id' not in data:
            data['id'] = self.generated_id
            self.generated_id += 1

        items.append(data)

    @property
    def package_description(self):
        try:
            with open(os.path.join(self.package_path,
                                   'description.txt')) as desc:
                return desc.read()
        except (IOError, OSError):
            return ''

    @property
    def package_file(self):
        return '%s.nxs' % self.package_name

    def compile(self):
        for dirpath, _, filenames in os.walk(self.package_path):
            for filename in filenames:
                if filename.endswith('.json'):
                    self._add_to_package(dirpath, filename)

        with open(os.path.join(os.getcwd(), self.package_file), 'w') as pkg_file:
            self.package['description'] = self.package_description
            pkg_file.write(json.dumps(self.package, indent=4))


def run_interactive():
    main_menu = """
    Nasuta's Achaea Packaging Tools
    ===============================

    1. Extract a package into files and folders
    2. Compile files and folders into a package
    3. Quit

    Your choice? """
    package_path_question = """
    Enter the path to your package: """
    package_name_question = """
    Enter the name of your package: """
    source_code_question = """
    Enter the path to your source code: """
    target_path_question = """
    Enter the path to store the result: """
    confirm_overwrite = """
    Overwrite the target directory? (Y/n) """

    def die(code=1):
        print()
        print('Exiting...', file=sys.stderr)
        sys.exit(int(code))

    menu_opt = 0
    while not (0 < menu_opt < 4):
        try:
            menu_opt = int(input(main_menu))
        except ValueError:
            pass
        except (KeyboardInterrupt, EOFError):
            die()
            break

    if menu_opt == 1:
        try:
            pkg_path = os.path.abspath(input(package_path_question))
            while not os.path.exists(pkg_path):
                print("\tCan't find this package!", file=sys.stderr)
                pkg_path = os.path.abspath(input(package_path_question))

            tgt_path = os.path.abspath(input(target_path_question))
        except (KeyboardInterrupt, EOFError):
            die()
        else:
            _, ext = os.path.splitext(pkg_path)
            try:
                Extractor = {
                    '.xml': MudletXMLPackageExtractor,
                    '.nxs': NexusNXSPackageExtractor,
                }[ext]
            except KeyError:
                print("Don't know how to extract this type of file.",
                      file=sys.stderr)
                die()

            overwrite = False
            if os.path.exists(tgt_path):
                overwrite = input(confirm_overwrite).lower() == 'y'

            extractor = Extractor(overwrite=overwrite)

            if ext == '.xml':
                data = ET.parse(pkg_path)
            elif ext == '.nxs':
                with open(pkg_path) as json_file:
                    data = json.loads(json_file.read())

            extractor(data, tgt_path)
    elif menu_opt == 2:
        try:
            pkg_path = os.path.abspath(input(source_code_question))
            while not os.path.exists(pkg_path):
                print("\tCan't find this package!", file=sys.stderr)
                pkg_path = os.path.abspath(input(source_code_question))

            pkg_name = input(package_name_question)
        except (KeyboardInterrupt, EOFError):
            die()
        else:
            compiler = NexusNXSCompiler(pkg_name)
            compiler.package_path = pkg_path
            compiler.compile()


if __name__ == "__main__":
    run_interactive()
