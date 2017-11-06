import polyline
import logging

logger = logging.getLogger(__name__)

def starts_to_geojson(strava_activities, max_latitude_abs = 90, max_longitude_abs = 180):
    """
    Turn strava activities into a mapbox dataset
    PARAMS:
        strava_activities (array<dict>): An array of strava activities from the strava API
    """
    features = []
    for activity in strava_activities:
        name = activity.get("name")
        start_coords = activity.get('start_latlng')

        if name and start_coords:
            if (abs(start_coords[0]) > max_latitude_abs) or (abs(start_coords[1]) > max_longitude_abs):
                continue

            feature = {
                "type": "Feature",
                "properties": {
                    "title": activity["name"],
                },
                "geometry": {
                    # strava uses latlong, geojson uses longlat
                    "coordinates": [ start_coords[1], start_coords[0] ],
                    "type": "Point"
                }
            }
        features.append(feature)

    data = {
        "features": features,
        "type": "FeatureCollection"
    }
    return data


def polylines_to_geojson(strava_activities):

    features = []
    for activity in strava_activities:
        name = activity.get("name")
        map_polyline = activity.get("map", {}).get("summary_polyline")

        if not map_polyline:
            logger.info("No polyline for activity %s", name)
            continue

        line_coords = []
        try:
            line_coords = polyline.decode(map_polyline)
        except:
            logger.exception("Failed at decoding polyline for activity %s", name)
            continue

        properties = {"title": name}
        properties.update(compute_activity_properties(activity))

        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "coordinates": [ [coord[1], coord[0]] for coord in line_coords ],
                "type": "LineString"
            }
        }
        features.append(feature)

    data = {
        "features": features,
        "type": "FeatureCollection"
    }
    return data


def compute_activity_properties(activity):

    #convert to ~miles
    distance = activity.get("distance") / 1609
    elevation_gain = activity.get("total_elevation_gain")

    # Make difficulty a mix of distance and feet climbed. Eg. a 100 mile 1000ft ride 100
    # is easier than a 50 mile 5000 climb 50 + 5000/50 = 150 100 + 1000/100 = 110
    difficulty = distance + elevation_gain/distance

    cats = {
        "easy": (0, 10),
        "medium": (11, 40),
        "hard": (41, 80),
        "v_hard": (81, 150),
        "epic": (151, 500)
    }

    category = None
    for cat, cat_range in cats.items():
        if cat_range[0] <=  difficulty <= cat_range[1]:
            category = cat
            break

    properties = {
        "difficulty": difficulty,
        "distance": distance,
        "elevation_gain": elevation_gain,
        "category": category
    }
    return properties


