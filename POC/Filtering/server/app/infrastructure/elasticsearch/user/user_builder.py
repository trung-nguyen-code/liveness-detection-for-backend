from typing import List
from datetime import datetime
from elasticsearch_dsl import Q

from app.constants.user import RangeInput, CommonInput, LocationInput
from app.utils.dict import safe_itemgetter


class Builder:
    def build_range_query(
        self, functions, field_name, min_value, max_value, score=10
    ):  # noqa: E501
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": """
                                if (doc.containsKey('%(field_name)s') && !doc['%(field_name)s'].empty && doc['%(field_name)s'].size() > 0) {
                                    if (doc['%(field_name)s'].getValue() * 1 <= params.min_value * 1) {
                                        return %(score)s *  Math.pow((doc['%(field_name)s'].getValue() * 1.0 / params.min_value * 1.0), 3);
                                    } else if (doc['%(field_name)s'].getValue() * 1 >= params.max_value * 1) {
                                        return %(score)s *  Math.pow((params.max_value * 1.0 / doc['%(field_name)s'].getValue() * 1.0), 3);
                                    } else {
                                        return %(score)s
                                    }
                                } else {
                                    return 0;
                                }
                            """  # noqa: E501
                        % {"field_name": field_name, "score": score},
                        "params": {
                            "min_value": min_value,
                            "max_value": max_value,
                        },  # noqa: E501
                    }
                }
            }
        )
        return functions

    def build_localisation(
        self,
        localisation,
        search_field,
        setting_type,
        functions,
        queries,
        score=10,  # noqa: E501
    ):
        if localisation and setting_type:
            source_str = """
                            if (doc.containsKey('%s') && !doc['%s'].empty && doc['%s'].size() > 0 && params.localisation ==  doc['%s'].getValue()) {
                                return %s;
                            } else {
                                return 0;
                            }
                        """ % (  # noqa: E501
                search_field,
                search_field,
                search_field,
                search_field,
                score,
            )
            functions.append(
                {
                    "script_score": {
                        "script": {
                            "source": source_str,
                            "params": {"localisation": str(localisation)},
                        }
                    }
                }
            )
        elif localisation and not setting_type:
            queries.append(Q("term", **{"%s" % (search_field): localisation}))
        return functions, queries

    def build_push_forward_query(self, functions, now, score=10):
        # 0 to 10    : the time since last boost more than 1 day
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": """
                            if (doc.containsKey('date_mise_avant') && !doc['date_mise_avant'].empty && doc['date_mise_avant'].size() > 0) {
                                double days = ((Instant.ofEpochSecond(params.now).toEpochMilli()-doc['date_mise_avant'].getValue().toInstant().toEpochMilli())/1000)/86400;
                                if (days <= 1) {
                                    return %s;
                                }
                                else if (days <= 3) {
                                    return %s;
                                }
                                else if (days <= 7) {
                                    return %s;
                                }
                                else if (days <= 30) {
                                    return %s;
                                }
                                else {
                                    return 0;
                                }
                            } else {
                                return 0;
                            }
                        """  # noqa: E501
                        % (score, score / 2, score / 4, score / 8),
                        "params": {"now": now},
                    }
                }
            }
        )
        return functions

    def build_distance_query(self, functions, lat, lon, score=10):
        # Distance between user and candidate
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": """
                            if (doc.containsKey('location') && !doc['location'].empty && doc['location'].size() > 0) {
                                if (doc.containsKey('latitude') && doc.containsKey('longitude') && doc['latitude'].size() > 0 && doc['longitude'].size() > 0) {
                                    if (doc['latitude'].getValue() != 0 || doc['longitude'].getValue() != 0) {
                                        double distance = doc['location'].arcDistance(params.lat,params.lon) / 1000;
                                        if (distance <= 50) {
                                            return %s;
                                        } else if (distance <= 100) {
                                            return %s;
                                        } else if (distance <= 300) {
                                            return %s;
                                        } else if (distance <= 700) {
                                            return %s;
                                        } else if (distance <= 1000) {
                                            return %s;
                                        } else {
                                            return 0;
                                        }
                                    }
                                }
                            } else {
                                return 0;
                            }
                        """  # noqa: E501
                        % (
                            score,
                            score * 0.75,
                            score * 0.5,
                            score * 0.25,
                            score * 0.125,
                        ),
                        "params": {"lat": lat, "lon": lon},
                    }
                }
            }
        )
        return functions

    def build_last_connection_query(self, functions, now, score=10):
        # 0 to 10    : the time since last connection more than 10 mins
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": """
                            double days = ((Instant.ofEpochSecond(params.now).toEpochMilli()-doc['last_live_time'].getValue().toInstant().toEpochMilli())/1000)/86400;
                            if (days <= 30.0) {
                                return 3.75;
                            }
                            if (days <= 7.0) {
                                return 7.5;
                            }
                            if (days <= 3.0) {
                                return 15;
                            }
                            if (days <= 1.0) {
                                return 30;
                            }
                            return 0;
                        """,  # noqa: E501
                        "params": {"now": now},
                    }
                }
            }
        )
        return functions

    def build_seniority_query(self, functions, now, score=10):
        #  0.1 to 10  : the seniority of the account
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": """
                            if (doc.containsKey('date_create') && !doc['date_create'].empty && doc['date_create'].size() > 0) {
                                double days = ((Instant.ofEpochSecond(params.now).toEpochMilli()-doc['date_create'].getValue().toInstant().toEpochMilli())/1000)/86400;
                                if (days <= 7) {
                                    return %s;
                                }
                                else if (days <= 15) {
                                    return %s;
                                }
                                else if (days <= 30) {
                                    return %s;
                                }
                                else {
                                    return 0;
                                }
                            } else {
                                return 0;
                            }
                        """  # noqa: E501
                        % (score, score / 2, score / 4),
                        "params": {"now": now},
                    }
                }
            }
        )
        return functions

    def build_photo_query(self, functions, score=10):
        # 0 or 5    : user has pictures
        functions.append(
            {
                "filter": {"exists": {"field": "photos"}},
                "weight": score,
            }
        )
        return functions

    def build_profile_filling_rate_query(self, functions, score=10):
        #  0 to 10    : Profile filling rate
        functions.append(
            {
                "script_score": {
                    "script": {
                        "source": "return doc['taux_remplissage'].getValue() * 1.0 /100 * %s"  # noqa: E501
                        % score,
                    }
                }
            }
        )
        return functions

    def build_categorical_function_score(
        self, functions, search_value, search_field, score=10
    ):
        if isinstance(search_value, list):
            functions.append(
                {
                    "filter": Q(
                        "terms",
                        **{
                            "%s"
                            % (search_field): list(
                                map(lambda x: int(x), search_value)
                            )  # noqa: E501
                        }
                    ),
                    "weight": score,
                }
            )
        else:
            functions.append(
                {
                    "filter": Q(
                        "term", **{"%s" % (search_field): int(search_value)}
                    ),  # noqa: E501
                    "weight": score,
                }
            )
        return functions

    def build_filter(self, queries, search_value, search_field):
        if isinstance(search_value, list):
            queries.append(
                Q(
                    "terms",
                    **{
                        "%s"
                        % (search_field): list(
                            map(lambda x: int(x), search_value)
                        )  # noqa: E501
                    }
                )
            )
        else:
            queries.append(
                Q("term", **{"%s" % (search_field): int(search_value)})
            )  # noqa: E501
        return queries

    def build_common_feature(
        self, feature_value, feature_name, setting, functions, queries
    ):  # noqa: E501
        setting_type = setting["setting_type"]
        score = setting["score"]
        if feature_value and setting_type:
            functions = self.build_categorical_function_score(
                functions, feature_value, feature_name, score
            )
        elif feature_value and not setting_type:
            queries = self.build_filter(queries, feature_value, feature_name)
        return functions, queries

    def build_origin(self, origin, setting_type, functions, queries, score=10):
        if origin and setting_type:
            functions.append(
                {
                    "filter": Q("terms", origin=list(map(lambda x: int(x), origin))),
                    "weight": score,
                }
            )
        elif origin and not setting_type:
            queries = self.build_filter(queries, origin, "origin")
        return functions, queries

    def parse_range_query(self, functions: List, input: RangeInput, settings):
        (min_tall, max_tall, min_age, max_age) = safe_itemgetter(
            "min_tall",
            "max_tall",
            "min_age",
            "max_age",
        )(input)
        if min_tall and max_tall and min_tall <= max_tall:
            functions = self.build_range_query(
                functions, "size", min_tall, max_tall, settings["size_score"]
            )
        if min_age and max_age and min_age <= max_age:
            functions = self.build_range_query(
                functions, "age", min_age, max_age, settings["age_score"]
            )
        return functions

    def parse_common_query(
        self, queries: List, functions: List, input: CommonInput, settings
    ):
        (
            eat_halal,
            is_pratiquant,
            salat_pratique,
            veil,
            want_children,
            has_children,
            family_situation,
            study_level,
            figure,
            fume,
        ) = safe_itemgetter(
            "eat_halal",
            "is_pratiquant",
            "salat_pratique",
            "veil",
            "want_children",
            "has_children",
            "family_situation",
            "study_level",
            "figure",
            "fume",
        )(
            input
        )
        # build eat halal
        functions, queries = self.build_common_feature(
            eat_halal,
            "eat_halal",
            settings.get("eat_halal"),
            functions,
            queries,
        )
        # build religious
        functions, queries = self.build_common_feature(
            is_pratiquant,
            "is_pratiquant",
            settings.get("religious"),
            functions,
            queries,
        )
        # build salat pratique
        functions, queries = self.build_common_feature(
            salat_pratique,
            "salat_pratique",
            settings.get("salat_pratique"),
            functions,
            queries,
        )

        # build veil
        if isinstance(veil, list):
            if veil:
                target_veil = veil
                if 1 in veil:
                    target_veil = 2
                elif 2 in veil:
                    target_veil = 1
                functions, queries = self.build_common_feature(
                    target_veil,
                    "veil",
                    settings.get("veil"),
                    functions,
                    queries,
                )
        elif isinstance(veil, int):
            if veil:
                target_veil = veil
                if 1 == veil:
                    target_veil = 2
                elif 2 == veil:
                    target_veil = 1
                functions, queries = self.build_common_feature(
                    target_veil,
                    "veil",
                    settings.get("veil"),
                    functions,
                    queries,
                )
        # build want children
        functions, queries = self.build_common_feature(
            want_children,
            "want_children",
            settings.get("want_children"),
            functions,
            queries,
        )
        # build has children
        functions, queries = self.build_common_feature(
            has_children,
            "has_children",
            settings.get("has_children"),
            functions,
            queries,
        )
        # build family situation
        functions, queries = self.build_common_feature(
            family_situation,
            "family_situation",
            settings.get("family_situation"),
            functions,
            queries,
        )
        # build degree
        functions, queries = self.build_common_feature(
            study_level,
            "study_level",
            settings.get("degree"),
            functions,
            queries,
        )
        # build body
        functions, queries = self.build_common_feature(
            figure,
            "figure",
            settings.get("body"),
            functions,
            queries,
        )
        # build smoke
        functions, queries = self.build_common_feature(
            fume,
            "fume",
            settings.get("fume"),
            functions,
            queries,
        )

        return functions, queries

    def parse_extra_query(self, functions, input: LocationInput, settings):
        now = round(datetime.now().timestamp())

        (latitude, longitude,) = safe_itemgetter(
            "latitude",
            "longitude",
        )(input)
        functions = self.build_push_forward_query(
            functions, now, settings["push_forward_score"]
        )
        functions = self.build_distance_query(
            functions, latitude, longitude, settings["distance_score"]
        )
        functions = self.build_last_connection_query(
            functions, now, settings["last_connection_score"]
        )
        functions = self.build_seniority_query(
            functions, now, settings["seniority_score"]
        )
        functions = self.build_photo_query(functions, settings["photos_score"])
        functions = self.build_profile_filling_rate_query(
            functions, settings["profile_filling_score"]
        )
        return functions
