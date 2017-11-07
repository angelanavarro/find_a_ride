import unittest
from ride_finder.strava import transformer

class TestTransformer(unittest.TestCase):

    def setUp(self):
        self.activity = {
            "average_watts": 91.3,
            "kilojoules": 3922.0,
            "average_temp": 18.0,
            "id": 1251332134,
            "gear_id": "b1152057",
            "average_speed": 4.715,
            "elapsed_time": 49260,
            "type": "Ride",
            "map": {
                "id": "a1251332134",
                "summary_polyline": "qwueF`|ljVeLl[xKpTwd@vMkSrl@cgCpOoYx]mb@{l@wcBlPeh@vfBqfBpuBxA|k@cNnKtQvUmDtt@me@NeKjWfK`C_Fxy@jW`SanAlZieBbxByZjBuSum@lKh}@yTtSj^ty@qh@qMuA_`@o_@qLhWhT{M`\\v[rRlClj@~l@dk@ob@rIc|@kq@a}@zPowAjbAuu@skA{|@jAmK|tA`SbQcHb]dy@kCifClrCob@wLio@`e@a@zhBcrCa}@PfVs`Ahq@}|@`dBusEbzB_qAbgCqk@~U_y@}i@{o@mhAkv@pGm_DyrAcc@zpAib@qRol@jPyJxm@nXfbA}Ffk@zj@by@m^bv@~H|eCcf@xpAbBxn@dSdt@hbBziA`GfvAqTvz@jHpz@ajApjBuGvzB`ZdP~`@{Uh|@a{@dW_z@vi@}Gxo@epArdBweAdAoh@xWxBxmAgpAlEqnAxnBgoA|[b`@pZyHtGj~AihCrkBawC|kDjAzjEpg@n\\bP{^_OAbPu`@oGwh@t`AaIlEel@pq@qe@rSel@sJaJhNex@zqB{LkA_~@~m@gt@{OufArPeDqD}c@dc@ss@scA~YtxAyiAp\\apAb{GkdE|cCgnCkb@_e@g`@eyAjeEsoEnd@aoAfr@sf@vS{_Ajx@me@pYu_Abw@a[lDqnAhd@bHqQkQrVmm@ay@sh@xVon@yh@gh@x{BguC`nAiZcXmSrFex@mKqD|ImVhf@O]gdCfgBiuB|`@s}A|gBsZfK~^jYvEnXuVfoCgRrJqi@zf@_OgLoSnLw]"
            },
            "elev_high": 747.2,
            "moving_time": 42940,
            "start_latlng": [
                37.8,
                -122.46
            ],
            "max_speed": 14.5,
            "end_latlng": [
                37.8,
                -122.46
            ],
            "distance": 202460.0,
            "name": "Marin Mountains 200k",
            "total_elevation_gain": 4027.0,
        }

    def test_starts_to_geojson(self):
        pass

    def test_compute_properties(self):
        expected_properties = {
            "distance": 202.46,
            "elevation_gain": 4027.0,
            "difficulty": 132.09,
            "category": "hard",
            "chill_score": 1
        }
        properties = transformer.compute_activity_properties(self.activity)
        self.assertItemsEqual(properties, expected_properties)
        self.assertTrue(all([properties[k] == v for k,v in expected_properties.items()]))


    def test_compute_properties_no_data(self):
        expected_properties = {
            "distance": 0,
            "elevation_gain": 0,
            "difficulty": 0,
            "category": "hard",
            "chill_score": None
        }
        properties = transformer.compute_activity_properties({})
        self.assertItemsEqual(properties, expected_properties)
        self.assertTrue(all([properties[k] == v for k,v in expected_properties.items()]))


    def test_polylines_to_geojson(self):
        data = transformer.polylines_to_geojson([self.activity])
        features = data.get("features")

        self.assertEqual(len(features), 1)
        self.assertEqual(data["type"], "FeatureCollection")
        activity_data = features[0]
        self.assertTrue(activity_data["geometry"]["coordinates"])
        self.assertEqual(activity_data["geometry"]["type"], "LineString")


    def test_polylines_to_geojson_buggy_coords(self):
        activity = {
            "elapsed_time": 49260,
            "map": {
                "id": "a1251332134",
                "summary_polyline": "qwupTwd@vi@zf@_OgLoSnLw]"
            }
        }
        data = transformer.polylines_to_geojson([activity])
        self.assertEqual(data['features'], [])


    def test_polylines_to_geojson_no_coords(self):
        activity = {
            "elapsed_time": 49260,
            "map": {
                "id": "a1251332134"
            }
        }
        data = transformer.polylines_to_geojson([activity])
        self.assertEqual(data['features'], [])
