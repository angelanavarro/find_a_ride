"""
Utility methods to transform a strava activity file
to geojson
"""
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
        name = activity.get("name", "Activity")
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
    # Compute a 'leisure' measure based on how much time i stopped
    elapsed_time = activity.get("elapsed_time", 0)
    moving_time = activity.get("moving_time", 0)
    difficulty = 0
    chill_score = None

    # TODO: Come up with some measure of "chillness"
    if moving_time:
        chill_score = elapsed_time / moving_time

    # Multiply the distance by a factor of elevation and distance
    # 10 miles with 1000ft will be 10 but the same miles with 3000ft will be
    # 30 and with 200ft will be 2
    elevation_gain_mi = activity.get("total_elevation_gain", 0) * 3.28
    distance_mi = activity.get("distance", 0) / 1609.0
    if distance_mi:
        difficulty = distance_mi * (elevation_gain_mi/ (distance_mi*100))

    # split them in categories where difficulty is < 1/2 the distance
    if difficulty < distance_mi / 2:
        category = "easy"
    elif difficulty < distance_mi:
        category = "medium"
    else:
        category = "hard"

    properties = {
        "distance": activity.get("distance", 0) / 1000,
        "elevation_gain": activity.get("total_elevation_gain", 0),
        "difficulty": round(difficulty, 2),
        "category": category,
        "chill_score": chill_score
    }
    return properties


