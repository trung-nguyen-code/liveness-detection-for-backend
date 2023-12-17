from server.search import SuperSearch
import json


def test_religious_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_religious(
        religious="1", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('is_pratiquant') && !doc['is_pratiquant'].empty && doc['is_pratiquant'].size() > 0 && params.religious == doc['is_pratiquant'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"religious": 1},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_family_situation_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_family_situation(
        status="1", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('family_situation') && !doc['family_situation'].empty && doc['family_situation'].size() > 0 && params.status == doc['family_situation'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"status": 1},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_degree_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_degree(
        degree="1", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('study_level') && !doc['study_level'].empty && doc['study_level'].size() > 0 && params.degree == doc['study_level'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"degree": 1},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_has_children_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_has_children(
        has_children="1", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('has_children') && !doc['has_children'].empty && doc['has_children'].size() > 0 && params.has_children == doc['has_children'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"has_children": 1},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_want_children_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_want_children(
        want_children="1", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('want_children') && !doc['want_children'].empty && doc['want_children'].size() > 0 && params.want_children == doc['want_children'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"want_children": 1},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_smoke_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_smoke(
        smoke="0", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('fume') && !doc['fume'].empty && doc['fume'].size() > 0 && params.smoke == doc['fume'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"smoke": 0},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_body_query():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_body(
        body="0", setting_type=True, functions=[], queries=[], score=11
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "    if (doc.containsKey('figure') && !doc['figure'].empty && doc['figure'].size() > 0 && params.body == doc['figure'].getValue()) {        return 11;    } else {        return 0;    }",
                "params": {"body": 0},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")


def test_localisation():
    super_search = SuperSearch(None, "settings.json")
    functions, queries = super_search.build_localisation(
        localisation="6",
        search_field="dept_code",
        setting_type=True,
        functions=[],
        queries=[],
        score=11,
    )
    expected_function = {
        "script_score": {
            "script": {
                "source": "if (doc.containsKey('dept_code') && !doc['dept_code'].empty && doc['dept_code'].size() > 0 && params.localisation == doc['dept_code'].getValue()) {    return 11;} else {    return 0;}",
                "params": {"localisation": "6"},
            }
        }
    }
    assert json.dumps(functions[0]).replace("\\n", "").replace(" ", "") == json.dumps(
        expected_function
    ).replace("\\n", "").replace(" ", "")
