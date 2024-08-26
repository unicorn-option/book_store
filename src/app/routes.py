from typing import List

from starlette.routing import Route


def build_routes() -> List[Route]:
    # routes = [
    #     {'path': '/names', 'endpoint': get_names, 'methods': ['GET'], 'name': 'get_name'},
    #     {'path': '/names/{uid}', 'endpoint': get_name_by_id, 'methods': ['GET'],
    #      'name': 'get_name_by_id'},
    # ]

    api_routes: List[Route] = []
    # for route in routes:
    #     obj = Route(**route)
    #     api_routes.append(obj)

    # api_routes = [
    #     Route('/names', endpoint=get_names, methods=['GET']),
    #     Route('/names/{uid}', endpoint=get_name_by_id, methods=['GET'])
    # ]

    return api_routes
