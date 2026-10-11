"""Passive, bounded local search. This module never launches a process or uses AI."""
import configparser
import os
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SearchResult:
    id: str
    label: str
    kind: str
    target: str


def classify_query(text: str, explicit_mode: str) -> str:
    if explicit_mode not in {'local', 'web', 'ai'}:
        raise ValueError('Unknown search mode')
    if explicit_mode == 'local' and text.lstrip().startswith('ai:'):
        return 'ai'
    return explicit_mode


def search(query: str, roots: list[str], *, app_dirs=None) -> list[SearchResult]:
    needle = query.strip().casefold()
    if not needle:
        return []
    if app_dirs is None:
        data_home = os.environ.get('XDG_DATA_HOME', str(Path.home() / '.local/share'))
        data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share').split(':')
        app_dirs = [str(Path(p) / 'applications') for p in [data_home, *data_dirs] if p]
    found = {}
    seen_apps = set()
    deadline = time.monotonic() + 0.25
    visited = 0
    for base, kind in [(p, 'application') for p in app_dirs] + [(p, 'file') for p in roots]:
        root = Path(base)
        if not root.is_absolute() or root.is_symlink():
            continue
        for parent, directories, files in os.walk(root, followlinks=False):
            directories[:] = sorted(d for d in directories if not d.startswith('.') and not (Path(parent) / d).is_symlink())
            for name in sorted(files):
                visited += 1
                if visited > 10000 or time.monotonic() > deadline:
                    return _rank(found.values(), needle)
                path = Path(parent) / name
                if name.startswith('.') or path.is_symlink() or not path.is_file():
                    continue
                label = name
                if kind == 'application':
                    if path.suffix != '.desktop':
                        continue
                    desktop_id = str(path.relative_to(root)).replace(os.sep, '-')
                    if desktop_id in seen_apps:
                        continue
                    seen_apps.add(desktop_id)
                    try:
                        if path.stat().st_size > 65536:
                            continue
                        parser = configparser.ConfigParser(interpolation=None, strict=False)
                        parser.read(path, encoding='utf-8')
                        entry = parser['Desktop Entry']
                        if entry.get('Type') != 'Application' or entry.getboolean('Hidden', False) or entry.getboolean('NoDisplay', False):
                            continue
                        desktops = set(os.environ.get('XDG_CURRENT_DESKTOP', '').split(':'))
                        only = set(filter(None, entry.get('OnlyShowIn', '').split(';')))
                        excluded = set(filter(None, entry.get('NotShowIn', '').split(';')))
                        if (only and not only.intersection(desktops)) or excluded.intersection(desktops):
                            continue
                        label = entry.get('Name', '')
                    except (OSError, UnicodeError, configparser.Error, KeyError, ValueError):
                        continue
                if label and needle in label.casefold():
                    target = str(path)
                    found[target] = SearchResult(target, label, kind, target)
    return _rank(found.values(), needle)


def _rank(results, needle):
    return sorted(results, key=lambda r: (r.label.casefold() != needle, not r.label.casefold().startswith(needle), r.label.casefold(), r.target))[:100]
