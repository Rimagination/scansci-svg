import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import species_reference as sr


class ReferencesTest(unittest.TestCase):
    def test_adult_filter_is_sent_to_inaturalist(self):
        taxon = {'id': 2, 'name': 'Papilio machaon', 'rank': 'species'}
        with patch.object(sr, 'request', side_effect=[{'results': [taxon]}, {'results': []}]) as fetch:
            result = sr.inaturalist('Papilio machaon', 4, adult=True)
        self.assertEqual(fetch.call_args.kwargs['term_id'], 1)
        self.assertEqual(fetch.call_args.kwargs['term_value_id'], 2)
        self.assertEqual(result['status'], 'no_images')

    def test_identity_is_not_first_search_hit(self):
        taxa = [{'id': 1, 'name': 'Upupa marginata', 'rank': 'species'},
                {'id': 2, 'name': 'Upupa epops', 'rank': 'species', 'preferred_common_name': None}]
        self.assertEqual(sr.choose_taxon('Upupa epops', taxa)['id'], 2)
        self.assertIsNone(sr.choose_taxon('Upupa', taxa))
        self.assertIsNone(sr.choose_taxon('Upupa epops', taxa + [taxa[1]]))

    def test_images_belong_to_taxon_and_keep_media_license(self):
        taxon = {'id': 2, 'name': 'Upupa epops', 'rank': 'species'}
        photo = {'id': 8, 'url': 'https://example.org/square.jpg', 'license_code': 'cc-by', 'attribution': 'Author'}
        wrong = {'id': 10, 'taxon': {'id': 99}, 'photos': [photo]}
        right = {'id': 11, 'taxon': {'id': 3, 'ancestor_ids': [2], 'name': 'Upupa epops epops'}, 'photos': [photo, photo]}
        with patch.object(sr, 'request', side_effect=[{'results': [taxon]}, {'results': [wrong, right]}]):
            data = sr.inaturalist('Upupa epops', 4)
        self.assertEqual(len(data['images']), 1)
        self.assertEqual(data['images'][0]['media_license'], 'cc-by')
        self.assertTrue(data['images'][0]['source_url'].endswith('/11'))

    def test_gbif_fuzzy_and_higher_rank_require_identity(self):
        for response in ({'matchType': 'FUZZY', 'rank': 'SPECIES'}, {'matchType': 'EXACT', 'rank': 'GENUS'}):
            with patch.object(sr, 'request', return_value=response) as fetch:
                self.assertEqual(sr.gbif('ambiguous', 4)['status'], 'needs_identity')
                self.assertEqual(fetch.call_count, 1)

    def test_cached_request_does_not_need_network(self):
        with tempfile.TemporaryDirectory() as directory:
            data = {'status': 'no_images', 'images': [], 'retrieved_at': 'test',
                    'request': {'query': 'Upupa epops', 'provider': 'inaturalist', 'limit': 6}}
            Path(directory, 'references.json').write_text(json.dumps(data), encoding='utf-8')
            with patch('sys.argv', ['species_reference', 'Upupa epops', directory]), patch.object(sr, 'request', side_effect=AssertionError('network used')), contextlib.redirect_stdout(io.StringIO()):
                sr.main()
            self.assertTrue(Path(directory, 'preview.html').exists())

    def test_gbif_resolves_synonym_and_keeps_licenses_separate(self):
        matched = {'matchType': 'EXACT', 'rank': 'SPECIES', 'usageKey': 1,
                   'acceptedUsageKey': 2, 'scientificName': 'Old name'}
        record = {'key': 3, 'scientificName': 'Accepted name', 'license': 'CC0',
                  'media': [{'type': 'StillImage', 'identifier': 'https://example.org/photo.jpg'}]}
        with patch.object(sr, 'request', side_effect=[matched, {'scientificName': 'Accepted name'}, {'results': [record]}]) as fetch:
            data = sr.gbif('Old name', 4)
        self.assertEqual(data['taxon']['name'], 'Accepted name')
        self.assertEqual(fetch.call_args_list[2].kwargs['taxonKey'], 2)
        self.assertIsNone(data['images'][0]['media_license'])
        self.assertEqual(data['images'][0]['record_license'], 'CC0')

    def test_preview_escapes_remote_metadata(self):
        data = {'status': 'references_found', 'retrieved_at': 'test', 'request': {'query': '<script>bad</script>', 'provider': 'test'},
                'images': [{'image_url': 'javascript:bad()', 'source_url': 'javascript:bad()', 'attribution': '<script>bad</script>'}]}
        page = sr.preview(data)
        self.assertNotIn('<script>', page)
        self.assertNotIn('javascript:', page)


if __name__ == '__main__':
    unittest.main()
