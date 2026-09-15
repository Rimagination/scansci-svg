"""Fetch a small, attributed species image reference set from public APIs."""
import argparse
import datetime as dt
import html
import json
from pathlib import Path
import re
import urllib.parse
import urllib.request


def request(base, endpoint, **params):
    url = base + endpoint + '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={'User-Agent': 'scansci-svg species-reference/1.0'})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def safe_url(value):
    return value if isinstance(value, str) and urllib.parse.urlsplit(value).scheme in ('https', 'http') else ''


def choose_taxon(query, taxa):
    def names(t):
        return [t.get(k) or '' for k in ('name', 'preferred_common_name', 'matched_term')]
    matches = [t for t in taxa if t.get('rank') == 'species' and t.get('is_active', True)
               and query.casefold().strip() in [n.casefold().strip() for n in names(t)]]
    return matches[0] if len(matches) == 1 else None


def inaturalist(query, limit, adult=False):
    api = 'https://api.inaturalist.org/v1/'
    taxa = request(api, 'taxa', q=query, rank='species', per_page=10, locale='zh-CN')['results']
    taxon = choose_taxon(query, taxa)
    if not taxon:
        return {'status': 'needs_identity', 'candidates': [
            {'id': t['id'], 'name': t['name'], 'common_name': t.get('preferred_common_name'), 'rank': t['rank']}
            for t in taxa], 'images': []}
    observations = request(api, 'observations', taxon_id=taxon['id'], photos='true',
                           quality_grade='research', order_by='votes', per_page=min(30, limit * 3),
                           **({'term_id': 1, 'term_value_id': 2} if adult else {}))['results']
    images, seen = [], set()
    for obs in observations:
        recorded = obs.get('taxon') or {}
        if taxon['id'] not in [recorded.get('id'), *recorded.get('ancestor_ids', [])]:
            continue
        for photo in (obs.get('photos') or [])[:2]:
            url = safe_url(photo.get('url'))
            if not url or photo.get('hidden') or photo.get('id') in seen:
                continue
            seen.add(photo.get('id'))
            url = re.sub(r'/square(\.[a-zA-Z]+)(?=\?|$)', r'/medium\1', url)
            images.append({'image_url': url, 'source_url': f"https://www.inaturalist.org/observations/{obs['id']}",
                           'photo_url': f"https://www.inaturalist.org/photos/{photo['id']}",
                           'recorded_name': recorded.get('name'), 'attribution': photo.get('attribution'),
                           'media_license': photo.get('license_code'), 'quality_grade': obs.get('quality_grade'),
                           'observed_on': obs.get('observed_on'),
                           'annotations': [{'attribute_id': a.get('controlled_attribute_id'), 'value_id': a.get('controlled_value_id')}
                                           for a in obs.get('annotations', [])]})
            if len(images) >= limit:
                break
        if len(images) >= limit:
            break
    return {'status': 'references_found' if images else 'no_images',
            'taxon': {'id': taxon['id'], 'name': taxon['name'], 'common_name': taxon.get('preferred_common_name'),
                      'url': f"https://www.inaturalist.org/taxa/{taxon['id']}"}, 'images': images}


def gbif(query, limit):
    api = 'https://api.gbif.org/v1/'
    matched = request(api, 'species/match', name=query, strict='true')
    if matched.get('matchType') != 'EXACT' or matched.get('rank') != 'SPECIES':
        return {'status': 'needs_identity', 'candidates': [matched], 'images': []}
    key = matched.get('acceptedUsageKey') or matched['usageKey']
    accepted = request(api, f'species/{key}') if matched.get('acceptedUsageKey') else matched
    records = request(api, 'occurrence/search', taxonKey=key, mediaType='StillImage', limit=min(50, limit * 4))['results']
    images, seen = [], set()
    for record in records:
        for media in record.get('media', []):
            url = safe_url(media.get('identifier'))
            if media.get('type') != 'StillImage' or not url or url in seen:
                continue
            seen.add(url)
            images.append({'image_url': url, 'source_url': f"https://www.gbif.org/occurrence/{record['key']}",
                           'photo_url': safe_url(media.get('references')),
                           'recorded_name': record.get('scientificName'), 'basis_of_record': record.get('basisOfRecord'),
                           'dataset_key': record.get('datasetKey'), 'attribution': media.get('creator') or media.get('rightsHolder'),
                           'media_license': media.get('license'), 'record_license': record.get('license'),
                           'observed_on': record.get('eventDate')})
            if len(images) >= limit:
                break
        if len(images) >= limit:
            break
    return {'status': 'references_found' if images else 'no_images',
            'taxon': {'id': key, 'name': accepted.get('scientificName'),
                      'matched_name': matched.get('scientificName'), 'match': matched,
                      'url': f'https://www.gbif.org/species/{key}'}, 'images': images}


def preview(data):
    esc = lambda v: html.escape(str(v or '未提供'), quote=True)
    cards = []
    for item in data['images']:
        cards.append(f'<article><a href="{esc(safe_url(item["source_url"]))}"><img loading="lazy" referrerpolicy="no-referrer" src="{esc(safe_url(item["image_url"]))}" alt="{esc(item.get("recorded_name"))}"></a>'
                     f'<p>{esc(item.get("recorded_name"))}</p><small>{esc(item.get("attribution"))}<br>图片许可：{esc(item.get("media_license"))}<br>{esc(item.get("basis_of_record") or item.get("quality_grade"))}</small></article>')
    identity = data.get('taxon', {}).get('name', data['request']['query'])
    candidates = '<pre>' + esc(json.dumps(data.get('candidates', []), ensure_ascii=False, indent=2)) + '</pre>' if data.get('candidates') else ''
    return f'<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>{esc(identity)} · 物种参考</title><style>body{{max-width:1200px;margin:32px auto;padding:20px;font:16px/1.5 system-ui;background:#f2f6f4;color:#203d35}}main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}}article{{padding:16px;background:white;border-radius:14px}}img{{width:100%;height:300px;object-fit:contain}}small{{color:#566b64}}pre{{white-space:pre-wrap}}</style><h1>{esc(identity)}</h1><p>{esc(data["request"]["provider"])} · {esc(data["status"])} · {esc(data["retrieved_at"])}</p><p>点击照片查看记录。先核对姿态、雌雄/季节或花果阶段，再选绘图参考；图片加载需联网。许可按每张图片记录。</p>{candidates}<main>{"".join(cards)}</main></html>'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('query', help='Scientific name preferred; unresolved names return candidates')
    parser.add_argument('output', type=Path)
    parser.add_argument('--provider', choices=['inaturalist', 'gbif'], default='inaturalist')
    parser.add_argument('--limit', type=int, choices=range(1, 13), default=6)
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--adult', action='store_true', help='iNaturalist annotated adult observations only')
    args = parser.parse_args()
    params = {'query': args.query.strip(), 'provider': args.provider, 'limit': args.limit}
    if args.adult:
        if args.provider != 'inaturalist':
            parser.error('--adult is supported by inaturalist only')
        params['adult'] = True
    if not params['query']:
        parser.error('Query must not be blank')
    record = args.output / 'references.json'
    if record.exists() and not args.refresh:
        data = json.loads(record.read_text(encoding='utf-8'))
        if data.get('request') != params:
            parser.error('Output belongs to another request; choose another directory or explicitly --refresh')
    else:
        data = inaturalist(params['query'], args.limit, adult=args.adult) if args.provider == 'inaturalist' else gbif(params['query'], args.limit)
        data.update(request=params, retrieved_at=dt.datetime.now(dt.timezone.utc).isoformat())
        args.output.mkdir(parents=True, exist_ok=True)
        record.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    (args.output / 'preview.html').write_text(preview(data), encoding='utf-8')
    print(json.dumps({'status': data['status'], 'taxon': data.get('taxon'), 'image_count': len(data['images']),
                      'references': str(record.resolve()), 'preview': str((args.output/'preview.html').resolve())}, ensure_ascii=False))


if __name__ == '__main__':
    main()
