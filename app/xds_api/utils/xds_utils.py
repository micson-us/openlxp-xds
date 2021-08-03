import json

import requests

from core.models import CourseSpotlight, Experience, XDSConfiguration


def get_request(request_url):
    """This method handles a simple HTTP get request to the passe in
        request_url"""
    response = requests.get(request_url)

    return response


def get_spotlight_courses_api_url():
    """This method gets the list of configured course spotlight IDs, the
        configured XIS api url and generates the query to request records"""
    # get XIS API url
    course_spotlights = CourseSpotlight.objects.filter(active=True)
    # get search string
    composite_api_url = XDSConfiguration.objects.first()\
        .target_xis_metadata_api
    queryString = '?id='

    for num, spotlight in enumerate(course_spotlights):
        if num >= (len(course_spotlights) - 1):
            queryString += spotlight.course_id
        else:
            queryString += spotlight.course_id + ','

    full_api_string = composite_api_url + queryString

    return full_api_string


def metadata_to_target(metadata_JSON):
    """This method takes in a JSON representation of a record and transforms it
        into the search engine format"""
    metadata_dict = json.loads(metadata_JSON)
    result = None

    if isinstance(metadata_dict, list):
        result_list = []

        for record in metadata_dict:
            if 'metadata' in record:
                currObj = record['metadata']
                meta = {}

                meta["id"] = record["unique_record_identifier"]
                meta["metadata_key_hash"] = record["metadata_key_hash"]
                currObj["meta"] = meta
                result_list.append(currObj)

        result = result_list

    elif isinstance(metadata_dict, dict):
        if 'metadata' in metadata_dict:
            currObj = metadata_dict['metadata']
            meta = {}

            meta["id"] = metadata_dict["unique_record_identifier"]
            meta["metadata_key_hash"] = metadata_dict["metadata_key_hash"]
            currObj["meta"] = meta
            result = currObj

    return result


def get_courses_api_url(course_id):
    """This method gets the metadata api url to fetch single records"""
    composite_api_url = XDSConfiguration.objects.first()\
        .target_xis_metadata_api
    full_api_url = composite_api_url + course_id

    return full_api_url


def save_experiences(course_list):
    """This method handles the saving of each course in the list"""
    for course_hash in course_list:
        newExperience, created = \
            Experience.objects.get_or_create(pk=course_hash)
        newExperience.save()
